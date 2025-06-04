import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

import requests
import structlog
from requests.auth import HTTPBasicAuth

from app.config import API_BASE_URL

structlog.configure(processors=[structlog.processors.JSONRenderer()])

log = structlog.get_logger()


owner_slug = "datasnaek"
dataset_slug = "youtube-new"
dataset_version = int("115")
csv_file_name = "GBvideos.csv"
json_file_name = "GB_category_id.json"


class DatasetVersionDetails:
    def __init__(self, version_json: dict[str, Any]):
        self.versionNumber: int = version_json["versionNumber"]
        self.hasVersionNotes: bool = version_json["hasVersionNotes"]
        self.versionNotesNullable: Optional[str] = version_json.get("versionNotes")


class DatasetDetails:
    """
    Full json params are not recreated here because we don't need them in that example.
    """

    def __init__(self, api_answer_json: dict[str, Any]):
        self.ownerRef: str = api_answer_json["ownerRef"]
        self.currentVersionNumber: int = api_answer_json["currentVersionNumber"]
        self.hasCurrentVersionNumber: bool = api_answer_json["hasCurrentVersionNumber"]
        self.ref: str = api_answer_json["ref"]
        self.versions = [
            DatasetVersionDetails(version)
            for version in api_answer_json.get("versions", [])
        ]

    def __repr__(self) -> str:
        return f"DatasetDetails(ownerRef={self.ownerRef}, currentVersionNumber={self.currentVersionNumber}, ref={self.ref})"


@dataclass
class KaggleCredentials:
    username: str
    key: str


def read_auth_config_file(file_path: str) -> KaggleCredentials:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Authentication config file not found: {file_path}")

    with open(file_path, "r") as file:
        try:
            config_data = json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON format in the authentication config file: {e}"
            )

    if "username" not in config_data or "key" not in config_data:
        raise ValueError(
            "Authentication config file must contain 'username' and 'key' fields"
        )

    log.info(
        "Using Kaggle credentials from config file", username=config_data["username"]
    )

    return KaggleCredentials(username=config_data["username"], key=config_data["key"])


def get_dataset_details(
    base_api_url: str, owner_slug: str, dataset_slug: str, auth: HTTPBasicAuth
) -> DatasetDetails:
    url = f"{base_api_url}/datasets/view/{owner_slug}/{dataset_slug}"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    response_data_dict = response.json()
    return DatasetDetails(response_data_dict)


def get_datasets_by_owner(
    base_api_url: str, owner_slug: str, auth: HTTPBasicAuth
) -> list[DatasetDetails]:
    url = f"{base_api_url}/datasets/list?user={owner_slug}"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    response_data_list = response.json()
    return [DatasetDetails(dataset) for dataset in response_data_list]


def check_if_overwrite_is_needed(
    archive_path: str, last_modified: datetime, expected_bytes_size: int
) -> bool:

    os.makedirs(os.path.dirname(archive_path), exist_ok=True)

    if not os.path.exists(archive_path):
        return True

    file_last_modified = datetime.fromtimestamp(
        os.path.getmtime(archive_path), tz=timezone.utc
    )
    if file_last_modified < last_modified:
        return True

    if os.path.getsize(archive_path) != expected_bytes_size:
        return True

    return False


def get_file_from_cache_or_download_it(
    owner_slug: str,
    dataset_slug: str,
    file_name: str,
    dataset_version: int,
    auth: HTTPBasicAuth,
) -> str:
    archive_path = os.path.join(
        "datasets",
        owner_slug,
        dataset_slug,
        "versions",
        str(dataset_version),
        file_name,
    )
    url = f"{API_BASE_URL}/datasets/download/{owner_slug}/{dataset_slug}/{file_name}?datasetVersionNumber={dataset_version}"
    with requests.get(url, stream=True, auth=auth) as response:
        response.raise_for_status()

        remote_date = datetime.strptime(
            response.headers["Last-Modified"], "%a, %d %b %Y %H:%M:%S %Z"
        ).replace(tzinfo=timezone.utc)
        file_size_bytes = int(response.headers.get("Content-Length", 0))
        if not file_size_bytes:
            raise ValueError("Content-Length header is missing or zero")

        should_overwrite: bool = check_if_overwrite_is_needed(
            archive_path, remote_date, file_size_bytes
        )

        if not should_overwrite:
            log.warning(
                "File already exists and is up to date",
                file_name=file_name,
                archive_path=archive_path,
            )
            return archive_path

        log.info(
            "Downloading file", file_name=file_name, archive_path=archive_path, url=url
        )
        downloaded = 0
        with open(archive_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                percent = downloaded * 100 / file_size_bytes if file_size_bytes else 0
                log.info(
                    "Download progress",
                    file_name=file_name,
                    downloaded=downloaded,
                    total_size=file_size_bytes,
                    percent=percent,
                )
        return archive_path


if __name__ == "__main__":
    kaggle_credentials = read_auth_config_file("kaggle.json")
    basic = HTTPBasicAuth(kaggle_credentials.username, kaggle_credentials.key)

    dataset_list = get_datasets_by_owner(API_BASE_URL, owner_slug, basic)
    datasets_refs = [dataset.ref for dataset in dataset_list]
    if f"{owner_slug}/{dataset_slug}" not in datasets_refs:
        raise ValueError(
            f"Dataset {owner_slug}/{dataset_slug} not found in the list of datasets for owner {owner_slug}"
        )

    dataset_details = get_dataset_details(API_BASE_URL, owner_slug, dataset_slug, basic)

    for versions in dataset_details.versions:
        if versions.versionNumber > dataset_version:
            log.warning(
                "Newer dataset version available",
                dataset_slug=dataset_slug,
                version_number=versions.versionNumber,
                version_notes=versions.versionNotesNullable,
            )

    csv_file_path = get_file_from_cache_or_download_it(
        owner_slug=owner_slug,
        dataset_slug=dataset_slug,
        file_name=csv_file_name,
        dataset_version=dataset_version,
        auth=basic,
    )
    json_file_path = get_file_from_cache_or_download_it(
        owner_slug=owner_slug,
        dataset_slug=dataset_slug,
        file_name=json_file_name,
        dataset_version=dataset_version,
        auth=basic,
    )
