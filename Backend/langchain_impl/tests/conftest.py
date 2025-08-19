import os
# keep the test env defaults
os.environ.setdefault("CHECKPOINTER_BACKEND", "memory")
os.environ.setdefault("DEPLOY_DDB", "false")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
