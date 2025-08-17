# Make both package and top-level modules importable for tests
import os, sys

# Paths
BACKEND = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))          # .../Backend
SRC     = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))         # .../Backend/langchain_impl/src

for p in (BACKEND, SRC):
    if p not in sys.path:
        sys.path.insert(0, p)

# Quick sanity (won't raise if absent; safe no-op)
try:
    import vector_stores, app  # top-level modules in src
    import langchain_impl.src.app  # package path used by tests
except Exception:
    pass
