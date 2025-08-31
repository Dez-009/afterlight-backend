# AfterLight FastAPI Backend

Premium digital platform for memorial planning and celebration of life.

## 🚀 Features

- **Authentication & Authorization**: JWT-based auth with role-based access control
- **Persona Management**: Complete CRUD operations for memorial personas
- **Subscription Tiers**: Free, Premium, Religious, Healthcare with automatic limits
- **Downgrade Handling**: Smart persona management when users downgrade
- **Avatar System**: Image upload, cropping, and management
- **Rate Limiting**: Configurable rate limiting per endpoint
- **CORS & Security**: Production-ready security headers and CORS policies
- **Database**: PostgreSQL with SQLAlchemy ORM
- **API Versioning**: Header and URL-based versioning support

## 🏗️ Architecture

```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── middleware/      # Auth, rate limiting, CORS
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic validation schemas
│   ├── services/        # Business logic
│   ├── config.py        # Configuration
│   ├── database.py      # Database connection
│   └── main.py          # FastAPI app
├── Dockerfile           # Container configuration
└── requirements.txt     # Python dependencies
```

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL + SQLAlchemy
- **Authentication**: JWT with python-jose
- **Validation**: Pydantic
- **Rate Limiting**: Custom sliding window implementation
- **Container**: Docker + Docker Compose

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL (or use Docker)

### Local Development

1. **Clone and setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run the backend**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Development

1. **Start all services**:
   ```bash
   docker-compose up -d
   ```

2. **View logs**:
   ```bash
   docker-compose logs -f backend
   ```

3. **Stop services**:
   ```bash
   docker-compose down
   ```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔐 Authentication

The backend uses JWT tokens for authentication:

1. **Login** to get access token
2. **Include token** in Authorization header: `Bearer <token>`
3. **Token expires** after 30 minutes (configurable)

## 🎯 API Endpoints

### Personas
- `GET /api/v1/personas` - List user's personas
- `POST /api/v1/personas` - Create new persona
- `GET /api/v1/personas/{id}` - Get specific persona
- `PUT /api/v1/personas/{id}` - Update persona
- `DELETE /api/v1/personas/{id}` - Delete persona
- `PATCH /api/v1/personas/{id}/access` - Update access status
- `POST /api/v1/personas/{id}/avatar` - Upload avatar

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/signup` - User registration
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - User logout

## 🗄️ Database Models

### User
- Authentication details
- Subscription tier and limits
- Cultural preferences
- Role and permissions

### Persona
- Personal information
- Cultural and religious details
- Memorial preferences
- Access status and storage usage

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth
- **Rate Limiting**: Configurable per-endpoint limits
- **CORS Protection**: Environment-aware CORS policies
- **Input Validation**: Pydantic schema validation
- **SQL Injection Protection**: SQLAlchemy ORM
- **Security Headers**: CSP, X-Frame-Options, etc.

## 📊 Subscription Tiers

| Tier | Personas | Storage | Features |
|------|----------|---------|----------|
| Free | 1 | 100MB | Basic persona creation |
| Premium | 5 | 1GB | Advanced features, AI obituaries |
| Religious | 10 | 2GB | Cultural templates, religious support |
| Healthcare | 20 | 5GB | Professional features, bulk operations |

## 🚀 Deployment

### Railway
1. Connect your GitHub repository
2. Set environment variables
3. Deploy automatically on push

### Docker
```bash
docker build -t afterlight-backend .
docker run -p 8000:8000 afterlight-backend
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_personas.py
```

## 📝 Environment Variables

```bash
# Required
JWT_SECRET=your-super-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db

# Optional
ENVIRONMENT=development
OPENAI_API_KEY=your-openai-key
REDIS_URL=redis://localhost:6379
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

This project is proprietary software for AfterLight platform.

## 🆘 Support

For support, contact the development team or create an issue in the repository.
