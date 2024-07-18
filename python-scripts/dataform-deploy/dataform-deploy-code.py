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
            print("Pre-release Workspace deleted successfully")
        except requests.exceptions.RequestException as e:
            print("Skipping deleting pre-release workspace:", e)

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
    def __init__(self, project_id, source_region, repository, access_token, directory_name, commit_message , workspace):
            self.project_id = project_id
            self.source_region = source_region
            self.repository = repository
            self.access_token = access_token
            self.directory_name = directory_name
            self.commit_message = commit_message
            self.workspace = workspace

    def fetch_files(self):
        list_directory_url = f"https://dataform.googleapis.com/v1beta1/projects/{self.project_id}/locations/{self.source_region}/repositories/{self.repository}/workspaces/pre-release:searchFiles"

        response = requests.get(list_directory_url, headers={"Authorization": f"Bearer {self.access_token}"})
        files_and_directories_to_delete = []

        if response.status_code == 200:
            data = response.json()
            directory_entries = data.get("searchResults", [])
            for entry in directory_entries:
                if "file" in entry:
                    file_name = entry["file"]["path"]
                    if "node_modules" in file_name:
                        continue
                    files_and_directories_to_delete.append(file_name)
                elif "directory" in entry:
                    directory_path = entry["directory"]["path"]
                    if "node_modules" in directory_path:
                        continue
                    files_and_directories_to_delete.append(directory_path + '/')  # Append '/' to mark as directory
        else:
            print(f"Failed to retrieve directory contents. Status code: {response.status_code}")

        return files_and_directories_to_delete

    def delete_files(self, files_and_directories_to_delete):
        client = dataform_v1beta1.DataformClient(client_options={"api_endpoint": f"dataform.googleapis.com:443"})

        # Sort files and directories to delete so that directories come after their contents
        files_and_directories_to_delete.sort(reverse=True)
        print("Deleting Files from pre-release")

        for file_or_directory_to_delete in files_and_directories_to_delete:
            # Initialize request argument(s)
            request = None
            if file_or_directory_to_delete.endswith('/'):
                request = dataform_v1beta1.RemoveDirectoryRequest(
                    workspace=f"projects/{self.project_id}/locations/{self.source_region}/repositories/{self.repository}/workspaces/pre-release",
                    path=file_or_directory_to_delete[:-1],  # Remove trailing '/'
                )
            else:
                request = dataform_v1beta1.RemoveFileRequest(
                    workspace=f"projects/{self.project_id}/locations/{self.source_region}/repositories/{self.repository}/workspaces/pre-release",
                    path=file_or_directory_to_delete,
                )

            # Make the request
            try:
                if isinstance(request, dataform_v1beta1.RemoveFileRequest):
                    response = client.remove_file(request=request)
                elif isinstance(request, dataform_v1beta1.RemoveDirectoryRequest):
                    response = client.remove_directory(request=request)
                print(f"Deleted file or directory: {file_or_directory_to_delete}")
            except Exception as e:
                print(f"Failed to delete file or directory {file_or_directory_to_delete}: {e}")

    def upload_file(self, file_path, relative_path, locations, repository, workspace):
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
        except PermissionError:
            print(f"Permission denied: {file_path}")
            return

        encoded_content = base64.b64encode(content).decode('utf-8')

        file_data = {
            "path": relative_path,
            "contents": encoded_content
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        file_url = f"https://dataform.googleapis.com/v1beta1/projects/{self.project_id}/locations/{locations}/repositories/{repository}/workspaces/{workspace}:writeFile"
        response = requests.post(file_url, headers=headers, data=json.dumps(file_data))

        if response.status_code == 200:
            print(f"File '{relative_path}' written successfully")
        else:
            print(f"Failed to write file '{relative_path}'")
            print(response.text)

    def upload_directory(self, directory, locations, repository, workspace, parent_dir=''):
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                relative_path = os.path.relpath(file_path, directory)
                if parent_dir:
                    relative_path = os.path.join(parent_dir, relative_path).replace("\\","/")  # Replace backslashes with forward slashes
                else:
                    relative_path = relative_path.replace("\\", "/")  # Replace backslashes with forward slashes
                self.upload_file(file_path, relative_path, locations, repository, workspace)

    def commit_changes(self, commit_message, source_region, repository, workspace , access_token):
        commit_data = {
            "author": {
                "name": "Your Name",
                "emailAddress": "your@email.com"
            },
            "commitMessage": commit_message
        }
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        commit_url = f"https://dataform.googleapis.com/v1beta1/projects/{self.project_id}/locations/{source_region}/repositories/{repository}/workspaces/{workspace}:commit"
        response = requests.post(commit_url, headers=headers, json=commit_data)

        if response.status_code == 200:
            print("Changes committed successfully")
            self.push_changes(source_region, repository, workspace, access_token)  # Call push after successful commit
        else:
            print("Failed to commit changes")
            print(response.text)

    def push_changes(self, source_region, repository, workspace, access_token, remote_branch="main"):
        push_data = {
            "remoteBranch": remote_branch
        }
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        push_url = f"https://dataform.googleapis.com/v1beta1/projects/{self.project_id}/locations/{source_region}/repositories/{repository}/workspaces/{workspace}:push"
        response = requests.post(push_url, headers=headers, json=push_data)

        if response.status_code == 200:
            print("Code changes pushed successfully")
        else:
            print("Failed to push code changes")
            print(response.text)


def main():
    if len(sys.argv) != 7:
        print(
            "Usage: python script.py <json_file_path> <project_id> <source_region> <repository> <directory_name> <commit_message>")
        return

    json_file_path = sys.argv[1]
    project_id = sys.argv[2]
    source_region = sys.argv[3]
    repository = sys.argv[4]
    directory_name = sys.argv[5]
    commit_message = sys.argv[6]
    workspace = "pre-release"

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_file_path
    gcp_manager = GCPManager(json_file_path)
    workspace_name = f"projects/{project_id}/locations/{source_region}/repositories/{repository}/workspaces/{workspace}"
    gcp_manager.delete_dataform_workspace(workspace_name)
    dataform_client = DataformClient(project_id, source_region, repository)
    dataform_client.create_workspace(workspace)

    access_token = gcp_manager.access_token
    file_handler = FileHandler(project_id, source_region, repository, access_token, directory_name, commit_message,
                               workspace)
    files_to_delete = file_handler.fetch_files()
    file_handler.delete_files(files_to_delete)
    print("###########Uploading Content from local to Dataform Workspace############")
    file_handler.upload_directory(directory_name, source_region, repository, workspace)
    file_handler.commit_changes(commit_message, source_region, repository, workspace, access_token)


if __name__ == "__main__":
    main()
