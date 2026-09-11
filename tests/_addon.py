"""Carrega os módulos puros do addon sem o Anki instalado.

`anki_mc_quiz/__init__.py` faz `from aqt import ...` logo na primeira linha, por
isso um import normal do pacote falha fora do Anki. Registamos um pacote
sintético com o mesmo nome cujo `__path__` aponta para a pasta do addon: os
submódulos `i18n` e `parsers` resolvem por esse caminho e o `__init__.py` nunca
chega a correr.
"""

import importlib
import pathlib
import sys
import types

ROOT = pathlib.Path(__file__).resolve().parent.parent
ADDON_DIR = ROOT / "anki_mc_quiz"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"

if "anki_mc_quiz" not in sys.modules:
    _pkg = types.ModuleType("anki_mc_quiz")
    _pkg.__path__ = [str(ADDON_DIR)]
    sys.modules["anki_mc_quiz"] = _pkg

parsers = importlib.import_module("anki_mc_quiz.parsers")
i18n = importlib.import_module("anki_mc_quiz.i18n")


def fixture(name: str) -> str:
    return (FIXTURES / f"{name}.txt").read_text(encoding="utf-8")
