# RAG-Demon: Les Mills AI Customer Service Assistant

[![AWS SAM](https://img.shields.io/badge/AWS-SAM-orange?logo=amazon-aws)](https://aws.amazon.com/serverless/sam/)
[![React](https://img.shields.io/badge/React-18.2-blue?logo=react)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.13-green?logo=python)](https://python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue?logo=typescript)](https://www.typescriptlang.org/)

An AI-powered customer service assistant specifically designed for Les Mills International. This project uses Retrieval-Augmented Generation (RAG) to provide intelligent, context-aware support by leveraging Les Mills' knowledge base and documentation.

---

## What This Project Does

RAG-Demon is a comprehensive customer service solution that:

- **Answers customer queries** using AI with access to Les Mills' knowledge base
- **Maintains conversation context** across multiple exchanges with session management
- **Provides source attribution** for all responses to ensure transparency
- **Offers dual AI implementations** - AWS Bedrock and LangChain for flexibility
- **Supports real-time chat** with a modern React-based web interface
- **Collects user feedback** to continuously improve response quality

## Key Features

### Intelligent AI Responses

- **RAG-powered answers** using vector search and large language models
- **Source citations** with links to original documentation
- **Conversation memory** that maintains context across chat sessions
- **Multiple AI backends** (AWS Bedrock Knowledge Base and LangChain)

### Enterprise-Ready Security

- **AWS Cognito authentication** with OAuth2/OIDC support
- **Role-based access control** with user session management
- **Secure API endpoints** with proper authorization headers

### Scalable Architecture

- **Serverless deployment** using AWS SAM (Lambda, API Gateway, DynamoDB)
- **Auto-scaling infrastructure** that handles variable workloads
- **Multi-environment support** (dev, test, prod) with isolated resources

### Modern User Experience

- **Responsive web interface** built with React and TypeScript
- **Real-time messaging** with smooth chat interactions
- **Dark/light mode support** for user preference
- **Mobile-friendly design** using TailwindCSS

## Tech Stack

### Frontend

- **React 18** with TypeScript for type safety
- **Vite** for fast development and optimized builds
- **TailwindCSS** for responsive styling
- **React Query** for efficient data fetching

### Backend

- **Python 3.13** with modern async support
- **AWS Lambda** for serverless compute
- **AWS Bedrock** for managed AI services
- **LangChain** for flexible AI orchestration
- **DynamoDB** for conversation storage

### Infrastructure

- **AWS SAM** for Infrastructure as Code
- **API Gateway** for RESTful API endpoints
- **AWS Cognito** for user authentication
- **OpenSearch Serverless** for vector storage

---

## Usage

### Prerequisites

Before running or deploying the application, ensure you have the following installed and configured.

#### Software

- Node.js (v18 or higher): Frontend runtime
- Python 3.13: Backend runtime
- Git: Version control
- AWS CLI: AWS resource management
- AWS SAM: AWS deployments with Infrastructure as Code (IaC)
- Poetry: Python dependency and virtual environment management

#### Accounts

- AWS: IAM user with admin privileges
- GitHub: Required for running GitHub Actions workflows

### Local Setup

Step 1: Clone the Repository

```bash
git clone https://github.com/Les-Mills-Ai-Agent/RAG-Demon.git
```

Step 2: Set Up Environment

The frontend and backend implementations use separate environments. Choose the one you want to configure:

**Frontend**

```bash
cd frontend
npm install
```

**Bedrock Backend**

```bash
cd backend/bedrock_impl
poetry install
```

**Langchain Prototype**

```bash
cd backend/langchain_impl
poetry install
```

> **Note:** VSCode may not automatically detect the virtual environment created by Poetry. To fix this:
>
> 1. Run `poetry env info`
> 2. Copy the Virtualenv executable path (ends with /bin/python)
> 3. In VSCode → Command Palette → “Python: Select Interpreter”
> 4. Choose “Enter interpreter path…” and paste the copied path

### Deployments

The backend defines its AWS resources in `backend/template.yaml` and should be deployed with AWS SAM.

Some shared resources exist outside of that template:

| Resource                          | Type                             | ARN / ID                                                         |
| --------------------------------- | -------------------------------- | ---------------------------------------------------------------- |
| **lmi-knowledge-base-collection** | OpenSearch Serverless Collection | `arn:aws:aoss:us-east-1:<ACCOUNT_ID>:collection/<COLLECTION_ID>` |
| **lmi-collection-access-policy**  | Access Policy                    | —                                                                |
| **BedrockKnowledgeBaseRole**      | IAM Role                         | `arn:aws:iam::<ACCOUNT_ID>:role/BedrockKnowledgeBaseRole`        |
| **RAG-Demon**                     | Amplify App                      | `<AMPLIFY_APP_ID>`                                               |

Deployment is automated through the GitHub Actions workflow
located at `.github/workflows/deploy.yaml`.

This workflow triggers automatically:

- When a Pull Request to dev is created
- When code is merged into dev or main

> **Note:** The workflow cannot currently be triggered manually.

### Running Locally

To run the frontend locally, you’ll need to set the following environment variables:

- **VITE_COGNITO_AUTHORITY**: URL of the Cognito authority domain
- **VITE_COGNITO_CLIENT_ID**: UUID of the Cognito user pool client
- **VITE_API_URL**: URL of the API

You can retrieve these values using the AWS Management Console or AWS CLI.

### Deployed Application Usage

1. Request a login from an administrator — you’ll receive a temporary password via email.
2. Visit https://www.ragdemon.com
3. Sign in with your email and temporary password.
4. You’ll be prompted to reset your password — choose a strong one.
5. Enter a query in the chat to start interacting with the AI agent.
6. Use the hamburger menu in the top left to view and continue chat sessions
7. Give feedback on a response with the `...` button next to the response

### CLI Prototype Usage

A lightweight CLI prototype is included under backend/langchain_impl. It implements the core RAG workflow using LangChain / LangGraph and the OpenAI API.

This implementation requires two DynamoDB tables for session handling. You can find the required table definitions at https://github.com/justinram11/langgraph-checkpoint-dynamodb

You will need the following environment variables:

- **OPENAI_API_KEY**: Your OpenAI API key
- **CHECKPOINTS_TABLE**: The name of your DynamoDB checkpoints table
- **WRITES_TABLE**: The name of your DynamoDB writes table

To run the prototype:

```bash
cd backend/langchain_impl
poetry install
poetry run ragdemon-cli
```

---

## API Documentation

The project includes OpenAPI specification in `backend/openapi.yaml`. Key endpoints:

- `POST /rag/bedrock` - Send questions to AI assistant
- `GET /rag/bedrock/conversation/{user_id}` - Get user's conversations
- `GET /rag/bedrock/messages/{session_id}` - Get messages in a session
- `POST /feedback` - Submit user feedback

## Support

- **Issues**: Report bugs via [GitHub Issues](https://github.com/Les-Mills-Ai-Agent/RAG-Demon/issues)
- **Les Mills Support**: Contact support for API access and configuration help

---

**Maintainers:** Les Mills AI Agent Team - (Harsh Maharaj, Max Henley, Stephen Dela Cruz, Vishal Nirmalan, Jan Karlo Nito)
**Repository:** [Les-Mills-Ai-Agent/RAG-Demon](https://github.com/Les-Mills-Ai-Agent/RAG-Demon)
