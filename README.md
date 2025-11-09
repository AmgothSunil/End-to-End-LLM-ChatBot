# 🤖 End-to-End LLM Chatbot

A production-ready conversational AI chatbot built with **FastAPI**, **Streamlit**, and deployed on **AWS ECS (Fargate)**. Features persistent chat history with **AWS RDS MySQL**, **Google Gemini LLM** integration via **LangChain**, and automated CI/CD pipeline using **GitHub Actions**.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Setup](#local-setup)
- [Deployment](#-deployment)
  - [Docker](#docker)
  - [AWS ECS](#aws-ecs)
- [CI/CD Pipeline](#-cicd-pipeline)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

- **FastAPI Backend**: High-performance async API with automatic OpenAPI documentation
- **Streamlit Frontend**: Interactive chat interface for seamless user experience
- **LLM Integration**: Google Gemini powered conversational AI via LangChain
- **Persistent Storage**: Session-based chat history stored in AWS RDS MySQL
- **Containerized**: Docker support for consistent deployments
- **Cloud-Native**: Deployed on AWS ECS Fargate with auto-scaling capabilities
- **Secrets Management**: Secure configuration via AWS Systems Manager Parameter Store
- **CI/CD**: Automated deployments through GitHub Actions
- **Production-Ready**: Comprehensive logging, error handling, and monitoring

---

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│             │         │                  │         │             │
│  Streamlit  │────────▶│  FastAPI Backend │────────▶│  AWS RDS    │
│  Frontend   │         │   (ECS Fargate)  │         │   (MySQL)   │
│             │         │                  │         │             │
└─────────────┘         └──────────────────┘         └─────────────┘
                                │
                                │
                                ▼
                        ┌──────────────┐
                        │    Google    │
                        │    Gemini    │
                        │     LLM      │
                        └──────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI, Uvicorn |
| **Frontend** | Streamlit |
| **LLM** | Google Gemini (via LangChain) |
| **Database** | AWS RDS MySQL |
| **Containerization** | Docker |
| **Cloud Platform** | AWS (ECS, ECR, RDS) |
| **CI/CD** | GitHub Actions |
| **Configuration** | AWS Systems Manager |
| **Logging** | AWS CloudWatch |

---

## 📁 Project Structure

```
END-TO-END-LLM-CHATBOT/
├── .github/
│   └── workflows/
│       └── deploy.yaml           # CI/CD pipeline configuration
├── app/
│   ├── __init__.py
│   ├── aws_rds_db.py            # Database connection and operations
│   ├── chatbot.py               # LLM and LangChain logic
│   ├── config.py                # Configuration management
│   └── main.py                  # FastAPI application entry point
├── frontend/
│   ├── chatbot_app.py           # Streamlit UI
│   └── requirements.txt         # Frontend dependencies
├── .dockerignore
├── .env.example                 # Environment variables template
├── .gitignore
├── dockerfile                   # Container image definition
├── ecs-task-def.json           # ECS task definition
├── LICENSE
├── params.yaml                  # Application parameters
├── pyproject.toml              # Python project configuration
├── README.md
├── requirements.txt            # Backend dependencies
└── uv.lock
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Docker (for containerization)
- AWS Account (for cloud deployment)
- Google Gemini API Key
- MySQL Database (local or RDS)

### Local Setup

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/End-to-End-LLM-ChatBot.git
cd End-to-End-LLM-ChatBot
```

2. **Create virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the root directory:

```env
# Database Configuration
DB_HOST=your-database-host
DB_PORT=3306
DB_USER=your-username
DB_PASSWORD=your-password
DB_NAME=chatbot

# API Keys
GOOGLE_API_KEY=your-google-gemini-api-key
LANGCHAIN_API_KEY=your-langchain-api-key
LANGCHAIN_PROJECT=your-project-name
```

5. **Run the backend**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Run the frontend** (in a separate terminal)

```bash
cd frontend
streamlit run chatbot_app.py
```

Access the application:
- Frontend: `http://localhost:8501`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

## 🐳 Deployment

### Docker

Build and run the Docker container:

```bash
# Build image
docker build -t llm-chatbot .

# Run container
docker run -d -p 8000:8000 --env-file .env llm-chatbot
```

### AWS ECS

**1. Create ECR Repository**

```bash
aws ecr create-repository --repository-name llm-chatbot --region ap-south-1
```

**2. Build and Push Docker Image**

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-south-1.amazonaws.com

# Tag and push
docker tag llm-chatbot:latest <account-id>.dkr.ecr.ap-south-1.amazonaws.com/llm-chatbot:latest
docker push <account-id>.dkr.ecr.ap-south-1.amazonaws.com/llm-chatbot:latest
```

**3. Create ECS Cluster**

```bash
aws ecs create-cluster --cluster-name chatbot-cluster --region ap-south-1
```

**4. Configure AWS Systems Manager Parameter Store**

Store sensitive configuration:

```bash
aws ssm put-parameter --name "/chatbot/DB_HOST" --value "your-db-host" --type "String"
aws ssm put-parameter --name "/chatbot/DB_PASSWORD" --value "your-password" --type "SecureString"
# Repeat for all environment variables
```

**5. Deploy ECS Service**

Update `ecs-task-def.json` with your values and deploy:

```bash
aws ecs register-task-definition --cli-input-json file://ecs-task-def.json
aws ecs create-service --cluster chatbot-cluster --service-name chatbot-service --task-definition chatbot-task --desired-count 1 --launch-type FARGATE
```

---

## 🔄 CI/CD Pipeline

The project uses **GitHub Actions** for automated deployments. On every push to the `main` branch:

1. ✅ Builds Docker image
2. ✅ Pushes to Amazon ECR
3. ✅ Updates ECS task definition
4. ✅ Deploys new version to ECS service

**Required GitHub Secrets:**

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `ECR_REPOSITORY`
- `ECS_CLUSTER`
- `ECS_SERVICE`
- `CONTAINER_NAME`

Configure these in: `Repository Settings → Secrets and variables → Actions`

---

## 📚 API Documentation

Once the backend is running, access interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/chat` | Send message and get LLM response |
| GET | `/history/{session_id}` | Retrieve chat history |

---

## ⚙️ Configuration

### Environment Variables

All sensitive configuration is managed via environment variables or AWS Parameter Store:

| Variable | Description | Required |
|----------|-------------|----------|
| `DB_HOST` | Database host endpoint | Yes |
| `DB_PORT` | Database port (default: 3306) | Yes |
| `DB_USER` | Database username | Yes |
| `DB_PASSWORD` | Database password | Yes |
| `DB_NAME` | Database name | Yes |
| `GOOGLE_API_KEY` | Google Gemini API key | Yes |
| `LANGCHAIN_API_KEY` | LangChain API key | No |
| `LANGCHAIN_PROJECT` | LangChain project name | No |

### Application Parameters

Customize application behavior in `params.yaml`:

```yaml
model:
  name: "gemini-pro"
  temperature: 0.7
  max_tokens: 1024

database:
  pool_size: 5
  pool_recycle: 3600
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**GenAI Learner**

- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your Name](https://linkedin.com/in/yourprofile)

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [LangChain](https://langchain.com/) - LLM orchestration
- [Streamlit](https://streamlit.io/) - Interactive UI
- [Google Gemini](https://ai.google.dev/) - Generative AI model

---

## 📊 Project Status

- [x] Core chatbot functionality
- [x] AWS RDS integration
- [x] Docker containerization
- [x] ECS deployment
- [x] CI/CD pipeline
- [ ] User authentication
- [ ] Multi-user support
- [ ] HTTPS with ALB
- [ ] Kubernetes migration

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

</div>
