# 🤖 End-to-End LLM Chatbot (MongoDB + FastAPI + Streamlit)

A full-stack, production-ready conversational AI chatbot powered by Google Gemini LLM. Built with FastAPI, LangChain, and Streamlit, this project features a MongoDB backend for persistent chat history, automated CI/CD with GitHub Actions, and cloud deployment (AWS ECS for backend, Render for frontend).

<div align="center">

⭐ **Star this repo if it helped you build your own LLM chatbot!** ⭐

</div>

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#-architecture)
- [🛠️ Tech Stack](#-tech-stack)
- [📁 Project Structure](#-project-structure)
- [🚀 Getting Started (Local)](#-getting-started-local)
- [🐳 Backend Deployment (AWS ECS)](#-backend-deployment-aws-ecs)
- [🌐 Frontend Deployment (Render)](#-frontend-deployment-render)
- [🔄 CI/CD (GitHub Actions)](#-cicd-github-actions)
- [📚 API Documentation](#-api-documentation)
- [⚙️ Configuration Reference](#-configuration-reference)
- [🧠 Example Prompt Flow](#-example-prompt-flow)
- [👨‍💻 Author](#-author)
- [📊 Project Status](#-project-status)
- [📜 License](#-license)

---

## ✨ Features

- ✅ **FastAPI Backend (Async)** – High-performance, production-grade REST API
- 💬 **Streamlit Frontend (Render)** – Clean, interactive chat interface
- 🧠 **Google Gemini Integration** – LLM-powered intelligent responses via LangChain
- 🗄️ **MongoDB Storage** – Session-based chat memory persistence
- 🐳 **Dockerized Architecture** – Fully containerized for portability
- ☁️ **AWS ECS (Fargate)** – Scalable, serverless backend hosting
- 🔐 **Secure Config via SSM** – AWS Parameter Store for environment secrets
- 🔁 **GitHub Actions CI/CD** – Automated deployment pipeline
- 📜 **Structured Logging** – AWS CloudWatch + Rotating file logs

---

## 🏗️ Architecture

```
┌────────────────┐       ┌──────────────────┐       ┌───────────────┐
│ Streamlit UI   │──────▶│  FastAPI Backend │──────▶│   MongoDB     │
│ (Render Cloud) │       │   (AWS ECS)      │       │   (Atlas)     │
└────────────────┘       └──────────────────┘       └───────────────┘
                               │
                               ▼
                         ┌────────────┐
                         │ Google     │
                         │ Gemini LLM │
                         └────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit (Render Cloud) |
| **Backend** | FastAPI, Uvicorn |
| **Database** | MongoDB Atlas |
| **LLM** | Google Gemini (LangChain Integration) |
| **Cloud Backend** | AWS ECS (Fargate) |
| **Containerization** | Docker |
| **CI/CD** | GitHub Actions |
| **Secrets** | AWS Systems Manager (Parameter Store) |
| **Monitoring** | AWS CloudWatch |

---

## 📁 Project Structure

```
END-TO-END-LLM-CHATBOT/
├── .github/
│   └── workflows/
│       └── deploy.yaml              # CI/CD pipeline
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   └── fastapi_app.py          # FastAPI entry point
│   ├── core/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── config.py               # Configuration loader
│   │   ├── exception.py            # Custom exceptions
│   │   └── logger.py               # Logging setup
│   ├── db/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   └── mango_database.py       # MongoDB async integration
│   ├── services/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── chatbot.py              # Chatbot logic (LangChain + Gemini)
│   │   ├── smoke_test_chat.py      # Smoke tests
│   │   └── __init__.py
│   └── tests/
│       ├── __pycache__/
│       ├── __init__.py
│       └── smoke_test_chat.py      # Test suite
├── config/
│   └── params.yaml                 # Application parameters
├── frontend/
│   ├── __init__.py
│   └── chatbot_app.py              # Streamlit frontend
├── .dockerignore                   # Docker ignore rules
├── .env                            # Environment variables (local)
├── .env.example                    # Example environment variables
├── .gitignore                      # Git ignore rules
├── .python-version                 # Python version specification
├── dockerfile                      # Docker image definition
├── ecs-task-def.json               # ECS Fargate task definition
├── lim.chatbot.egg-info/           # Package metadata
├── LICENSE                         # License file
├── README.md                       # This file
├── pyproject.toml                  # Project configuration
├── requirements.txt                # Python dependencies
└── uv.lock                         # UV package manager lock file
```

---

## 🚀 Getting Started (Local)

### Prerequisites

- **Python 3.10+**
- **Docker** (for containerization)
- **MongoDB Atlas** (cloud) or local MongoDB instance
- **Google Gemini API Key** – Get it from [Google Cloud Console](https://console.cloud.google.com/)
- **AWS Account** (for deployment)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/End-to-End-LLM-ChatBot.git
   cd End-to-End-LLM-ChatBot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**

   Create a `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your credentials:
   ```
   # MongoDB Configuration
   MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/
   MONGO_DB_NAME=Chatbot_DB
   MONGO_COLLECTION=Chatbot_History

   # Google Gemini Configuration
   GOOGLE_API_KEY=your-google-gemini-api-key

   # LangChain Configuration
   LANGCHAIN_API_KEY=your-langchain-api-key
   LANGCHAIN_PROJECT=chatbot
   ```

5. **Run FastAPI backend locally**
   ```bash
   uvicorn app.api.fastapi_app:app --reload --port 8000
   ```

   API documentation available at: [http://localhost:8000/docs](http://localhost:8000/docs)

6. **Run Streamlit frontend** (in a new terminal)
   ```bash
   cd frontend
   streamlit run chatbot_app.py
   ```

   Access UI at: [http://localhost:8501](http://localhost:8501)

---

## 🐳 Backend Deployment (AWS ECS)

### Step 1: Build Docker Image

```bash
docker build -t fastapi_chatbot .
```

### Step 2: Push to Amazon ECR

```bash
# Get login token
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-south-1.amazonaws.com

# Tag image
docker tag fastapi_chatbot:latest <account-id>.dkr.ecr.ap-south-1.amazonaws.com/fastapi-chatbot:latest

# Push to ECR
docker push <account-id>.dkr.ecr.ap-south-1.amazonaws.com/fastapi-chatbot:latest
```

### Step 3: Store Environment Variables in AWS Systems Manager Parameter Store

```bash
aws ssm put-parameter \
  --name "/chatbot/MONGO_URI" \
  --value "mongodb+srv://..." \
  --type "SecureString" \
  --region ap-south-1

aws ssm put-parameter \
  --name "/chatbot/GOOGLE_API_KEY" \
  --value "your-api-key" \
  --type "SecureString" \
  --region ap-south-1

aws ssm put-parameter \
  --name "/chatbot/LANGCHAIN_API_KEY" \
  --value "your-langchain-key" \
  --type "SecureString" \
  --region ap-south-1
```

### Step 4: Register ECS Task Definition

```bash
aws ecs register-task-definition \
  --cli-input-json file://ecs-task-def.json \
  --region ap-south-1
```

### Step 5: Create ECS Service

```bash
aws ecs create-service \
  --cluster chatbot-cluster \
  --service-name chatbot-service \
  --task-definition fastapi-task:1 \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --region ap-south-1
```

---

## 🌐 Frontend Deployment (Render)

### Step 1: Connect Repository to Render

- Go to [https://render.com](https://render.com) → **Create New** → **Web Service**
- Connect your GitHub repository

### Step 2: Configure Build & Start Commands

**Build Command:**
```bash
pip install -r frontend/requirements.txt
```

**Start Command:**
```bash
streamlit run frontend/chatbot_app.py --server.port 10000 --server.address 0.0.0.0
```

### Step 3: Add Environment Variables

In Render dashboard, add:

| Variable | Value |
|----------|-------|
| `API_URL` | `https://your-ecs-endpoint/chat` |

### Step 4: Deploy

Click **Deploy** and wait for the service to go live! 🚀

Your frontend is now live on Render, communicating with your AWS ECS backend.

---

## 🔄 CI/CD (GitHub Actions)

The workflow in `.github/workflows/deploy.yaml` automatically:

1. Builds the Docker image
2. Pushes to Amazon ECR
3. Updates the ECS task definition
4. Deploys the latest version to ECS

### Required GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets → Actions):

| Secret | Description | Example |
|--------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_REGION` | AWS deployment region | `ap-south-1` |
| `ECR_REPOSITORY` | ECR repository name | `fastapi-chatbot` |
| `ECS_CLUSTER` | ECS cluster name | `chatbot-cluster` |
| `ECS_SERVICE` | ECS service name | `chatbot-service` |
| `CONTAINER_NAME` | ECS container name | `fastapi-container` |

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000  (local)
https://your-ecs-endpoint  (production)
```

### Endpoints

#### 1. Health Check
```http
GET /
```

**Response:**
```json
{
  "status": "healthy",
  "message": "FastAPI Chatbot Backend is running"
}
```

#### 2. Chat Endpoint
```http
POST /chat
```

**Request Body:**
```json
{
  "user_id": "user_123",
  "message": "What is LangChain?",
  "session_id": "session_456"
}
```

**Response:**
```json
{
  "user_id": "user_123",
  "session_id": "session_456",
  "user_message": "What is LangChain?",
  "assistant_response": "LangChain is a framework for building applications powered by large language models.",
  "timestamp": "2025-11-09T14:30:00Z"
}
```

---

## ⚙️ Configuration Reference

### Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `MONGO_URI` | MongoDB connection string | ✅ | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `MONGO_DB_NAME` | MongoDB database name | ✅ | `Chatbot_DB` |
| `MONGO_COLLECTION` | MongoDB collection name | ✅ | `Chatbot_History` |
| `GOOGLE_API_KEY` | Google Gemini API key | ✅ | `AIzaSy...` |
| `LANGCHAIN_API_KEY` | LangChain API key | ❌ | `ls__...` |
| `LANGCHAIN_PROJECT` | LangChain project name | ❌ | `chatbot` |

### Configuration File (`config/params.yaml`)

```yaml
chatbot:
  model: "gemini-pro"
  temperature: 0.7
  max_tokens: 512
  
mongo:
  timeout: 30
  retry_attempts: 3
  
logging:
  level: "INFO"
  format: "structured"
```

---

## 🧠 Example Prompt Flow

```
User: What is LangChain?
Assistant: LangChain is a framework for building applications powered by 
large language models. It provides tools and abstractions for working with LLMs.

User: Explain it like I'm 10 years old.
Assistant: Imagine a super smart robot that can read, understand, and write. 
LangChain is the toolbox that helps people build that robot!

User: Can you show me an example?
Assistant: Sure! Here's a simple example using Python:
```python
from langchain import OpenAI, PromptTemplate

llm = OpenAI(temperature=0.9)
prompt = PromptTemplate(input_variables=["topic"], template="Tell me about {topic}")
result = llm(prompt.format(topic="Python"))
print(result)
```

---

## 🛠️ Development & Testing

### Run Smoke Tests

```bash
pytest tests/smoke_test_chat.py -v
```

### View Logs Locally

```bash
tail -f logs/app.log
```

### AWS CloudWatch Logs (Production)

```bash
aws logs tail /ecs/fastapi-chatbot --follow --region ap-south-1
```

---

## 📝 Troubleshooting

### Issue: MongoDB Connection Error
- ✅ Verify `MONGO_URI` format is correct
- ✅ Check IP whitelist in MongoDB Atlas
- ✅ Ensure credentials are URL-encoded

### Issue: Gemini API Rate Limit
- ✅ Add request retry logic
- ✅ Implement exponential backoff
- ✅ Monitor API usage in Google Cloud Console

### Issue: ECS Task Failing
- ✅ Check CloudWatch logs: `aws logs tail /ecs/fastapi-chatbot`
- ✅ Verify IAM permissions for SSM Parameter Store
- ✅ Confirm security group rules allow egress

---

## 👨‍💻 Author

**Your Name / GenAI Learner**

- 🚀 **GitHub:** [@yourusername](https://github.com/yourusername)
- 💼 **LinkedIn:** [Your Profile](https://linkedin.com/in/yourprofile)
- 🌐 **Portfolio:** [yourwebsite.com](https://yourwebsite.com)

---

## 📊 Project Status

- ✅ FastAPI + Async MongoDB backend
- ✅ Streamlit frontend
- ✅ AWS ECS backend deployment
- ✅ Render frontend deployment
- ✅ CI/CD GitHub Actions pipeline
- 🔄 Authentication system (in progress)
- ⏳ HTTPS + Custom domain
- ⏳ Load balancing with ALB
- ⏳ Multi-region deployment

---

## 📜 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

<div align="center">

**⭐ If this project helped you, please star it! ⭐**

Made with ❤️ by GenAI Learner

</div>