import os
import sys
import json
import nuke

# ── 1. Path setup ──────────────────────────────────────────────────────────────
_HERE    = os.path.dirname(os.path.abspath(__file__))
_NK_ROOT = os.path.join(os.path.expanduser("~"), ".nuke", "NK VFX Folder_Creator")

# Auto-detect versioned subfolder (cp37 / cp39 / cp310 / cp311 …)
_VARIANT     = "cp{}{}".format(sys.version_info[0], sys.version_info[1])
_VARIANT_DIR = os.path.join(_NK_ROOT, _VARIANT)
for _p in (_HERE, _VARIANT_DIR, _NK_ROOT):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
try:
    nuke.pluginAddPath(_VARIANT_DIR)
except Exception:
    pass