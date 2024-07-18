import os
import time
import requests
import json
import base64
import shutil
from google.oauth2 import service_account
import google.auth
import google.auth.transport.requests
from google.cloud import dataform_v1beta1
import sys

class GCPManager:
    def __init__(self, json_file_path):
        self.credentials = service_account.Credentials.from_service_account_file(
            json_file_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        self.request = google.auth.transport.requests.Request()
        self.credentials.refresh(self.request)
        self.access_token = self.credentials.token

    def delete_dataform_workspace(self, workspace_name):
        api_url = f"https://dataform.googleapis.com/v1beta1/{workspace_name}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.delete(api_url, headers=headers)
            response.raise_for_status()
            print("main-clone Workspace deleted successfully")
        except requests.exceptions.RequestException as e:
            print("Skipping deleting main-clone workspace:", e)

class DataformClient:
    def __init__(self, project_id, source_region, repository):
        self.client = dataform_v1beta1.DataformClient(client_options={"api_endpoint": f"dataform.googleapis.com:443"})
        self.parent = f"projects/{project_id}/locations/{source_region}/repositories/{repository}"

    def create_workspace(self, workspace_id):
        request = dataform_v1beta1.CreateWorkspaceRequest(
            parent=self.parent,
            workspace_id=workspace_id,
        )
        response = self.client.create_workspace(request=request)
        print("Created workspace:", response)
        time.sleep(10)

class FileHandler:
    def __init__(self, project_id, source_region, repository, output_directory, access_token):
        self.project_id = project_id
        self.source_region = source_region
        self.repository = repository
        self.output_directory = output_directory
        self.access_token = access_token

    def fetch_files(self):
        list_directory_url = f"https://dataform.googleapis.com/v1beta1/projects/{self.project_id}/locations/{self.source_region}/repositories/{self.repository}/workspaces/main-clone:searchFiles"

        response = requests.get(list_directory_url, headers={"Authorization": f"Bearer {self.access_token}"})
        print(response)

        if response.status_code == 200:
            data = response.json()
            directory_entries = data.get("searchResults", [])
            print(directory_entries)
            for entry in directory_entries:
                if "file" in entry:
                    file_name = entry["file"]["path"]

                    if "node_modules" in file_name:
                        continue

                    self.read_and_save_file(file_name)
        else:
            print(f"Failed to retrieve directory contents. Status code: {response.status_code}")

    def read_and_save_file(self, file_name):
        read_file_url = f"https://dataform.googleapis.com/v1beta1/projects/{self.project_id}/locations/{self.source_region}/repositories/{self.repository}:readFile?path={file_name}"

        file_response = requests.get(read_file_url, headers={"Authorization": f"Bearer {self.access_token}"})
        if file_response.status_code == 200:
            file_contents = file_response.text
            data = json.loads(file_contents)
            encoded_content = data.get("contents", '')  # Fetch content directly
            directory_path = os.path.join(self.output_directory, os.path.dirname(file_name))
            os.makedirs(directory_path, exist_ok=True)
            file_path = os.path.join(self.output_directory, file_name)
            try:
                with open(file_path, "wb") as f:
                    f.write(base64.b64decode(encoded_content))
                print(f"File '{file_path}' created successfully.")
            except Exception as e:
                print(f"Failed to decode and write file '{file_path}': {str(e)}")
        else:
            print(f"Failed to retrieve file contents for {file_name}. Status code: {file_response.status_code}")

def main():
    if len(sys.argv) != 6:
        print("Usage: python script.py <json_file_path> <project_id> <source_region> <repository> <output_directory>")
        return

    json_file_path = sys.argv[1]
    project_id = sys.argv[2]
    source_region = sys.argv[3]
    repository = sys.argv[4]
    output_directory = sys.argv[5]

    if os.path.exists(output_directory):
        try:
            shutil.rmtree(output_directory)
            print(f"Deleted existing output directory: {output_directory}")
        except Exception as e:
            print(f"Failed to delete existing output directory: {output_directory}, Error: {str(e)}")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_file_path
    gcp_manager = GCPManager(json_file_path)
    workspace_name = f"projects/{project_id}/locations/{source_region}/repositories/{repository}/workspaces/main-clone"
    gcp_manager.delete_dataform_workspace(workspace_name)

    dataform_client = DataformClient(project_id, source_region, repository)
    dataform_client.create_workspace('main-clone')

    access_token = gcp_manager.access_token
    file_handler = FileHandler(project_id, source_region, repository, output_directory, access_token)
    print("###########Fetching Data from Source Repo############")
    file_handler.fetch_files()
    gcp_manager.delete_dataform_workspace(workspace_name)

if __name__ == "__main__":
    main()
