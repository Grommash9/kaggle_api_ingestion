import vcr
from app.config import VCR_RECORD_MODE


vcr_c = vcr.VCR(
    cassette_library_dir="tests/fixtures/cassettes",
    record_mode=VCR_RECORD_MODE,
    match_on=["host", "path", "method", "query", "body"],
    filter_headers=["Authorization", "Cookie"],
    ignore_hosts=["127.0.0.1", "localhost"],
)