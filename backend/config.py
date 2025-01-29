import os
from urllib.parse import urlparse


class Config:
    def __init__(self):
        self.cache_blob_account_url = None
        self.is_development = False

    @staticmethod
    def from_environment():
        conf = Config()
        conf.cache_blob_account_url = os.environ.get("CACHE_BLOB_ACCOUNT_URL")
        conf.is_development = os.environ.get("IS_DEVELOPMENT") in ('1', 'True', 'true')

        conf.validate()
        return conf

    def validate(self):
        if not self.cache_blob_account_url:
            raise ValueError("cache_blob_account_url configuration is required")

        if not urlparse(self.cache_blob_account_url).netloc:
            raise ValueError("cache_blob_account_url must be an absolute URL")
