import os, sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]  # repo root (tests -> langchain_impl -> Backend -> ROOT)
candidates = ["backend", "Backend"]

paths = []
for name in candidates:
    base = ROOT / name
    if base.exists():
        paths += [str(base), str(base / "langchain_impl" / "src")]

for p in paths:
    if p not in sys.path:
        sys.path.insert(0, p)

# Force CI-safe, stateless backend BEFORE any app/server imports
os.environ.setdefault("CHECKPOINTER_BACKEND", "memory")
os.environ.setdefault("DEPLOY_DDB", "false")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
