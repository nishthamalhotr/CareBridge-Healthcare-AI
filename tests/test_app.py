from io import BytesIO
import json
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from streamlit.testing.v1 import AppTest

from carebridge.triage import UNSURE_OPTION, URGENT_TERMS


APP_FILE = Path(__file__).resolve().parents[1] / "app.py"


def test_fictional_demo_generates_and_clears_summary():
    app = AppTest.from_file(str(APP_FILE), default_timeout=10).run()
    assert not app.exception

    app.button(key="load_demo").click().run()
    assert not app.exception
    assert app.text_input(key="preferred_name").value == "Sample (fictional)"
    assert "mild headache" in app.text_area(key="symptoms").value.lower()
    assert app.multiselect(key="red_flags").options == [*URGENT_TERMS, UNSURE_OPTION]

    app.button(key="create_summary").click().run()
    assert not app.exception
    summary = app.text_area(key="summary_preview").value
    assert "Symptoms described: A mild headache" in summary
    assert "Questions or concerns to discuss:" in summary
    narrative = app.session_state["intake_narrative"]
    assert "mild headache" in narrative.lower()
    assert "Sample (fictional)" not in narrative
    assert "18–39" not in narrative
    assert "Warning signs" not in narrative
    assert len(app.get("download_button")) == 1

    local_response = BytesIO(json.dumps({"response": "Details explicitly mentioned\n- Headache"}).encode())
    with patch("carebridge.local_ai.urlopen", return_value=local_response):
        app.button(key="organize_local_notes").click().run()
    assert not app.exception
    assert app.text_area(key="local_ai_draft").value.endswith("- Headache")
    assert "Symptoms described: A mild headache" in app.text_area(key="summary_preview").value

    with patch("carebridge.local_ai.urlopen", side_effect=URLError("connection refused")):
        app.button(key="organize_local_notes").click().run()
    assert not app.exception
    assert any("Could not connect to Ollama" in error.value for error in app.error)
    assert all(widget.key != "local_ai_draft" for widget in app.text_area)

    app.run()
    assert "Symptoms described: A mild headache" in app.text_area(key="summary_preview").value

    app.button(key="clear_form").click().run()
    assert not app.exception
    assert app.text_input(key="preferred_name").value == ""
    assert all(widget.key != "summary_preview" for widget in app.text_area)
