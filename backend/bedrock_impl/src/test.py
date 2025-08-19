from bedrock_impl.src.store import AiMessage, Message
from bedrock_impl.src.models import ResponsePart, Chunk

from pydantic import AnyUrl

message = AiMessage(
    session_id = '123',
    message_id = '456',
    body = 'Here is the answer to your query',
    response_parts = [
        ResponsePart(
            text = 'Here is the answer',
            references = [
                Chunk(
                    text = 'Reference content 1',
                    url = AnyUrl('https://google.com')
                )
            ]
        ),
        ResponsePart(
            text = 'to your query',
            references = [
                Chunk(
                    text = 'Reference content 2',
                    url = AnyUrl('https://amazon.com')
                )
            ]
        ),
    ]
)

print(message.model_dump_json())