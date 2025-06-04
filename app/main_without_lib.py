import sys
import os
import requests
from requests.auth import HTTPBasicAuth
from dataclasses import dataclass
from typing import Optional
import json
from datetime import datetime, timezone

base_url = "https://www.kaggle.com/api/v1"
owner_slug = "datasnaek"
dataset_slug = "youtube-new"
dataset_version = "115"
csv_file_name = "GBvideos.csv"
json_file_name = "GB_category_id.json"

class DatasetVersionDetails:
    def __init__(self, version_json: dict):
        self.versionNumber: int = version_json["versionNumber"]
        self.hasVersionNotes: bool = version_json["hasVersionNotes"]
        self.versionNotesNullable: Optional[str] = version_json.get("versionNotes")


class DatasetDetails:
    def __init__(self, api_answer_json: dict):
        self.ownerRef: str = api_answer_json["ownerRef"]
        self.currentVersionNumber: int = api_answer_json["currentVersionNumber"]
        self.hasCurrentVersionNumber: bool = api_answer_json["hasCurrentVersionNumber"]
        self.ref: str = api_answer_json["ref"]
        self.versions = [
            DatasetVersionDetails(version) for version in api_answer_json.get('versions', [])
        ]

    def __repr__(self):
        return f"DatasetDetails(ownerRef={self.ownerRef}, currentVersionNumber={self.currentVersionNumber}, ref={self.ref})"

@dataclass
class KaggleCredentials:
    username: str
    key: str


with open('kaggle.json', 'r') as file:
    json_config = file.read()



credentials_data_from_auth_config_file = json.loads(json_config)

kaggle_credentials = KaggleCredentials(
    username=credentials_data_from_auth_config_file['username'],
    key=credentials_data_from_auth_config_file['key']
)
basic = HTTPBasicAuth(kaggle_credentials.username, kaggle_credentials.key)


def get_dataset_details(owner_slug: str, dataset_slug: str) -> DatasetDetails:
    url = f"{base_url}/datasets/view/{owner_slug}/{dataset_slug}"
    response = requests.get(url, auth=basic)
    
    if response.status_code == 200:
        response_data_dict = response.json()
        return DatasetDetails(response_data_dict)
    else:
        raise Exception(f"Failed to fetch dataset details: {response.status_code} - {response.text}")


def get_datasets_by_owner(owner_slug: str) -> list[DatasetDetails]:
    url = f"{base_url}/datasets/list?user={owner_slug}"
    
    response = requests.get(url, auth=basic)
    
    if response.status_code == 200:
        response_data_list = response.json()
        return [DatasetDetails(dataset) for dataset in response_data_list]
    else:
        raise Exception(f"Failed to fetch datasets by owner: {response.status_code} - {response.text}")


def check_if_overwrite_is_needed(archive_path: str, last_modified: datetime, expected_bytes_size: int) -> bool:
    
    os.makedirs(os.path.dirname(archive_path), exist_ok=True)

    if not os.path.exists(archive_path):
        return True
    
    file_last_modified = datetime.fromtimestamp(os.path.getmtime(archive_path), tz=timezone.utc)
    if file_last_modified < last_modified:
        return True
    
    if os.path.getsize(archive_path) != expected_bytes_size:
        return True
    
    return False



# import time
# import sys
# start_time = time.time()
# response = requests.get(, stream=True)
# print("Last-Modified:", response.headers.get("Last-Modified"))
# print("Content-Length:", response.headers.get("Content-Length"))
# archive_path = os.path.join("datasets", owner_slug, dataset_slug, "versions", str(dataset_version), json_file_name)




# if check_if_overwrite_is_needed(archive_path, remote_date, file_size_bytes):
#     print(f"Downloading {json_file_name}...")
#     downloaded = 0
#     with open(archive_path, "wb") as f:
#         for chunk in response.iter_content(chunk_size=8192):
            
#             f.write(chunk)
#             downloaded += len(chunk)
#             percent = downloaded * 100 / file_size_bytes if file_size_bytes else 0
#             sys.stdout.write(f"\rProgress: {percent:.2f}% ({downloaded}/{file_size_bytes} bytes)")
#             sys.stdout.flush()
# else:
#     print(f"{json_file_name} is already up to date, skipping download.")

# response.close()


# # Download CSV file
# response2 = requests.get(
#     f"{base_url}/datasets/download/{owner_slug}/{dataset_slug}/{csv_file_name}?datasetVersionNumber={dataset_version}",
#     stream=True
# )
# print("Last-Modified (CSV):", response2.headers.get("Last-Modified"))
# print("Content-Length (CSV):", response2.headers.get("Content-Length"))

# archive_path_csv = os.path.join("datasets", owner_slug, dataset_slug, "versions", str(dataset_version), csv_file_name)
# remote_date_csv = datetime.strptime(response2.headers["Last-Modified"], "%a, %d %b %Y %H:%M:%S %Z").replace(
#     tzinfo=timezone.utc
# )
# file_size_bytes_csv = int(response2.headers.get("Content-Length", 0))

# if not file_size_bytes_csv:
#     raise ValueError("Content-Length header is missing or zero for CSV file")

# if check_if_overwrite_is_needed(archive_path_csv, remote_date_csv, file_size_bytes_csv):
#     print(f"Downloading {csv_file_name}...")
#     downloaded = 0
#     with open(archive_path_csv, "wb") as f:
#         for chunk in response2.iter_content(chunk_size=8192):
#             f.write(chunk)
#             downloaded += len(chunk)
#             percent = downloaded * 100 / file_size_bytes_csv if file_size_bytes_csv else 0
#             sys.stdout.write(f"\rProgress: {percent:.2f}% ({downloaded}/{file_size_bytes_csv} bytes)")
#             sys.stdout.flush()
#     print()
# else:
#     print(f"{csv_file_name} is already up to date, skipping download.")
# response2.close()

# end_time = time.time()
# print(f"Time taken to download: {end_time - start_time:.2f} seconds")


def get_file_from_cache_or_download_it(
    owner_slug: str,
    dataset_slug: str,
    file_name: str,
    dataset_version: int,
) -> str:
    archive_path = os.path.join("datasets", owner_slug, dataset_slug, "versions", dataset_version, file_name)
    url = f"{base_url}/datasets/download/{owner_slug}/{dataset_slug}/{file_name}?datasetVersionNumber={dataset_version}"
    with requests.get(url, stream=True) as response:
        response.raise_for_status()

        remote_date = datetime.strptime(response.headers["Last-Modified"], "%a, %d %b %Y %H:%M:%S %Z").replace(
            tzinfo=timezone.utc
        )
        file_size_bytes = int(response.headers.get("Content-Length", 0))
        if not file_size_bytes:
            raise ValueError("Content-Length header is missing or zero")



        should_overwrite = check_if_overwrite_is_needed(
            archive_path,
            remote_date,
            file_size_bytes
        )

        if not should_overwrite:
            print(f"{file_name} is already up to date, skipping download.")
            return archive_path
        
        print(f"Downloading {file_name}...")
        downloaded = 0
        with open(archive_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                percent = downloaded * 100 / file_size_bytes if file_size_bytes else 0
                sys.stdout.write(f"\rProgress: {percent:.2f}% ({downloaded}/{file_size_bytes} bytes)")
                sys.stdout.flush()
    
        return archive_path


get_file_from_cache_or_download_it(owner_slug, dataset_slug, csv_file_name, dataset_version)
get_file_from_cache_or_download_it(owner_slug, dataset_slug, json_file_name, dataset_version)