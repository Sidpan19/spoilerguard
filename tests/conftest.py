import pytest

from src.models import Classification, VideoInput


@pytest.fixture
def video():
    def make(title="", description="", date="2026-10-16", transcript=""):
        return VideoInput(title=title, description=description, post_date=date, transcript_excerpt=transcript)
    return make
