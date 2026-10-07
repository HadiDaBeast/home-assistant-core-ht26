"""Test convert_device_diagnostics_to_fixture script."""

import copy
import json
from pathlib import Path
import sys
from unittest.mock import patch

import pytest

from homeassistant.components.zwave_js.scripts.convert_device_diagnostics_to_fixture import (
    extract_fixture_data,
    get_fixtures_dir_path,
    main,
    path_sanitization,
)

from tests.common import load_fixture, load_json_object_fixture


def _minify(text: str) -> str:
    """Minify string by removing whitespace and new lines."""
    return text.replace(" ", "").replace("\n", "")


def test_fixture_functions() -> None:
    """Test functions related to the fixture."""
    diagnostics_data = load_json_object_fixture("zwave_js/device_diagnostics.json")
    state = extract_fixture_data(copy.deepcopy(diagnostics_data))
    assert isinstance(state["values"], list)
    assert (
        get_fixtures_dir_path(state)
        == Path(__file__).parents[1] / "fixtures" / "zooz_zse44_state.json"
    )

    old_diagnostics_format_data = copy.deepcopy(diagnostics_data)
    old_diagnostics_format_data["data"]["state"]["values"] = list(
        old_diagnostics_format_data["data"]["state"]["values"].values()
    )
    old_diagnostics_format_data["data"]["state"]["endpoints"] = list(
        old_diagnostics_format_data["data"]["state"]["endpoints"].values()
    )

    assert (
        extract_fixture_data(old_diagnostics_format_data)
        == old_diagnostics_format_data["data"]["state"]
    )

    with pytest.raises(ValueError):
        extract_fixture_data({})


def test_null_bytes_in_path() -> None:
    """Test path for null bytes."""
    invalid_path = Path(__file__).parents[1] / "diagnostics\x00.json"
    with pytest.raises(ValueError, match="Null byte in path"):
        path_sanitization(invalid_path)


def test_path_sanitation() -> None:
    """Test path sanitation."""
    valid_path = Path(__file__).parents[1] / "fixtures" / "device_diagnostics.json"
    sanitized_path = path_sanitization(valid_path)
    assert valid_path == sanitized_path


def test_path_invalid_filetype() -> None:
    """Test invalid path sanitization with nonexisting files and unexpected filetype."""
    invaild_path_non_json = Path(__file__).parents[1] / "__init__.py"
    invalid_path_dir = Path(__file__).parents[1]
    invaild_path_non_existant = Path("invalid.json")
    with pytest.raises(ValueError):
        path_sanitization(invaild_path_non_json)
    with pytest.raises(ValueError):
        path_sanitization(invalid_path_dir)
    with pytest.raises(ValueError):
        path_sanitization(invaild_path_non_existant)


def test_main(capfd: pytest.CaptureFixture[str]) -> None:
    """Test main function."""
    fixture_str = load_fixture("zwave_js/zooz_zse44_state.json")
    fixture_dict = json.loads(fixture_str)

    # Test dump to stdout
    args = [
        "homeassistant/components/zwave_js/scripts/convert_device_diagnostics_to_fixture.py",
        str(Path(__file__).parents[1] / "fixtures" / "device_diagnostics.json"),
    ]
    with patch.object(sys, "argv", args):
        main()

    captured = capfd.readouterr()
    assert _minify(captured.out) == _minify(fixture_str)

    # Check file dump
    args.append("--file")
    with (
        patch.object(sys, "argv", args),
        patch(
            "homeassistant.components.zwave_js.scripts.convert_device_diagnostics_to_fixture.Path.write_text"
        ) as write_text_mock,
    ):
        main()

    assert len(write_text_mock.call_args_list) == 1
    assert write_text_mock.call_args[0][0] == json.dumps(fixture_dict, indent=2)
