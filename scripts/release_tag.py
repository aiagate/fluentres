"""Classify and validate release tags used by the publish workflows."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Literal

from packaging.version import InvalidVersion, Version

ReleaseKind = Literal["stable", "prerelease"]


def parse_release_tag(tag: str) -> Version:
    """Return the PEP 440 version represented by a valid release tag."""
    if not tag.startswith("v"):
        raise ValueError(f"release tag must start with 'v': {tag!r}")

    try:
        version = Version(tag[1:])
    except InvalidVersion as error:
        raise ValueError(
            f"release tag is not a valid PEP 440 version: {tag!r}"
        ) from error

    if version.local is not None:
        raise ValueError(
            f"local versions cannot be published to package indexes: {tag!r}"
        )

    return version


def classify_release_tag(tag: str) -> ReleaseKind:
    """Classify a valid release tag for the appropriate package index."""
    version = parse_release_tag(tag)
    return "prerelease" if version.is_prerelease else "stable"


def _write_github_output(classification: ReleaseKind) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path is None:
        print(classification)
        return

    with Path(output_path).open("a", encoding="utf-8") as stream:
        print(f"classification={classification}", file=stream)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag", help="release tag to classify")
    args = parser.parse_args()

    try:
        classification = classify_release_tag(args.tag)
    except ValueError as error:
        parser.exit(1, f"{error}\n")
    _write_github_output(classification)


if __name__ == "__main__":
    main()
