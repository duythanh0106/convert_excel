# ⚙️ Configuration Guide

Hướng dẫn cấu hình chi tiết cho Universal File Converter.

---

## 📋 Mục Lục

1. [Environment Variables](#environment-variables)
2. [Docker Configuration](#docker-configuration)
3. [API Configuration](#api-configuration)
4. [Authentication Setup](#authentication-setup)
5. [Performance Tuning](#performance-tuning)
6. [Logging Configuration](#logging-configuration)
7. [Security Best Practices](#security-best-practices)

---

## 🔑 Environment Variables

### Tạo .env File

```bash
cp .env.example .env
```

### Biến Bắt Buộc

```dotenv
# Security - Tạo secret key mạnh
# Command: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-random-secret-key-here-min-32-chars
```

### Biến Tuỳ Chọn

```dotenv
# ============================================================================
# SERVER CONFIGURATION
# ============================================================================

# Môi trường chạy
FASTAPI_ENV=development              # production | development | testing

# Server binding
HOST=0.0.0.0                         # 0.0.0.0 (all interfaces) or 127.0.0.1
PORT=8080                            # Port để lắng nghe

# Tên ứng dụng
APP_NAME=Universal File Converter
APP_VERSION=3.0.0

# ============================================================================
# FILE MANAGEMENT
# ============================================================================

# Thư mục lưu upload
UPLOAD_FOLDER=uploads

# Thư mục lưu output
OUTPUT_FOLDER=outputs

# Kích thước file tối đa (bytes)
MAX_FILE_SIZE=104857600              # 100MB (default)
                                     # 52428800 = 50MB
                                     # 209715200 = 200MB

# Các extension được phép (comma-separated)
ALLOWED_EXTENSIONS=.xlsx,.xls,.pdf,.docx,.pptx,.png,.jpg

# ============================================================================
# AUTO CLEANUP
# ============================================================================

# Số giờ để xóa file cũ (tự động)
CLEANUP_HOURS=24                     # Xóa file > 24h

# Interval check cleanup (seconds)
CLEANUP_INTERVAL=3600                # Check mỗi 1h

# ============================================================================
# TIMEZONE
# ============================================================================

# Múi giờ ứng dụng
TZ=Asia/Ho_Chi_Minh                  # Asia/Ho_Chi_Minh, UTC, etc.

# ============================================================================
# CORS CONFIGURATION
# ============================================================================

# Origins được phép (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Allow credentials
CORS_ALLOW_CREDENTIALS=true

# Allow methods
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS

# Allow headers
CORS_ALLOW_HEADERS=*

# ============================================================================
# LOGGING
# ============================================================================

# Mức độ logging
LOG_LEVEL=info                       # debug | info | warning | error | critical

# Format log
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Log file (optional)
LOG_FILE=logs/app.log

# ============================================================================
# DATABASE (Future)
# ============================================================================

# DATABASE_URL=postgresql://user:password@localhost/convert_tool

# ============================================================================
# OAUTH / OIDC (Optional)
# ============================================================================

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_CLIENT_REDIRECT_URI=http://localhost:8080/auth/callback/google

# Keycloak
KEYCLOAK_SERVER_URL=https://keycloak.company.com
KEYCLOAK_REALM=convert-tool
KEYCLOAK_CLIENT_ID=convert-tool
KEYCLOAK_CLIENT_SECRET=your-keycloak-secret
KEYCLOAK_DISCOVERY_URL=https://keycloak.company.com/realms/convert-tool/.well-known/openid-configuration

# ============================================================================
# MONITORING & OBSERVABILITY
# ============================================================================

# Sentry DSN (Error tracking)
# SENTRY_DSN=https://key@sentry.io/project-id

# Prometheus metrics (Future)
# PROMETHEUS_ENABLED=false

# ============================================================================
# RATE LIMITING (Future)
# ============================================================================

# RATE_LIMIT_ENABLED=false
# RATE_LIMIT_REQUESTS=100
# RATE_LIMIT_PERIOD=60
```

---

## 🐳 Docker Configuration

### docker-compose.yml Production Setup

```yaml
version: '3.8'

services:
  convert-tool:
    build:
      context: .
      dockerfile: dockerfile
    image: convert-tool:3.0.0
    container_name: convert-tool-app
    
    # Ports
    ports:
      - "8080:8080"
    
    # Volumes
    volumes:
      - uploads_data:/app/uploads
      - outputs_data:/app/outputs
      - logs_data:/app/logs
    
    # Environment variables
    environment:
      - FASTAPI_ENV=production
      - HOST=0.0.0.0
      - PORT=8080
      - SECRET_KEY=${SECRET_KEY}
      - MAX_FILE_SIZE=104857600
      - CLEANUP_HOURS=24
      - TZ=Asia/Ho_Chi_Minh
      - LOG_LEVEL=info
    
    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    
    # Auto restart
    restart: unless-stopped
    
    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
    # Logging
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
    
    # Network
    networks:
      - convert-network
    
    # Dependencies
    depends_on:
      - redis  # (Future)

  # Redis cache (Future)
  # redis:
  #   image: redis:7-alpine
  #   container_name: convert-tool-redis
  #   networks:
  #     - convert-network

volumes:
  uploads_data:
    driver: local
  outputs_data:
    driver: local
  logs_data:
    driver: local

networks:
  convert-network:
    driver: bridge
```

---

## 📡 API Configuration

### CORS Setup

```python
# main.py example
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "https://app.company.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,  # 10 minutes
)
```

### Rate Limiting (Future Implementation)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/upload")
@limiter.limit("10/minute")  # 10 requests per minute
async def upload(request: Request, file: UploadFile):
    ...
```

---

## 🔐 Authentication Setup

### Google OAuth Configuration

1. **Tạo Google Cloud Project**
   - Truy cập [Google Cloud Console](https://console.cloud.google.com)
   - Tạo project mới
   - Bật OAuth 2.0 API

2. **Tạo OAuth Credentials**
   - Type: Web application
   - Authorized redirect URIs:
     ```
     http://localhost:8080/auth/callback/google
     https://app.company.com/auth/callback/google
     ```

3. **Cấu Hình .env**
   ```dotenv
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

### Keycloak Configuration

1. **Setup Keycloak Server**
   ```bash
   docker run -d \
     -e KEYCLOAK_ADMIN=admin \
     -e KEYCLOAK_ADMIN_PASSWORD=admin \
     -p 8000:8080 \
     quay.io/keycloak/keycloak:latest \
     start-dev
   ```

2. **Tạo Realm & Client**
   - Realm: `convert-tool`
   - Client: `convert-tool`
   - Client Type: Confidential
   - Valid redirect URIs: `http://localhost:8080/auth/callback/keycloak`

3. **Cấu Hình .env**
   ```dotenv
   KEYCLOAK_SERVER_URL=http://localhost:8000
   KEYCLOAK_REALM=convert-tool
   KEYCLOAK_CLIENT_ID=convert-tool
   KEYCLOAK_CLIENT_SECRET=your-secret
   ```

---

## ⚡ Performance Tuning

### Worker Configuration (Gunicorn)

```bash
# Production: 4x CPU cores
gunicorn main:app \
  --workers 8 \
  --worker-class uvicorn.workers.UvicornWorker \
  --worker-connections 1000 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --bind 0.0.0.0:8080 \
  --access-logfile - \
  --error-logfile -
```

### Database Connection Pool (Future)

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
)
```

### Caching Strategy

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_supported_formats():
    return universal_converter.get_supported_formats()
```

---

## 📊 Logging Configuration

### Structured Logging

```python
import logging
from pythonjsonlogger import jsonlogger

# Setup JSON logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
```

### Log Rotation

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=10485760,  # 10MB
    backupCount=10,
)
logger.addHandler(handler)
```

---

## 🛡️ Security Best Practices

### 1. Secret Management
```bash
# Generate strong secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# NEVER commit secrets
echo ".env" >> .gitignore
```

### 2. HTTPS in Production
```nginx
server {
    listen 443 ssl http2;
    server_name convert.company.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://localhost:8080;
    }
}
```

### 3. Input Validation
```python
# Universal converter validates:
- File extensions
- File sizes
- MIME types
- File structure
```

### 4. Rate Limiting
```python
# Future: Implement rate limiting per IP
# Future: Implement per-user quotas
```

### 5. Database Security (Future)
```python
# Use environment variables for credentials
db_url = os.getenv("DATABASE_URL")
# Never hardcode credentials
```

---

## 📝 Example .env for Development

```dotenv
# Development
FASTAPI_ENV=development
HOST=127.0.0.1
PORT=8080

# Files
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=outputs
MAX_FILE_SIZE=52428800

# Security
SECRET_KEY=dev-key-not-secure-change-in-production

# Logging
LOG_LEVEL=debug

# Cleanup
CLEANUP_HOURS=48
```

---

## 📝 Example .env for Production

```dotenv
# Production
FASTAPI_ENV=production
HOST=0.0.0.0
PORT=8080

# Files
UPLOAD_FOLDER=/data/uploads
OUTPUT_FOLDER=/data/outputs
MAX_FILE_SIZE=104857600

# Security
SECRET_KEY=<generate-strong-key>

# Logging
LOG_LEVEL=info
LOG_FILE=/var/log/convert-tool/app.log

# Cleanup
CLEANUP_HOURS=24

# CORS
CORS_ORIGINS=https://app.company.com

# OAuth
GOOGLE_CLIENT_ID=<your-client-id>
GOOGLE_CLIENT_SECRET=<your-secret>
```

---

## ✅ Configuration Checklist

- [ ] Tạo .env file từ .env.example
- [ ] Generate SECRET_KEY mạnh
- [ ] Set FASTAPI_ENV=production
- [ ] Cấu hình MAX_FILE_SIZE phù hợp
- [ ] Setup CORS origins
- [ ] Configure logging
- [ ] Setup HTTPS/SSL
- [ ] Configure authentication (Google/Keycloak)
- [ ] Setup monitoring
- [ ] Setup backup strategy
- [ ] Test health check endpoint

---

## 🆘 Troubleshooting

### Config Not Loading
```bash
# Check if .env exists
ls -la .env

# Verify variables loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('SECRET_KEY'))"
```

### Port Already in Use
```bash
# Find process using port
lsof -i :8080

# Kill process
kill -9 <PID>
```

### Permission Denied
```bash
# Fix folder permissions
chmod 755 uploads outputs logs
chown -R app:app uploads outputs logs
```

---

For more information, see [README.md](README.md) and [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
