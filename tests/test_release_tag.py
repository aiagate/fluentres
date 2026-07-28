from __future__ import annotations

import sys
from pathlib import Path

import pytest
from packaging.version import Version

from scripts.release_tag import classify_release_tag, main, parse_release_tag


@pytest.mark.parametrize(
    "tag",
    [
        "v1.2.3",
        "v1.2.3.post1",
    ],
)
def test_classifies_stable_release_tags(tag: str) -> None:
    assert classify_release_tag(tag) == "stable"


@pytest.mark.parametrize(
    "tag",
    [
        "v1.2.3rc1",
        "v1.2.3a1",
        "v1.2.3b1",
        "v1.2.3.dev1",
    ],
)
def test_classifies_prerelease_tags(tag: str) -> None:
    assert classify_release_tag(tag) == "prerelease"


def test_returns_parsed_version() -> None:
    assert parse_release_tag("v1.2.3") == Version("1.2.3")


def test_rejects_local_version() -> None:
    with pytest.raises(ValueError, match="local versions cannot be published"):
        classify_release_tag("v1.2.3+local")


def test_rejects_invalid_version() -> None:
    with pytest.raises(ValueError, match="not a valid PEP 440 version"):
        classify_release_tag("vnot-a-version")


def test_rejects_tag_without_v_prefix() -> None:
    with pytest.raises(ValueError, match="must start with 'v'"):
        classify_release_tag("1.2.3")


def test_cli_writes_classification_to_github_output(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "github-output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output_path))
    monkeypatch.setattr(sys, "argv", ["release_tag.py", "v1.2.3rc1"])

    main()

    assert output_path.read_text(encoding="utf-8") == "classification=prerelease\n"
