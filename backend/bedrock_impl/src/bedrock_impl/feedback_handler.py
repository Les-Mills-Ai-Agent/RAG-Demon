import json, os
from datetime import datetime, timezone
from typing import Any, Dict
import boto3

TABLE_NAME = os.environ.get("TABLE_NAME", "FeedbackTable")
dynamodb = boto3.client("dynamodb")

def _json(status: int, body: Dict[str, Any]):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            # API-level CORS is already enabled; header here is harmless/optional
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
    return {"S": str(v)}

def handler(event, _context):
    method = (
        event.get("requestContext", {}).get("http", {}).get("method")
        or event.get("httpMethod")
        or "POST"
    )
    if method == "OPTIONS":
        return _json(200, {"ok": True})

    if method != "POST":
        return _json(405, {"error": "Method Not Allowed"})

    try:
        body = json.loads(event.get("body") or "{}")
    except Exception:
        return _json(400, {"error": "Invalid JSON"})

    required = ["pk", "sk", "issueType", "severity", "submittedAt"]
    missing = [k for k in required if body.get(k) is None]
    if missing:
        return _json(400, {"error": f"Missing fields: {', '.join(missing)}"})

    body.setdefault("receivedAt", datetime.now(timezone.utc).isoformat())

    item = {
        "pk": {"S": body["pk"]},
        "sk": {"S": body["sk"]},
        "sessionId": _to_attr(body.get("sessionId")),
        "issueType": _to_attr(body.get("issueType")),
        "severity": _to_attr(body.get("severity")),
        "notes": _to_attr(body.get("notes") or ""),
        "includeContext": _to_attr(bool(body.get("includeContext"))),
        "question": _to_attr(body.get("question")),
        "answer": _to_attr(body.get("answer")),
        "submittedAt": _to_attr(body.get("submittedAt")),
        "receivedAt": _to_attr(body.get("receivedAt")),
        "metadata.userAgent": _to_attr(body.get("metadata", {}).get("userAgent")),
        "metadata.language": _to_attr(body.get("metadata", {}).get("language")),
        "metadata.tzOffsetMin": _to_attr(body.get("metadata", {}).get("tzOffsetMin")),
    }

    try:
        dynamodb.put_item(
            TableName=TABLE_NAME,
            Item=item,
            ConditionExpression="attribute_not_exists(pk) AND attribute_not_exists(sk)",
        )
        return _json(200, {"ok": True})
    except Exception as e:
        print("PutItem failed:", e)
        return _json(500, {"error": "Failed to save feedback"})
