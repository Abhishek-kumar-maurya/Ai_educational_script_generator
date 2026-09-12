from core.validator import parse_seconds, deterministic_validate

def test_parse_seconds():
    assert parse_seconds("01:30") == 90

def test_valid_script():
    script = {
        "scenes": [{
            "start_time": "00:00",
            "end_time": "00:20",
            "visual_animation": "Show a simple diagram.",
            "voiceover_dialogue": "Let us explore this.",
            "ots_sfx": "WHOOSH"
        }]
    }
    result = deterministic_validate(script, 1, [])
    assert result["valid_schema"] is True
