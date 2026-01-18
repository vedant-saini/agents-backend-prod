"""
AWS Integration (Giga JD Requirement)
S3: Store execution logs
CloudWatch: Track metrics
Secrets Manager: Secure credential storage
"""

import boto3
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class AWSClient:
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.bucket = os.getenv("AWS_S3_BUCKET", "giga-ai-backend")
        
        try:
            # Initialize AWS clients
            self.s3 = boto3.client(
                "s3",
                region_name=self.region,
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )
            
            self.cloudwatch = boto3.client(
                "cloudwatch",
                region_name=self.region,
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )
            
            self.secrets = boto3.client(
                "secretsmanager",
                region_name=self.region,
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )
            
            logger.info("✅ AWS clients initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ AWS initialization failed: {e}. Continuing without AWS.")
            self.s3 = None
            self.cloudwatch = None
            self.secrets = None
    
    async def upload_execution_log(
        self, 
        request_id: str, 
        execution_data: Dict[str, Any]
    ) -> bool:
        """Upload execution log to S3"""
        if not self.s3:
            return False
        
        try:
            key = f"executions/{request_id}.json"
            self.s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=json.dumps(execution_data, indent=2),
                ContentType="application/json"
            )
            logger.info(f"📤 Uploaded execution log to S3: {key}")
            return True
        except Exception as e:
            logger.error(f"❌ S3 upload failed: {e}")
            return False
    
    async def put_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "Count",
        request_id: str = ""
    ) -> bool:
        """Put metric to CloudWatch"""
        if not self.cloudwatch:
            return False
        
        try:
            dimensions = []
            if request_id:
                dimensions.append({
                    "Name": "RequestID",
                    "Value": request_id[:20]
                })
            
            self.cloudwatch.put_metric_data(
                Namespace="GigaAIBackend",
                MetricData=[
                    {
                        "MetricName": metric_name,
                        "Value": value,
                        "Unit": unit,
                        "Timestamp": datetime.utcnow(),
                        "Dimensions": dimensions
                    }
                ]
            )
            logger.debug(f"📊 Metric {metric_name}={value} posted to CloudWatch")
            return True
        except Exception as e:
            logger.error(f"❌ CloudWatch metric failed: {e}")
            return False
    
    async def get_secret(self, secret_name: str) -> Optional[str]:
        """Retrieve secret from Secrets Manager"""
        if not self.secrets:
            return None
        
        try:
            response = self.secrets.get_secret_value(SecretId=secret_name)
            logger.info(f"🔐 Retrieved secret: {secret_name}")
            return response["SecretString"]
        except Exception as e:
            logger.error(f"❌ Failed to get secret: {e}")
            return None

# Singleton instance (None if AWS not available)
try:
    aws_client = AWSClient() if os.getenv("AWS_REGION") else None
except:
    aws_client = None
