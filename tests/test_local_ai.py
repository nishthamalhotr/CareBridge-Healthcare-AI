import json
from io import BytesIO
from urllib.error import HTTPError, URLError
from unittest.mock import patch

import pytest

from carebridge.local_ai import (
    DEFAULT_MODEL,
    OLLAMA_GENERATE_URL,
    LocalAIError,
    organize_notes_locally,
)


def test_organizer_posts_to_loopback_and_returns_local_model_draft():
    response = BytesIO(json.dumps({"response": "Details explicitly mentioned\n- Headache"}).encode())
    with patch("carebridge.local_ai.urlopen", return_value=response) as mocked_urlopen:
        draft = organize_notes_locally(
            "Symptoms: headache",
            model=DEFAULT_MODEL,
        )

    request = mocked_urlopen.call_args.args[0]
    payload = json.loads(request.data)
    assert request.full_url == OLLAMA_GENERATE_URL
    assert payload["model"] == DEFAULT_MODEL
    assert payload["stream"] is False
    assert "Symptoms: headache" in payload["prompt"]
    assert "Do not diagnose" in payload["prompt"]
    assert draft == "Details explicitly mentioned\n- Headache"


def test_empty_notes_fail_before_request():
    with patch("carebridge.local_ai.urlopen") as mocked_urlopen:
        with pytest.raises(LocalAIError, match="Add some notes"):
            organize_notes_locally("   ")
    mocked_urlopen.assert_not_called()


def test_model_name_must_not_contain_whitespace():
    with pytest.raises(LocalAIError, match="valid Ollama model"):
        organize_notes_locally("Notes", model="bad model")


def test_missing_model_reports_how_to_install_it():
    error = HTTPError(OLLAMA_GENERATE_URL, 404, "not found", {}, None)
    with patch("carebridge.local_ai.urlopen", side_effect=error):
        with pytest.raises(LocalAIError, match="ollama pull llama3.2:3b"):
            organize_notes_locally("Notes")


def test_unavailable_local_service_has_actionable_error():
    error = URLError(ConnectionRefusedError("connection refused"))
    with patch("carebridge.local_ai.urlopen", side_effect=error):
        with pytest.raises(LocalAIError, match="Start Ollama"):
            organize_notes_locally("Notes")


def test_invalid_local_service_response_is_reported():
    with patch("carebridge.local_ai.urlopen", return_value=BytesIO(b"not-json")):
        with pytest.raises(LocalAIError, match="invalid response"):
            organize_notes_locally("Notes")


def test_empty_model_response_is_reported():
    response = BytesIO(json.dumps({"response": "  "}).encode())
    with patch("carebridge.local_ai.urlopen", return_value=response):
        with pytest.raises(LocalAIError, match="empty draft"):
            organize_notes_locally("Notes")
