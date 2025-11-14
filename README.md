# Serverless Aquifer Management & Simulation Platform

A full-stack serverless application for managing aquifer data, models, and simulations with AWS Lambda-based processing pipeline.

## 🏗️ Architecture

This project consists of four main components:

- **Backend API** - FastAPI-based REST API for managing models, simulations, and aquifer data
- **Frontend** - React + TypeScript web application for user interface
- **Data Processing** - Python service for running aquifer simulations (deployed as AWS Lambda)
- **Infrastructure** - Terraform modules for AWS deployment (Lambda, SQS, EC2)

## 📁 Project Structure

```
serverless-aquifer-test/
├── backend/              # FastAPI backend service
│   ├── auth/            # Authentication system (JWT, local Cognito mock)
│   ├── models/          # SQLAlchemy database models
│   ├── routers/         # API route handlers
│   ├── schemas/         # Pydantic validation schemas
│   └── main.py          # FastAPI application entry point
├── frontend/            # React + TypeScript frontend
│   └── src/
│       ├── pages/       # Application pages
│       ├── components/  # React components
│       └── contexts/    # React contexts (Auth, Theme)
├── data-processing/     # Simulation processing service
│   ├── classes/         # Core simulation classes
│   └── main.py          # Lambda handler
├── terraform/           # Infrastructure as Code
│   └── modules/         # Terraform modules (Lambda, SQS, EC2)
├── testing/             # Test scripts and data
└── docker-compose.yml   # Local development setup
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 20+
- Docker and Docker Compose
- PostgreSQL (or use Docker Compose)

### Local Development Setup

1. **Start PostgreSQL with Docker Compose:**
```bash
docker-compose up -d
```

2. **Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The backend API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

3. **Frontend Setup:**
```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

4. **Initialize Test Data (Optional):**
```bash
cd backend
python init_test_data.py
python init_auth_data.py
```

## 🔑 Authentication

The application uses JWT-based authentication with a local Cognito mock for development. See [backend/AUTHENTICATION_GUIDE.md](backend/AUTHENTICATION_GUIDE.md) for details.

**Default Development Users:**
- `admin` / any password - Full access
- `user` / any password - Standard user
- `analyst` / any password - Analyst role

## 📡 API Endpoints

### Models
- `POST /api/v1/models/` - Create a new model
- `GET /api/v1/models/` - List all models (paginated)
- `GET /api/v1/models/{id}` - Get specific model
- `PUT /api/v1/models/{id}` - Update model
- `DELETE /api/v1/models/{id}` - Delete model

### Simulations
- `POST /api/v1/simulations/` - Create a new simulation
- `GET /api/v1/simulations/` - List all simulations (paginated)
- `GET /api/v1/simulations/{id}` - Get specific simulation
- `PUT /api/v1/simulations/{id}` - Update simulation
- `DELETE /api/v1/simulations/{id}` - Delete simulation

### Authentication
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/users` - Create new user (admin only)

## 🧪 Testing

Comprehensive test scripts are available in the `testing/` directory:

```bash
cd testing
./scripts/run_all_tests.sh
```

Individual test scripts:
- `test_auth_system.sh` - Authentication tests
- `test_models_new.sh` - Model management tests
- `test_simulations_new.sh` - Simulation tests
- `test_comprehensive_new.sh` - Full integration tests

## ☁️ AWS Deployment

### Infrastructure Setup

The project includes Terraform modules for AWS deployment:

1. **Configure AWS credentials:**
```bash
aws configure
```

2. **Initialize Terraform:**
```bash
cd terraform
terraform init
```

3. **Plan and Apply:**
```bash
terraform plan
terraform apply
```

### Deployed Components

- **Lambda Function** - Processes simulation jobs from SQS
- **SQS Queue** - Message queue for simulation jobs
- **EC2 Instance** - Optional test instance
- **ECR Repository** - Container registry for Lambda function

### Data Processing Service

The data processing service runs as an AWS Lambda function triggered by SQS messages:

1. **Build and Push Docker Image:**
```bash
cd data-processing
./build-push.sh
```

2. **Lambda receives simulation jobs from SQS**
3. **Processes aquifer simulations**
4. **Updates database with results**

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy 2.0** - ORM with multi-database support
- **Pydantic** - Data validation
- **JWT** - Authentication
- **Alembic** - Database migrations
- **PostgreSQL** - Primary database

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router** - Navigation

### Data Processing
- **Python 3.8+** - Simulation engine
- **boto3** - AWS SDK
- **psycopg2** - PostgreSQL adapter

### Infrastructure
- **Terraform** - Infrastructure as Code
- **AWS Lambda** - Serverless compute
- **AWS SQS** - Message queue
- **AWS ECR** - Container registry
- **Docker** - Containerization

## 📊 Database Schema

The application uses PostgreSQL with the following main entities:

- **Users** - User accounts and authentication
- **Models** - Aquifer model configurations (stored as JSON)
- **Simulations** - Simulation runs with status and results
- **Optimization Results** - Optimization outcomes

Database tables are automatically created on application startup.

## 🔧 Configuration

### Environment Variables

**Backend:**
```bash
DATABASE_URL=postgresql://user:password@localhost/aquifer_db
```

**Data Processing (Lambda):**
```bash
DATABASE_URL=postgresql://user:password@host:port/db
DB_USER=aquifer_user
DB_PASSWORD=aquifer_password
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=aquifer_db
```

## 📝 Development

### Database Migrations

```bash
cd backend
python migrate_database.py
# or
alembic upgrade head
```

### Reset Database

```bash
cd backend
python reset_database.py
```

## 📚 Documentation

- [Backend API Documentation](backend/README.md)
- [Authentication Guide](backend/AUTHENTICATION_GUIDE.md)
- [Frontend Documentation](frontend/README.md)
- [Testing Guide](testing/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🔗 Repository

https://github.com/Ahmed-Nasr-hassan/serverless-aquifer-test

