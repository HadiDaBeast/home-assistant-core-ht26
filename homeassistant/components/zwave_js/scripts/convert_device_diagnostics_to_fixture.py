"""Script to convert a device diagnostics file to a fixture."""

import argparse
import json
import os
from pathlib import Path
from typing import Any

from homeassistant.util import slugify
from homeassistant.util.json import load_json


def get_arguments() -> argparse.Namespace:
    """Get parsed passed in arguments."""
    parser = argparse.ArgumentParser(description="Z-Wave JS Fixture generator")
    parser.add_argument(
        "diagnostics_file", type=Path, help="Device diagnostics file to convert"
    )
    parser.add_argument(
        "--file",
        action="store_true",
        help=(
            "Dump fixture to file in fixtures folder. By default, the fixture will be "
            "printed to standard output."
        ),
    )

    return parser.parse_args()


def get_fixtures_dir_path(data: dict) -> Path:
    """Get path to fixtures directory."""
    device_config = data["deviceConfig"]
    filename = slugify(
        f"{device_config['manufacturer']}-{device_config['label']}_state"
    )
    path = Path(__file__).parents[1]
    # Use the rightmost "homeassistant" component to handle repo paths
    # that themselves contain a "homeassistant" segment.
    index = len(path.parts) - 1 - path.parts[::-1].index("homeassistant")
    return Path(
        *path.parts[:index],
        "tests",
        *path.parts[index + 1 :],
        "fixtures",
        f"{filename}.json",
    )


def path_sanitization(path: Path) -> Path:
    """Sanitizes the path."""
    if "\x00" in os.fspath(path):
        raise ValueError("Null byte in path")
    try:
        canonical_path = path.expanduser().resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Path cannot be resolved: {e}") from e
    if canonical_path.suffix.lower() != ".json":
        raise ValueError("Expected .json format")
    if not canonical_path.is_file():
        raise ValueError("Expected an existing file")
    return canonical_path


def extract_fixture_data(diagnostics_data: Any) -> dict:
    """Extract fixture data from file."""
    if (
        not isinstance(diagnostics_data, dict)
        or "data" not in diagnostics_data
        or "state" not in diagnostics_data["data"]
        or "home_assistant" not in diagnostics_data
        or (
            "integration_manifest" not in diagnostics_data
            and "domain" not in diagnostics_data["integration_manifest"]
        )
        or "custom_components" not in diagnostics_data
    ):
        raise ValueError("Invalid diagnostics file format")
    state: dict = diagnostics_data["data"]["state"]
    if not isinstance(state["values"], list):
        values_dict: dict[str, dict] = state.pop("values")
        state["values"] = list(values_dict.values())
    if not isinstance(state["endpoints"], list):
        endpoints_dict: dict[str, dict] = state.pop("endpoints")
        state["endpoints"] = list(endpoints_dict.values())

    return state


def create_fixture_file(path: Path, state_text: str) -> None:
    """Create a file for the state dump in the fixtures directory."""
    path.write_text(state_text, "utf8")


def main() -> None:
    """Run the main script."""
    args = get_arguments()
    try:
        diagnostics_path: Path = path_sanitization(args.diagnostics_file)
    except ValueError as e:
        print(f"Error: {e}")  # noqa: T201
        return
    diagnostics = load_json(diagnostics_path)
    try:
        fixture_data = extract_fixture_data(diagnostics)
    except ValueError as e:
        print(f"Error: {e}")  # noqa: T201
        return
    fixture_text = json.dumps(fixture_data, indent=2)
    if args.file:
        fixture_path = get_fixtures_dir_path(fixture_data)
        create_fixture_file(fixture_path, fixture_text)
        return
    print(fixture_text)  # noqa: T201


if __name__ == "__main__":
    main()
