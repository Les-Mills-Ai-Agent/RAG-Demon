from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal, ClassVar, Mapping, Callable, Union

from pydantic import AnyUrl, BaseModel, Field, model_serializer

from uuid import uuid4

from mypy_boto3_dynamodb.service_resource import Table as DynamoDBTable
from datetime import datetime, timezone
from typing import Any
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError


from models import AnswerResponseBody, ResponsePart

class ChatStore:

    def __init__(
        self,
        table: DynamoDBTable | None = None
        ) -> None:
            self.table = (
                table
                if table is not None
                else boto3.resource("dynamodb").Table("BedrockSessions")
            )

    def save_message(
        self,
        role: Literal['user', 'ai'],
        body: str,
        session_id: str,
        response_parts: Optional[List[ResponsePart]] = None) -> Union[UserMessage, AiMessage]:

            if role == 'ai':
                if not response_parts:
                    response_parts = []
                message = AiMessage(
                    session_id = session_id,
                    body = body,
                    response_parts = response_parts
                )
            elif role == 'user':
                message = UserMessage(
                    session_id = session_id,
                    body = body
                )
            else:
                raise ValueError("Invalid role")
            
            self.table.put_item(
                Item = message.model_dump(mode = "json")
            )

            return message
        
    def get_latest_messages(self, user_id: str, session_id: str, n: int) -> list[AiMessage | UserMessage]:
        response = self.table.query(
            KeyConditionExpression = Key("session_id").eq(f"SESSION#{session_id}") & Key("created_at_message_id").begins_with("MESSAGE#"),
            ScanIndexForward = False,  # descending order
            Limit = n
        )
        
        messages = response.get("Items", [])
        messages = [Message.from_dynamodb(item = message) for message in messages]

        messages.reverse()

        return messages

    def create_session(self, user_id: str) -> str:
        session = Session(user_id=user_id)

        self.table.put_item(
            Item=session.model_dump(mode = "json")
        )

        return session.session_id
    
    def get_session(self, session_id: str) -> Session:
        response = self.table.query(
            KeyConditionExpression = Key("session_id").eq(f"SESSION#{session_id}") & Key("created_at_message_id").eq("METADATA")
        )

        items = response.get("Items", [])
        if not items:
            raise ValueError(f"Session {session_id} not found")

        # Convert the first (and only) item to a Session object
        session_item = items[0]
        return Session.model_validate(session_item)


class Message(BaseModel):
    session_id: str = Field(..., description = "The session ID this message belongs to")
    message_id: str = Field(
        default_factory = lambda : str(uuid4()),
        description = "Unique identifier for this message"
    )
    role: Literal['user', 'ai'] = Field(..., description = "Role of the message sender")
    body: str = Field(..., description = "Content of the message")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
        description="UTC timestamp of message creation in ISO format with milliseconds"
    )

    def __str__(self) -> str:
        return f"[{self.role}] : {self.body}"
    
    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:  
        base = super().model_dump(*args, **kwargs)

        base.pop("session_id", None)
        base.pop("message_id", None)
        base.pop("created_at", None)

        base.update({
            "session_id": f"SESSION#{self.session_id}",
            "created_at_message_id": f"MESSAGE#{self.created_at}#{self.message_id}"
        })
        return base
    
    @staticmethod
    def from_dynamodb(item: Dict[str, Any]) -> Union[AiMessage, UserMessage]:
        
        session_id = item.pop("session_id", "")
        created_at_message_id = item.pop("created_at_message_id", "")

        session_id = session_id.removeprefix("SESSION#")
        created_at_message_id = created_at_message_id.removeprefix("MESSAGE#")

        created_at, message_id = created_at_message_id.split("#", 1)

        item["session_id"] = session_id
        item["message_id"] = message_id
        item["created_at"] = created_at

        role = item.get("role")

        if role == 'ai':
            return AiMessage.model_validate(item)
        if role == 'user':
            return UserMessage.model_validate(item)
        else:
            raise ValueError("Unknown role")

    
class AiMessage(Message):
    role: Literal['user', 'ai'] = 'ai'
    response_parts: List[ResponsePart] = Field(..., description="List of parts that make up the AI response")

class UserMessage(Message):
    role: Literal['user', 'ai'] = 'user'

class Session(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()), description="The ID of the session")
    user_id: str = Field(..., description="The ID of the user generated by cognito")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
        description="UTC timestamp of session creation in ISO format with milliseconds"
    )
    last_updated: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
        description="UTC timestamp of the last message sent in ISO format with milliseconds"
    )

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        base = super().model_dump(*args, **kwargs)

        base.pop("session_id", None)

        base.update({
            "session_id": f"SESSION#{self.session_id}",
            "created_at_message_id": "METADATA"
        })

        return base
    
    def from_dynamodb(self, item: Dict[str, Any]) -> Session:

        session_id = item.pop("session_id", "")

        session_id = session_id.removeprefix("SESSION#")

        item["session_id"] = session_id

        return Session.model_validate(item)

