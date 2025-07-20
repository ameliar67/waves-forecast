import os
from urllib.parse import urlparse


import boto3
from mypy_boto3_s3.service_resource import Bucket


class Config:
    def __init__(self, is_development: bool, schedule: str, s3_bucket: Bucket):
        self.is_development = is_development
        self.schedule = schedule
        self.s3_bucket = s3_bucket

    @staticmethod
    def from_environment():
        is_development = os.environ.get("IS_DEVELOPMENT") in ("1", "True", "true")
        schedule = os.environ.get("SCHEDULE")
        s3_service_url = os.environ.get("S3_SERVICE_URL")
        s3_bucket_name = os.environ.get("S3_BUCKET_NAME")
        s3_access_key_id = os.environ.get("S3_ACCESS_KEY_ID")
        s3_secret_key = os.environ.get("S3_SECRET_KEY")

        Config.validate(
            schedule, s3_service_url, s3_bucket_name, s3_access_key_id, s3_secret_key
        )
        s3_bucket = boto3.resource(
            "s3",
            endpoint_url=s3_service_url,
            aws_access_key_id=s3_access_key_id,
            aws_secret_access_key=s3_secret_key,
        ).Bucket(s3_bucket_name)

        return Config(is_development, schedule, s3_bucket)

    @staticmethod
    def validate(
        schedule: str | None,
        s3_service_url: str | None,
        s3_bucket_name: str | None,
        s3_access_key_id: str | None,
        s3_secret_key: str | None,
    ):
        if not schedule:
            raise ValueError("schedule configuration is required")

        if not s3_service_url:
            raise ValueError("s3_service_url configuration is required")

        if not urlparse(s3_service_url).netloc:
            raise ValueError("s3_service_url must be an absolute URL")

        if not s3_bucket_name:
            raise ValueError("s3_bucket_name configuration is required")

        if not s3_access_key_id:
            raise ValueError("s3_access_key_id configuration is required")

        if not s3_secret_key:
            raise ValueError("s3_secret_key configuration is required")
