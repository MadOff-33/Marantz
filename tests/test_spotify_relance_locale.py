"""Non-régression locale — spotify-relance doit accepter un uptime décimal
sous une locale à virgule décimale (fr_FR.UTF-8 observé en production).

La locale n'est pas installée sur ce poste : elle est compilée par localedef
--no-archive sous tests/tmp/localetest (aucune installation système), puis
utilisée via LOCPATH. Si la compilation est impossible, skip motivé.
"""
import shutil
import subprocess
from pathlib import Path

import pytest

from test_spotify_relance import Fx  # noqa: E402  (réutilise le harnais existant)

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "spotify-relance.sh"
LOCALES = Path(__file__).resolve().parent / "tmp" / "localetest"


@pytest.fixture(scope="module")
def fr_locale():
    """LOCPATH vers une locale fr_FR.UTF-8 compilée localement, ou skip."""
    if not shutil.which("localedef"):
        pytest.skip("localedef indisponible : locale fr_FR.UTF-8 impossible à produire")
    if not Path("/usr/share/i18n/locales/fr_FR").exists():
        pytest.skip("définitions i18n absentes : locale fr_FR.UTF-8 impossible à produire")
    prefix = LOCALES / "prefix"
    locpath = prefix / "usr" / "lib" / "locale"
    locpath.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["localedef", "--prefix={0}".format(prefix), "--no-archive",
         "-i", "fr_FR", "-f", "UTF-8", "fr_FR.UTF-8"],
        check=True, capture_output=True)
    probe = subprocess.run(
        ["bash", "-c", "printf '%.0f' 3397902.75"],
        env={"PATH": "/usr/bin:/bin", "LC_ALL": "fr_FR.UTF-8",
             "LOCPATH": str(locpath)},
        capture_output=True, text=True)
    if probe.returncode == 0:
        pytest.skip("printf accepte le point décimal : locale non contraignante ici")
    return {"LC_ALL": "fr_FR.UTF-8", "LOCPATH": str(locpath)}


def test_uptime_decimal_locale_fr(tmp_path, fr_locale):
    """Uptime décimal sous fr_FR.UTF-8 : pas de sortie 3 « uptime invalide »."""
    fx = Fx(tmp_path)
    fx.upt.write_text("3397902.75 99999.00\n")
    env = fx.env()
    env.update(fr_locale)
    result = subprocess.run(
        ["bash", str(SCRIPT), "test"],
        cwd=str(REPO), env=env,
        capture_output=True, text=True, timeout=60)
    assert result.returncode != 3, result.stderr
    assert "uptime invalide" not in result.stderr
