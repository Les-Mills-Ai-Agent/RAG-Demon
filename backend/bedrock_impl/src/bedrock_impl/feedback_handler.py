import json, os, uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Literal
import boto3
from aws_lambda_powertools import Logger
from pydantic import BaseModel, ValidationError

# Initialise logger
logger = Logger(service="feedback-handler")

TABLE_NAME = os.environ.get("TABLE_NAME", "FeedbackTable")
dynamodb = boto3.client("dynamodb")


# -------------------- helpers --------------------
def _json(status: int, body: Dict[str, Any]):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "authorization, content-type",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
        },
        "body": json.dumps(body),
    }


def _to_attr(v: Any):
    if v is None:
        return {"NULL": True}
    if isinstance(v, bool):
        return {"BOOL": v}
    if isinstance(v, (int, float)):
        return {"N": str(v)}
    if isinstance(v, dict):
        return {"M": {k: _to_attr(v[k]) for k in v}}
    if isinstance(v, list):
        return {"L": [_to_attr(x) for x in v]}
    return {"S": str(v)}


# -------------------- request models (no pk/sk) --------------------
class MetadataIn(BaseModel):
    userAgent: Optional[str] = None
    language: Optional[str] = None
    tzOffsetMin: Optional[float] = None


class FeedbackIn(BaseModel):
    sessionId: Optional[str] = None
    issueType: str
    severity: Literal["Low", "Medium", "High"]
    notes: Optional[str] = None
    includeContext: Optional[bool] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    submittedAt: datetime
    metadata: Optional[MetadataIn] = None


# -------------------- handler --------------------
@logger.inject_lambda_context
def handler(event, _context):
    method = (
        event.get("requestContext", {}).get("http", {}).get("method")
        or event.get("httpMethod")
        or "POST"
    )
    if method == "OPTIONS":
        return _json(200, {"ok": True})
    if method != "POST":
        logger.warning(f"Invalid method attempted: {method}")
        return _json(405, {"error": "Method Not Allowed"})

    # Parse JSON body
    try:
        body = json.loads(event.get("body") or "{}")
    except Exception:
        logger.exception("Invalid JSON in request body")
        return _json(400, {"error": "Invalid JSON"})

    # Validate structure (no pk/sk expected from client)
    try:
        payload = FeedbackIn.model_validate(body)
    except ValidationError as e:
        logger.warning({"validation_error": e.errors()})
        return _json(400, {"error": "Invalid payload", "details": e.errors()})

    # Extract Cognito claims (user identity) from REST API GW authorizer
    claims = (event.get("requestContext", {}).get("authorizer") or {}).get("claims") or {}
    sub = claims.get("sub")
    username = claims.get("cognito:username") or claims.get("username")
    email = claims.get("email")

    if not sub:
        logger.warning("Missing user identity (no JWT sub claim)")
        return _json(401, {"error": "Missing user identity"})

    # Server-generated keys
    submitted_at_iso = payload.submittedAt.isoformat()
    sk = f"FEEDBACK#{submitted_at_iso}#{uuid.uuid4()}"
    pk = f"USER#{sub}"

    received_at = datetime.now(timezone.utc).isoformat()

    # Build DynamoDB item
    item = {
        "pk": {"S": pk},
        "sk": {"S": sk},
        "sessionId": _to_attr(payload.sessionId),
        "issueType": _to_attr(payload.issueType),
        "severity": _to_attr(payload.severity),
        "notes": _to_attr(payload.notes or ""),
        "includeContext": _to_attr(bool(payload.includeContext)),
        "question": _to_attr(payload.question),
        "answer": _to_attr(payload.answer),
        "submittedAt": _to_attr(submitted_at_iso),
        "receivedAt": _to_attr(received_at),
        "metadata": _to_attr({
            "userAgent": payload.metadata.userAgent if payload.metadata else None,
            "language": payload.metadata.language if payload.metadata else None,
            "tzOffsetMin": payload.metadata.tzOffsetMin if payload.metadata else None,
        }),
        "reportedBy": _to_attr({
            "sub": sub,
            "username": username,
            "email": email,
            "displayName": claims.get("name") or username or email or "Anonymous",
        }),
    }

    # Save to DynamoDB
    try:
        dynamodb.put_item(
            TableName=TABLE_NAME,
            Item=item,
            ConditionExpression="attribute_not_exists(pk) AND attribute_not_exists(sk)",
        )
        logger.info("Feedback saved successfully", extra={"pk": pk, "sk": sk})
        # Align with your OpenAPI success example
        return _json(200, {"status": "ok", "id": sk})
    except Exception as e:
        logger.exception("PutItem failed", extra={"error": str(e)})
        return _json(500, {"error": "Failed to save feedback"})
