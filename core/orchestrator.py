from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any

from crewai import Crew, Task, Process, LLM
from agents.manager import create_manager
from agents.developer import create_developer
from agents.tester import create_tester
from metrics.logger import logger
from integrations.aws_client import aws_client
from integrations.validator import validate_response, calculate_confidence

class Orchestrator:
    def __init__(self):
        logger.info("🚀 Initializing Orchestrator")
        
        # Validate OpenAI API key
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise RuntimeError("❌ OPENAI_API_KEY not in environment")
        
        # Initialize LLM with GPT-4 (Giga requirement)
        self.llm = LLM(
            model="gpt-4-turbo",
            api_key=openai_key,
            temperature=0.2
        )
        
        # Initialize agents
        self.manager = create_manager(self.llm)
        self.developer = create_developer(self.llm)
        self.tester = create_tester(self.llm)
        
        logger.info("✅ Orchestrator initialized successfully")
    
    async def run(
        self, 
        task: str, 
        context: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main orchestration function following Giga JD:
        - Strong Python backend ✓
        - AWS S3 logging ✓
        - CloudWatch metrics ✓
        - Hallucination prevention ✓
        - Confidence scoring ✓
        """
        
        start_time = time.time()
        request_id = request_id or f"req_{datetime.utcnow().timestamp()}"
        
        logger.info(f"[{request_id}] 📋 Task received: {task[:100]}")
        
        try:
            # Prepare task with context
            full_task = task
            if context:
                full_task = f"{task}\n\nContext:\n{context}"
            
            # Execute crew synchronously in thread
            def _run_crew():
                # Create sequential tasks
                manager_task = Task(
                    description=full_task,
                    agent=self.manager,
                    expected_output="Clear step-by-step implementation plan with analysis"
                )
                
                developer_task = Task(
                    description="Implement the manager's plan. Write production-ready code.",
                    agent=self.developer,
                    expected_output="Clean, optimized, well-commented code following best practices"
                )
                
                tester_task = Task(
                    description="Test the code thoroughly, find bugs, generate test cases",
                    agent=self.tester,
                    expected_output="Verified code with comprehensive test cases and bug report"
                )
                
                # Create crew with sequential process
                crew = Crew(
                    agents=[self.manager, self.developer, self.tester],
                    tasks=[manager_task, developer_task, tester_task],
                    process=Process.sequential,
                    verbose=True
                )
                
                logger.info(f"[{request_id}] 🔄 Crew execution started")
                return crew.kickoff()
            
            # Run in thread (non-blocking)
            result = await asyncio.to_thread(_run_crew)
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Validate response for hallucinations
            validation = validate_response(result)
            confidence = calculate_confidence(result, validation)
            
            # Alert if low confidence
            if confidence < 0.75:
                logger.warning(f"[{request_id}] ⚠️ Low confidence: {confidence:.2f}")
                if aws_client:
                    await aws_client.put_metric(
                        "LowConfidenceAlerts",
                        1,
                        request_id=request_id
                    )
            
            # Upload to S3 for audit
            execution_data = {
                "request_id": request_id,
                "task": task,
                "context": context,
                "result": str(result)[:5000],  # Limit size
                "confidence": confidence,
                "validation": validation,
                "execution_time_ms": execution_time_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if aws_client:
                await aws_client.upload_execution_log(request_id, execution_data)
                await aws_client.put_metric(
                    "ExecutionLatency",
                    execution_time_ms,
                    unit="Milliseconds",
                    request_id=request_id
                )
            
            logger.info(f"[{request_id}] ✅ Task completed in {execution_time_ms:.0f}ms")
            
            return {
                "request_id": request_id,
                "result": result,
                "status": "validated" if validation["status"] == "passed" else "flagged",
                "confidence_score": confidence,
                "execution_time_ms": execution_time_ms,
                "validation_issues": validation.get("issues", [])
            }
            
        except Exception as e:
            logger.error(f"[{request_id}] ❌ Orchestration failed: {str(e)}", exc_info=True)
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Log failure to S3
            if aws_client:
                await aws_client.upload_execution_log(
                    request_id,
                    {
                        "request_id": request_id,
                        "task": task,
                        "error": str(e),
                        "execution_time_ms": execution_time_ms,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            
            raise

# Singleton instance
orchestrator = Orchestrator()
