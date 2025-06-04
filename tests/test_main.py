from app.main_without_lib import get_dataset_details, get_datasets_by_owner
from tests.conftest import vcr_c
from requests.auth import HTTPBasicAuth
from app.config import API_BASE_URL
import pytest
from requests.exceptions import HTTPError
from app.main_without_lib import check_if_overwrite_is_needed
import os
import pytest
from pathlib import Path
from datetime import datetime, timezone, timedelta

CONTENT = b"hello world"


@vcr_c.use_cassette("get_existing_datasets_by_owner.yaml")
def test_get_existing_datasets_by_owner():
    owner_slug = "datasnaek"
    dataset_slug = "youtube-new"
    basic = HTTPBasicAuth("any", "any")
    # I have added auth to codebase but it's actually not used anyhow so I am assuming that is outdated
    dataset_list = get_datasets_by_owner(API_BASE_URL, owner_slug, basic)
    
    datasets_refs = [dataset.ref for dataset in dataset_list]
    assert f"{owner_slug}/{dataset_slug}" in datasets_refs, (
        f"Dataset {owner_slug}/{dataset_slug} not found in the list of datasets for owner {owner_slug}"
    )

@vcr_c.use_cassette("get_non_existing_dataset.yaml")
def test_get_non_existing_dataset():
    owner_slug = "datasnaek"
    dataset_slug = "non-existing-dataset"
    basic = HTTPBasicAuth("any", "any")
    with pytest.raises(HTTPError) as exc_info:
        get_dataset_details(API_BASE_URL, owner_slug, dataset_slug, basic)
    assert exc_info.value.response.status_code == 403


@vcr_c.use_cassette("get_existing_dataset_details.yaml")
def test_get_existing_dataset_details():
    owner_slug = "datasnaek"
    dataset_slug = "youtube-new"
    basic = HTTPBasicAuth("any", "any")
    dataset_details = get_dataset_details(API_BASE_URL, owner_slug, dataset_slug, basic)
    assert dataset_details.ownerRef == owner_slug
    assert dataset_details.ref == f"{owner_slug}/{dataset_slug}"




def write_test_file(path: Path, content: bytes, mtime: datetime):
    path.write_bytes(content)
    mod_time = mtime.timestamp()
    os.utime(path, times=(mod_time, mod_time))

# https://docs.pytest.org/en/6.2.x/tmpdir.html
def test_overwrite_needed_when_file_does_not_exist(tmp_path):
    archive_path = Path(tmp_path) / "archive" / "file.txt"
    result = check_if_overwrite_is_needed(str(archive_path), datetime.now(timezone.utc), 123)
    assert result is True


def test_overwrite_needed_when_file_is_older(tmp_path):
    archive_path = Path(tmp_path) / "archive" / "file.txt"
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    mtime = datetime.now(timezone.utc) - timedelta(days=1)
    write_test_file(archive_path, CONTENT, mtime)

    future_time = datetime.now(timezone.utc)
    result = check_if_overwrite_is_needed(str(archive_path), future_time, len(CONTENT))
    assert result is True


def test_overwrite_needed_when_file_size_differs(tmp_path):
    archive_path = Path(tmp_path) / "archive" / "file.txt"
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    mtime = datetime.now(timezone.utc)
    write_test_file(archive_path, CONTENT, mtime)
    result = check_if_overwrite_is_needed(str(archive_path), mtime, len(CONTENT) + 1)
    assert result is True


def test_no_overwrite_needed_when_file_is_recent_and_size_matches(tmp_path):
    archive_path = Path(tmp_path) / "archive" / "file.txt"
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    mtime = datetime.now(timezone.utc)
    write_test_file(archive_path, CONTENT, mtime)
    result = check_if_overwrite_is_needed(str(archive_path), mtime, len(CONTENT))
    assert result is False