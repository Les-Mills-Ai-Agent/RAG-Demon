import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "langchain_impl" / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# keep the test env defaults
os.environ.setdefault("CHECKPOINTER_BACKEND", "memory")
os.environ.setdefault("DEPLOY_DDB", "false")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
