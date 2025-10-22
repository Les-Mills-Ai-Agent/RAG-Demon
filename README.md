# RAG-Demon: Les Mills AI Customer Service Assistant

[![AWS SAM](https://img.shields.io/badge/AWS-SAM-orange?logo=amazon-aws)](https://aws.amazon.com/serverless/sam/)
[![React](https://img.shields.io/badge/React-18.2-blue?logo=react)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.13-green?logo=python)](https://python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue?logo=typescript)](https://www.typescriptlang.org/)

An AI-powered customer service assistant specifically designed for Les Mills International. This project uses Retrieval-Augmented Generation (RAG) to provide intelligent, context-aware support by leveraging Les Mills' knowledge base and documentation.

## 🎯 What This Project Does

RAG-Demon is a comprehensive customer service solution that:

- **Answers customer queries** using AI with access to Les Mills' knowledge base
- **Maintains conversation context** across multiple exchanges with session management
- **Provides source attribution** for all responses to ensure transparency
- **Offers dual AI implementations** - AWS Bedrock and LangChain for flexibility
- **Supports real-time chat** with a modern React-based web interface
- **Collects user feedback** to continuously improve response quality

## ✨ Key Features

### 🤖 Intelligent AI Responses
- **RAG-powered answers** using vector search and large language models
- **Source citations** with links to original documentation
- **Conversation memory** that maintains context across chat sessions
- **Multiple AI backends** (AWS Bedrock Knowledge Base and LangChain)

### 🔐 Enterprise-Ready Security
- **AWS Cognito authentication** with OAuth2/OIDC support
- **Role-based access control** with user session management
- **Secure API endpoints** with proper authorization headers

### 🏗️ Scalable Architecture
- **Serverless deployment** using AWS SAM (Lambda, API Gateway, DynamoDB)
- **Auto-scaling infrastructure** that handles variable workloads
- **Multi-environment support** (dev, test, prod) with isolated resources

### 📱 Modern User Experience
- **Responsive web interface** built with React and TypeScript
- **Real-time messaging** with smooth chat interactions
- **Dark/light mode support** for user preference
- **Mobile-friendly design** using TailwindCSS

## 🛠️ Tech Stack

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

## 🚀 Getting Started

### Prerequisites

- **Python 3.13+** with Poetry or pip
- **Node.js 18+** with npm/yarn
- **AWS CLI** configured with appropriate permissions
- **SAM CLI** for local development and deployment
- **OpenAI API key** (for LangChain implementation)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Les-Mills-Ai-Agent/RAG-Demon.git
   cd RAG-Demon
   ```

2. **Set up the backend**
   ```bash
   cd backend/bedrock_impl
   poetry install
   ```

3. **Configure environment variables**
   ```bash
   # Create .env file in backend/langchain_impl/ (if using LangChain)
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Deploy AWS infrastructure**
   ```bash
   cd backend
   sam build
   sam deploy --guided
   ```

5. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   
   # Configure environment variables
   cp .env.example .env.local
   # Edit .env.local with your API URLs and Cognito settings
   ```

6. **Run locally**
   ```bash
   # Start the frontend
   npm run dev
   

### Environment Configuration

The project requires several environment variables:

**Frontend (.env.local):**
```env
VITE_COGNITO_AUTHORITY=https://your-domain.auth.region.amazoncognito.com
VITE_COGNITO_CLIENT_ID=your_cognito_client_id
VITE_API_URL=https://your-api-gateway-url.execute-api.region.amazonaws.com/env
```

**Backend (for LangChain implementation):**
```env
OPENAI_API_KEY=your_openai_api_key
```

## � Usage Examples

### Basic Chat Interaction
```typescript
// Frontend service call
const response = await bedrockRagService.sendMessage({
  message_id: generateId(),
  content: "How do I cancel my Les Mills subscription?",
  session_id: currentSessionId,
  created_at: new Date().toISOString()
});
```

### API Endpoint Usage
```bash
# Send a question to the RAG API
curl -X POST https://your-api-url/rag/bedrock \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "unique_id",
    "content": "What fitness programs are available?",
    "created_at": "2024-01-01T00:00:00Z"
  }'
```


## 🧪 Development

### Running Tests
```bash
# Backend tests
cd backend/bedrock_impl
python -m pytest

cd ../langchain_impl  
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Local Development
```bash
# Start local API Gateway
sam local start-api --port 3001

# Start frontend with hot reload
cd frontend
npm run dev
```

## 📖 API Documentation

The project includes OpenAPI specification in `backend/openapi.yaml`. Key endpoints:

- `POST /rag/bedrock` - Send questions to AI assistant
- `GET /rag/bedrock/conversation/{user_id}` - Get user's conversations
- `GET /rag/bedrock/messages/{session_id}` - Get messages in a session
- `POST /feedback` - Submit user feedback

## 🆘 Support

- **Issues**: Report bugs via [GitHub Issues](https://github.com/Les-Mills-Ai-Agent/RAG-Demon/issues)
- **Les Mills Support**: Contact support for API access and configuration help

---

**Maintainers:** Les Mills AI Agent Team - (Harsh Maharaj, Max Henley, Stephen Dela Cruz, Vishal Nirmalan, Jan Karlo Nito)
**Repository:** [Les-Mills-Ai-Agent/RAG-Demon](https://github.com/Les-Mills-Ai-Agent/RAG-Demon)
