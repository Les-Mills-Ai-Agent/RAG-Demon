from typing import Optional
from bedrock_impl.models import RAGRequest, RAGResponse
from bedrock_impl.store import AiMessage, UserMessage

import boto3

from mypy_boto3_bedrock_agent_runtime.type_defs import RetrieveAndGenerateResponseTypeDef, RetrieveAndGenerateConfigurationTypeDef
from mypy_boto3_bedrock_agent_runtime import AgentsforBedrockRuntimeClient
from aws_lambda_powertools import Logger

from uuid import uuid4
from datetime import datetime, timezone

logger = Logger(service="rag-bedrock-lambda")

class Bedrock:

    def __init__(
        self,
        client: AgentsforBedrockRuntimeClient | None = None,
        rag_config: RetrieveAndGenerateConfigurationTypeDef | None = None
        ) -> None:
            self.client = (
                client
                if client is not None
                else boto3.client("bedrock-agent-runtime")
            )
            self.rag_config = (
                rag_config
                if rag_config is not None
                else RetrieveAndGenerateConfigurationTypeDef(
                    type = "KNOWLEDGE_BASE",
                    knowledgeBaseConfiguration={
                        "knowledgeBaseId": "XBOBJWN1MQ",
                        "modelArn": "anthropic.claude-3-5-sonnet-20240620-v1:0",
                        "generationConfiguration": {
                            "guardrailConfiguration": {
                                "guardrailId": "3x3fwig8roag",
                                "guardrailVersion": "3",
                            },
                            "promptTemplate": {
                                "textPromptTemplate": """
                                    <task>
                                        You are a specialized customer support assistant for Les Mills B2B customers.
                                        Your task is to answer the customer's question accurately using only the information
                                        provided in the retrieved context and previous chat history.
                                    </task>
                                    <instructions>
                                        - Read the customer's question, retrieved context, and chat history carefully
                                        - Base your answer EXCLUSIVELY on the information in the retrieved context
                                        - If the retrieved context does not contain the answer to the question, respond with 
                                        \"I don't have enough information to answer this question based on the available context.\"
                                        - Maintain a professional, helpful tone appropriate for B2B customer support
                                        - Ask the user for further clarification or context if it would help to answer the question accurately
                                        - Provide concise, accurate answers without adding information beyond what's in the context
                                        - Reference specific parts of the context to support your answer when applicable
                                    </instructions>
                                    
                                    <conversation>
                                        $input$
                                    </conversation>
                                    
                                    <retrieved_context>
                                        $search_results$
                                    </retrieved_context>
                                    
                                    Please formulate your response based solely on the above information.
                                    Begin your answer directly addressing the customer's question without
                                    repeating or summarizing the question itself.
                                """
                            }
                        }
                    }
                )
            )

    def parse_request(self, body: str) -> RAGRequest:
        """
        Parse and validate the incoming JSON request body into a QuestionRequest.
        """
        return RAGRequest.model_validate_json(body)

    def generate_response(self, query: str, context: Optional[list[AiMessage | UserMessage]] = None) -> RetrieveAndGenerateResponseTypeDef:
        try:
            if context:
                input = query + str([str(msg) + " | " for msg in context])
            else:
                input = query

            return self.client.retrieve_and_generate(
                input = {
                    "text": input
                },
                retrieveAndGenerateConfiguration = self.rag_config
            )
        except Exception as e:
             raise RuntimeError(f"Bedrock API call failed: {e}") from e

    def parse_response(self, response: RetrieveAndGenerateResponseTypeDef) -> RAGResponse:
        message_id = str(uuid4())
        output = response.get("output").get("text")
        session_id = response.get("sessionId")
        citations = response.get("citations", [])
        created_at = datetime.now(timezone.utc)

        extracted_parts = []

        for citation in citations:
            generated_response_part = citation.get("generatedResponsePart")
            part_text = None
            if generated_response_part:
                text_response_part = generated_response_part.get("textResponsePart")
                if text_response_part:
                    part_text = text_response_part.get("text")

            refs = citation.get("retrievedReferences", [])
            simplified_refs = [
                {
                    "text": ref.get("content", {}).get("text"),
                    "url": ref.get("location", {}).get("webLocation", {}).get("url"),
                }
                for ref in refs
                if ref.get("location", {}).get("type") == "WEB"
            ]

            extracted_parts.append({
                "text": part_text,
                "references": simplified_refs,
            })

        return RAGResponse(
            message_id = message_id,
            content = output,
            response_parts = extracted_parts,
            session_id = session_id,
            created_at = created_at
        )