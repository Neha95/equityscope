# EquityScope Cloud Deployment Guide

## Overview

This guide covers deploying EquityScope v2.0 to production environments using Docker containers, including database setup, monitoring, SSL certificates, and backup strategies.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │     Traefik     │    │      CDN        │
│   (CloudFlare)  │────│  (SSL/Routing)  │────│   (Static)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │     Redis       │
│   (React/Nginx) │    │   (FastAPI)     │    │   (Caching)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Prometheus    │    │    Grafana      │
│  (Production)   │    │  (Monitoring)   │    │  (Dashboard)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

### Server Requirements

**Minimum Requirements:**
- **CPU**: 2 vCPUs
- **RAM**: 4GB
- **Storage**: 50GB SSD
- **Network**: 1Gbps bandwidth

**Recommended (Production):**
- **CPU**: 4+ vCPUs
- **RAM**: 8GB+
- **Storage**: 100GB+ SSD
- **Network**: 1Gbps+ bandwidth

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Ubuntu 20.04+ / CentOS 8+ / Amazon Linux 2
- SSL Certificate (Let's Encrypt recommended)

### Cloud Provider Setup

#### AWS EC2
```bash
# Launch EC2 instance
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --instance-type t3.medium \
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxxx \
    --subnet-id subnet-xxxxxxxxx \
    --user-data file://install-docker.sh
```

#### DigitalOcean Droplet
```bash
# Create droplet with Docker pre-installed
doctl compute droplet create equityscope-prod \
    --region nyc1 \
    --image docker-20-04 \
    --size s-2vcpu-4gb \
    --ssh-keys your-ssh-key-id
```

#### Google Cloud Platform
```bash
# Create VM instance
gcloud compute instances create equityscope-prod \
    --zone=us-central1-a \
    --machine-type=n1-standard-2 \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=50GB \
    --boot-disk-type=pd-ssd
```

## Initial Server Setup

### 1. Update System and Install Docker

```bash
#!/bin/bash
# install-docker.sh

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER

# Install additional tools
sudo apt install -y git htop curl wget unzip

# Configure firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

echo "Docker installation complete. Please logout and login again."
```

### 2. Clone Repository and Setup

```bash
# Clone repository
git clone https://github.com/your-org/equityscope.git
cd equityscope/v2-optimized

# Create production directories
sudo mkdir -p /opt/equityscope/{data,cache,logs,backups}
sudo chown -R $USER:$USER /opt/equityscope

# Create environment files
cp .env.example .env.production
```

## Environment Configuration

### 1. Production Environment Variables

Create `/opt/equityscope/.env.production`:

```bash
# Application Settings
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256

# Database Configuration
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://equityscope_user:secure_password@postgres:5432/equityscope_db
POSTGRES_DB=equityscope_db
POSTGRES_USER=equityscope_user
POSTGRES_PASSWORD=secure_password_change_this

# Redis Configuration
REDIS_URL=redis://redis:6379/0
CACHE_TTL_HOURS=6

# File Storage
DATA_DIR=/app/data
CACHE_DIR=/app/cache
LOG_LEVEL=INFO

# External APIs
CLAUDE_API_KEY=your-claude-api-key
FINANCIAL_DATA_API_KEY=your-financial-api-key

# Security
CORS_ORIGINS=https://equityscope.com,https://www.equityscope.com
ALLOWED_HOSTS=equityscope.com,www.equityscope.com,api.equityscope.com

# SSL/TLS
LETSENCRYPT_EMAIL=admin@equityscope.com
DOMAIN_NAME=equityscope.com
API_DOMAIN=api.equityscope.com

# Monitoring
GRAFANA_PASSWORD=secure_grafana_password
PROMETHEUS_RETENTION=30d

# Backup Configuration
BACKUP_S3_BUCKET=equityscope-backups
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM

# Email Configuration (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=noreply@equityscope.com
SMTP_PASSWORD=your-email-password
FROM_EMAIL=noreply@equityscope.com
```

### 2. Traefik Configuration

Create `traefik/traefik.yml`:

```yaml
# Traefik Configuration
global:
  checkNewVersion: false

api:
  dashboard: true
  debug: false

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
  file:
    directory: /etc/traefik/dynamic
    watch: true

certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@equityscope.com
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web

log:
  level: INFO
  filePath: "/var/log/traefik.log"

accessLog:
  filePath: "/var/log/access.log"
```

Create `traefik/dynamic/middleware.yml`:

```yaml
# Middleware Configuration
http:
  middlewares:
    secureHeaders:
      headers:
        accessControlAllowMethods:
          - GET
          - OPTIONS
          - PUT
          - POST
          - DELETE
        accessControlAllowOriginList:
          - "https://equityscope.com"
          - "https://www.equityscope.com"
        accessControlMaxAge: 100
        hostsProxyHeaders:
          - "X-Forwarded-Host"
        referrerPolicy: "same-origin"
        customRequestHeaders:
          X-Forwarded-Proto: "https"
        customResponseHeaders:
          X-Robots-Tag: "noindex,nofollow,nosnippet,noarchive"
        sslRedirect: true
        sslHost: "equityscope.com"
        sslForceHost: true
        stsSeconds: 31536000
        stsIncludeSubdomains: true
        stsPreload: true
        forceSTSHeader: true
        frameDeny: true
        contentTypeNosniff: true
        browserXssFilter: true
    
    rateLimiter:
      rateLimit:
        average: 100
        burst: 200
```

## Database Setup

### 1. PostgreSQL Production Setup

Create `postgresql/init.sql`:

```sql
-- Initialize EquityScope Database
CREATE DATABASE equityscope_db;
CREATE USER equityscope_user WITH ENCRYPTED PASSWORD 'secure_password_change_this';
GRANT ALL PRIVILEGES ON DATABASE equityscope_db TO equityscope_user;

-- Connect to database
\c equityscope_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant permissions
GRANT ALL ON SCHEMA public TO equityscope_user;
```

### 2. Database Migration

Create `scripts/migrate_to_postgres.py`:

```python
#!/usr/bin/env python3
"""
Migration script from file-based storage to PostgreSQL
"""

import json
import asyncio
import asyncpg
from pathlib import Path
from datetime import datetime

async def migrate_users_to_postgres():
    """Migrate user data from JSON files to PostgreSQL"""
    
    # Connect to PostgreSQL
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="equityscope_user",
        password="secure_password_change_this",
        database="equityscope_db"
    )
    
    try:
        # Create users table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                email VARCHAR(255) UNIQUE NOT NULL,
                full_name VARCHAR(255),
                company VARCHAR(255),
                hashed_password TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'pending_verification',
                email_verified BOOLEAN DEFAULT FALSE,
                tier VARCHAR(50) DEFAULT 'free',
                subscription_start TIMESTAMP,
                subscription_end TIMESTAMP,
                total_analyses INTEGER DEFAULT 0,
                monthly_analyses INTEGER DEFAULT 0,
                rate_limit_count INTEGER DEFAULT 0,
                rate_limit_window_start TIMESTAMP,
                verification_token TEXT,
                reset_token TEXT,
                reset_token_expires TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                last_analysis TIMESTAMP,
                preferences JSONB DEFAULT '{}'
            );
        """)
        
        # Create API keys table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                key_hash TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                expires_at TIMESTAMP,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create sessions table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                ip_address INET,
                user_agent TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Load and migrate user data from JSON files
        data_dir = Path("/opt/equityscope/data")
        users_file = data_dir / "users.json"
        
        if users_file.exists():
            with open(users_file, 'r') as f:
                users_data = json.load(f)
            
            for user_data in users_data.values():
                await conn.execute("""
                    INSERT INTO users (
                        id, email, full_name, company, hashed_password,
                        status, email_verified, tier, total_analyses,
                        monthly_analyses, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    ON CONFLICT (email) DO NOTHING
                """, 
                    user_data["id"],
                    user_data["email"],
                    user_data.get("full_name"),
                    user_data.get("company"),
                    user_data["hashed_password"],
                    user_data.get("status", "pending_verification"),
                    user_data.get("email_verified", False),
                    user_data.get("tier", "free"),
                    user_data.get("total_analyses", 0),
                    user_data.get("monthly_analyses", 0),
                    datetime.fromisoformat(user_data["created_at"]),
                    datetime.fromisoformat(user_data["updated_at"])
                )
        
        print("Migration completed successfully!")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(migrate_users_to_postgres())
```

## Deployment Process

### 1. Production Docker Compose

Update `docker-compose.yml` for production:

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: equityscope-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./postgresql/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - equityscope-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Backend API Service
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: production
    container_name: equityscope-backend
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - CORS_ORIGINS=${CORS_ORIGINS}
    volumes:
      - /opt/equityscope/data:/app/data
      - /opt/equityscope/cache:/app/cache
      - /opt/equityscope/logs:/app/logs
    networks:
      - equityscope-network
    depends_on:
      - postgres
      - redis
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Host(`${API_DOMAIN}`)"
      - "traefik.http.routers.backend.tls=true"
      - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
      - "traefik.http.routers.backend.middlewares=secureHeaders,rateLimiter"

  # Frontend React Application
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: production
    container_name: equityscope-frontend
    restart: unless-stopped
    environment:
      - REACT_APP_API_URL=https://${API_DOMAIN}
      - REACT_APP_ENVIRONMENT=production
    networks:
      - equityscope-network
    depends_on:
      - backend
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`${DOMAIN_NAME}`) || Host(`www.${DOMAIN_NAME}`)"
      - "traefik.http.routers.frontend.tls=true"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
      - "traefik.http.routers.frontend.middlewares=secureHeaders"

volumes:
  postgres-data:
    driver: local
  redis-data:
    driver: local
  traefik-certificates:
    driver: local
  prometheus-data:
    driver: local
  grafana-data:
    driver: local

networks:
  equityscope-network:
    driver: bridge
```

### 2. Deployment Script

Create `scripts/deploy.sh`:

```bash
#!/bin/bash
# Production deployment script

set -e

echo "🚀 Starting EquityScope Production Deployment..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root"
    exit 1
fi

# Set variables
DEPLOY_DIR="/opt/equityscope"
BACKUP_DIR="/opt/equityscope/backups/$(date +%Y%m%d_%H%M%S)"
ENV_FILE=".env.production"

# Create backup
echo "📦 Creating backup..."
sudo mkdir -p "$BACKUP_DIR"
sudo cp -r "$DEPLOY_DIR/data" "$BACKUP_DIR/" 2>/dev/null || true
sudo cp -r "$DEPLOY_DIR/cache" "$BACKUP_DIR/" 2>/dev/null || true

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Load environment variables
if [ -f "$ENV_FILE" ]; then
    export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
else
    echo "❌ Environment file $ENV_FILE not found!"
    exit 1
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f docker-compose.yml --env-file "$ENV_FILE" down
docker-compose -f docker-compose.yml --env-file "$ENV_FILE" build --no-cache
docker-compose -f docker-compose.yml --env-file "$ENV_FILE" up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Run database migrations if needed
echo "🗄️  Running database migrations..."
docker-compose exec backend python scripts/migrate_to_postgres.py

# Health check
echo "🩺 Performing health check..."
sleep 10

if curl -f "https://${API_DOMAIN}/api/v2/health" > /dev/null 2>&1; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed"
    echo "📋 Service logs:"
    docker-compose logs backend
    exit 1
fi

if curl -f "https://${DOMAIN_NAME}" > /dev/null 2>&1; then
    echo "✅ Frontend health check passed"
else
    echo "❌ Frontend health check failed"
    echo "📋 Service logs:"
    docker-compose logs frontend
    exit 1
fi

# Clean up old Docker images
echo "🧹 Cleaning up old images..."
docker image prune -f

echo "🎉 Deployment completed successfully!"
echo "🌐 Frontend: https://${DOMAIN_NAME}"
echo "🔗 API: https://${API_DOMAIN}"
echo "📊 Monitoring: https://grafana.${DOMAIN_NAME}"
```

### 3. First-time Deployment

```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Run initial deployment
./scripts/deploy.sh

# Check logs
docker-compose logs -f
```

## Monitoring and Alerting

### 1. Prometheus Configuration

Create `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

rule_files: []

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'equityscope-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'traefik'
    static_configs:
      - targets: ['traefik:8080']
```

### 2. Grafana Dashboards

Create monitoring dashboards for:
- API response times and error rates
- Database performance metrics
- Cache hit rates and performance
- System resource utilization
- User activity and rate limiting

### 3. Log Management

Configure centralized logging:

```bash
# Configure log rotation
sudo tee /etc/logrotate.d/equityscope << EOF
/opt/equityscope/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 docker docker
    postrotate
        docker exec equityscope-backend kill -USR1 1
    endscript
}
EOF
```

## Backup and Recovery

### 1. Automated Backup Script

Create `scripts/backup.sh`:

```bash
#!/bin/bash
# Automated backup script

set -e

# Configuration
BACKUP_DIR="/opt/equityscope/backups"
S3_BUCKET="equityscope-backups"
RETENTION_DAYS=30

# Create timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="equityscope_backup_$TIMESTAMP"

echo "🔄 Starting backup: $BACKUP_NAME"

# Create backup directory
mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

# Backup PostgreSQL database
echo "📊 Backing up database..."
docker exec equityscope-postgres pg_dump -U equityscope_user equityscope_db > "$BACKUP_DIR/$BACKUP_NAME/database.sql"

# Backup application data
echo "📁 Backing up application data..."
cp -r /opt/equityscope/data "$BACKUP_DIR/$BACKUP_NAME/"
cp -r /opt/equityscope/cache "$BACKUP_DIR/$BACKUP_NAME/"

# Create archive
echo "📦 Creating archive..."
cd "$BACKUP_DIR"
tar -czf "$BACKUP_NAME.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

# Upload to S3
echo "☁️  Uploading to S3..."
aws s3 cp "$BACKUP_NAME.tar.gz" "s3://$S3_BUCKET/$BACKUP_NAME.tar.gz"

# Clean up local backups older than retention period
echo "🧹 Cleaning up old backups..."
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "✅ Backup completed: $BACKUP_NAME.tar.gz"
```

### 2. Setup Automated Backups

```bash
# Add to crontab
echo "0 2 * * * /opt/equityscope/scripts/backup.sh >> /var/log/equityscope-backup.log 2>&1" | crontab -
```

### 3. Recovery Process

```bash
#!/bin/bash
# Recovery script

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

echo "🔄 Starting recovery from: $BACKUP_FILE"

# Stop services
docker-compose down

# Extract backup
tar -xzf "$BACKUP_FILE" -C /tmp/

# Restore database
echo "📊 Restoring database..."
docker-compose up -d postgres
sleep 30
docker exec -i equityscope-postgres psql -U equityscope_user -d equityscope_db < /tmp/equityscope_backup_*/database.sql

# Restore application data
echo "📁 Restoring application data..."
sudo rm -rf /opt/equityscope/data
sudo rm -rf /opt/equityscope/cache
sudo cp -r /tmp/equityscope_backup_*/data /opt/equityscope/
sudo cp -r /tmp/equityscope_backup_*/cache /opt/equityscope/
sudo chown -R docker:docker /opt/equityscope/

# Start all services
docker-compose up -d

echo "✅ Recovery completed!"
```

## Security Hardening

### 1. Server Security

```bash
#!/bin/bash
# Security hardening script

# Disable root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# Configure SSH key-only authentication
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# Restart SSH
sudo systemctl restart sshd

# Install fail2ban
sudo apt install -y fail2ban

# Configure fail2ban
sudo tee /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 1800
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log

[traefik-auth]
enabled = true
port = http,https
logpath = /opt/equityscope/logs/traefik.log
maxretry = 3
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Configure automatic security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 2. Application Security

- Enable HTTPS everywhere with HSTS
- Implement rate limiting at multiple levels
- Use secure headers via Traefik middleware
- Regular security updates and vulnerability scanning
- Database connection encryption
- API key rotation policies

## Performance Optimization

### 1. Database Optimization

```sql
-- PostgreSQL performance tuning
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.7;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
SELECT pg_reload_conf();

-- Create indexes
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_users_tier ON users(tier);
CREATE INDEX CONCURRENTLY idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX CONCURRENTLY idx_sessions_user_id ON sessions(user_id);
```

### 2. Caching Strategy

- Redis for session storage and API response caching
- CloudFlare CDN for static assets
- Browser caching headers via Traefik
- Database query result caching

### 3. Resource Limits

Update `docker-compose.yml` with resource limits:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  postgres:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

## Troubleshooting

### Common Issues

**1. SSL Certificate Issues**
```bash
# Check certificate status
docker-compose logs traefik | grep acme

# Manually request certificate
docker-compose exec traefik traefik acme --help
```

**2. Database Connection Issues**
```bash
# Check database status
docker-compose exec postgres pg_isready -U equityscope_user

# Check database logs
docker-compose logs postgres
```

**3. High Memory Usage**
```bash
# Monitor resource usage
docker stats

# Check application logs
docker-compose logs backend | tail -n 100
```

### Health Checks

```bash
#!/bin/bash
# Health check script

echo "🩺 EquityScope Health Check"

# Check services
services=("traefik" "backend" "frontend" "postgres" "redis")
for service in "${services[@]}"; do
    if docker-compose ps $service | grep -q "Up"; then
        echo "✅ $service: Running"
    else
        echo "❌ $service: Not running"
    fi
done

# Check API endpoints
if curl -f "https://${API_DOMAIN}/api/v2/health" > /dev/null 2>&1; then
    echo "✅ API Health: OK"
else
    echo "❌ API Health: Failed"
fi

# Check database
if docker-compose exec postgres pg_isready -U equityscope_user > /dev/null 2>&1; then
    echo "✅ Database: OK"
else
    echo "❌ Database: Failed"
fi

# Check disk space
df -h /opt/equityscope
```

## Maintenance

### Regular Maintenance Tasks

**Daily:**
- Automated backups
- Log rotation
- Health checks

**Weekly:**
- Security updates
- Performance monitoring review
- Database maintenance

**Monthly:**
- SSL certificate renewal (automatic)
- Backup retention cleanup
- Performance optimization review

### Update Process

```bash
#!/bin/bash
# Update process

# 1. Create maintenance window
echo "🔧 Starting maintenance window..."

# 2. Backup current state
./scripts/backup.sh

# 3. Pull updates
git pull origin main

# 4. Update containers
docker-compose pull
docker-compose up -d --force-recreate

# 5. Run migrations
docker-compose exec backend python scripts/migrate.py

# 6. Health check
./scripts/health-check.sh

echo "✅ Update completed!"
```

This comprehensive deployment guide covers all aspects of deploying EquityScope v2.0 to production, including security, monitoring, backups, and maintenance procedures.