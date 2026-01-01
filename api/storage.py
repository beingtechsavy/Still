import os
from azure.storage.blob import BlobServiceClient
from datetime import datetime, timedelta

# Initialize only if connection string is present
CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

class StorageService:
    def __init__(self):
        if not CONNECTION_STRING:
            print("WARNING: Storage connection string missing. Using mock storage.")
            self.service_client = None
            self.container_name = "still-temp-audio"
        else:
            self.service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
            self.container_name = "still-temp-audio"
            self._ensure_container()

    def _ensure_container(self):
        try:
            container_client = self.service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container()
        except Exception as e:
            print(f"Container setup error: {e}")

    async def upload_audio(self, file_data: bytes, filename: str) -> str:
        """Uploads audio and returns a temporary SAS URL or Path."""
        if not self.service_client:
            # Mock behavior meant for local usage if keys aren't set
            mock_path = f"tmp/{filename}"
            os.makedirs("tmp", exist_ok=True)
            with open(mock_path, "wb") as f:
                f.write(file_data)
            return mock_path

        blob_client = self.service_client.get_blob_client(container=self.container_name, blob=filename)
        blob_client.upload_blob(file_data, overwrite=True)
        return blob_client.url

    async def delete_audio(self, filename: str):
        """Immediately delete the audio blob."""
        if not self.service_client:
            mock_path = f"tmp/{filename}"
            if os.path.exists(mock_path):
                os.remove(mock_path)
            return

        try:
            blob_client = self.service_client.get_blob_client(container=self.container_name, blob=filename)
            blob_client.delete_blob()
        except Exception as e:
            print(f"Deletion error for {filename}: {e}")
