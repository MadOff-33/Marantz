"""Conftest tests.

Place la base temporaire de pytest sous tests/tmp/ du depot (jamais /tmp),
et detecte un systeme de fichiers qui ignore chmod (ex. DrvFs/9p sous WSL) :
ces FS rendent les tests de gardes de permissions et systemd-analyze
non significatifs ; ils sont alors ignores (skip), pas echoues.
"""

import os
from pathlib import Path

import pytest


def pytest_configure(config):
    if config.option.basetemp is None:
        root = Path(__file__).resolve().parent / "tmp"
        root.mkdir(parents=True, exist_ok=True)
        config.option.basetemp = str(root)


def _chmod_ignore() -> bool:
    probe = Path(__file__).resolve().parent / "tmp" / ".probe_chmod"
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_text("")
    os.chmod(probe, 0o000)
    lisible = probe.exists() and probe.read_text() == ""
    probe.unlink(missing_ok=True)
    return lisible


def pytest_collection_modifyitems(config, items):
    if not _chmod_ignore():
        return
    sensibles = {
        "test_guards_lecture_refusee",
        "test_guards_outil_absent_non_executable",
        "test_units_verify_systemd_analyze",
    }
    skips = pytest.mark.skip(
        reason="FS sans chmod effectif (DrvFs/9p) : garde de permissions "
               "et systemd-analyze non significatifs sur ce montage")
    for item in items:
        if item.name.split("[")[0] in sensibles:
            item.add_marker(skips)
