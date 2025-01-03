import datetime
from azure.core.exceptions import AzureError
from azure.storage.blob import ContainerClient
from typing import Union


class Cache:
    def __init__(self, container_client: ContainerClient) -> None:
        self.container_client = container_client

    def get_item(self, key: str, max_age_seconds: int) -> Union[bytes, None]:
        try:
            blob_client = self.container_client.get_blob_client(key)
            valid_from = datetime.datetime.now() - datetime.timedelta(
                seconds=max_age_seconds
            )
            blob_response = blob_client.download_blob(if_modified_since=valid_from)
            return blob_response.readall()
        except AzureError:
            return None

    def set_item(self, key: str, data: bytes) -> None:
        blob_client = self.container_client.get_blob_client(key)
        blob_client.upload_blob(data)
