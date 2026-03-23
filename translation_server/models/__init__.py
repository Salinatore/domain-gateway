"""
translation_server.models package initializer.

This makes `translation_server.models` importable and attempts to
conveniently re-export public names from any submodules found in the
`translation_server/models` package directory.

Usage:
    from translation_server.models import SomeModel

Notes:
- Submodules are imported dynamically. If a submodule raises during
  import it will be skipped to avoid breaking consumers of the package.
- Only public attributes (not starting with an underscore) are re-exported.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import List

__all__: List[str] = []
__version__ = "0.1.0"

# Dynamically import and re-export public attributes from submodules.
# This keeps the package convenient to use without requiring the caller
# to know the exact submodule layout.
for finder, name, ispkg in pkgutil.iter_modules(__path__):
    # Only consider direct modules in this package
    try:
        module = importlib.import_module(f".{name}", __name__)
    except Exception:
        # Avoid failing the whole package import if a single module has issues.
        # Consumers can still import submodules directly for debugging.
        continue

    # Re-export public attributes from the module into this package namespace.
    for attr_name in dir(module):
        if attr_name.startswith("_"):
            continue
        try:
            attr = getattr(module, attr_name)
        except Exception:
            # If attribute access raises, skip it.
            continue
        globals()[attr_name] = attr
        __all__.append(attr_name)

# Ensure unique, deterministic ordering for __all__
__all__ = sorted(set(__all__))
