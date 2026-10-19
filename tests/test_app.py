from pathlib import Path

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
    assert len(app.get("download_button")) == 1

    app.run()
    assert "Symptoms described: A mild headache" in app.text_area(key="summary_preview").value

    app.button(key="clear_form").click().run()
    assert not app.exception
    assert app.text_input(key="preferred_name").value == ""
    assert all(widget.key != "summary_preview" for widget in app.text_area)
