# Enhanced Story System - FastAPI Backend

## 🚀 Overview

Hệ thống đã được mở rộng với các tính năng mới:
- ✅ **Story Categories và Types** (article, report, recruitment)
- ✅ **Support System** với file attachments và source tracking
- ✅ **Email Notifications** cho recruitment workflow
- ✅ **File Storage & CDN** với thumbnail generation
- ✅ **Image Processing** với Pillow integration
- ✅ **Database Schema** được cập nhật với relationships
- ✅ **API Documentation** đầy đủ

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Story System  │    │  Support System │    │  Email Service  │
│                 │    │                 │    │                 │
│ • Categories    │    │ • File Attach   │    │ • SMTP Config   │
│ • Types         │    │ • Source Track  │    │ • Notifications │
│ • Recruitment   │    │ • Status Mgmt   │    │ • Confirmations │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Database      │
                    │                 │
                    │ • MySQL 8.0     │
                    │ • Redis Cache   │
                    │ • File Storage  │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  CDN/Thumbnail  │
                    │                 │
                    │ • Image Resize  │
                    │ • Format Conv   │
                    │ • S3 Storage    │
                    │ • Cache Layer   │
                    └─────────────────┘
```

## 🛠️ Setup & Installation

### 1. Environment Variables
Tạo file `.env` với các biến sau:

```env
# App Settings
APP_NAME=Enhanced Story System
DEBUG=true
ENABLE_SSL=false
ENV=development

# Database
DB_HOST=db
DB_PORT=3306
DB_USER=user
DB_PASSWORD=password
DB_NAME=users_db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AWS S3 (Optional)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION_NAME=us-east-1
AWS_S3_BUCKET_NAME=your-bucket

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ADMIN_EMAIL=admin@example.com
FROM_EMAIL=noreply@example.com
```

### 2. Start Services
```bash
# Build with new dependencies (first time)
docker-compose build --no-cache

# Start all services
docker-compose up -d

# Check status
docker ps

# View logs
docker logs backend-fastapi-middlerware-app-1
```

**Note:** First build sẽ mất thời gian hơn do cài đặt Pillow và system dependencies.

### 3. Database Migration
```bash
# Create thumbnails table (if not exists)
docker exec -it backend-fastapi-middlerware-db-1 mysql -u user -ppassword users_db < create_thumbnails_table.sql

# Or run SQL manually in Adminer (http://localhost:8080)
```

### 4. Seed Data
```bash
# Seed categories
docker exec -it backend-fastapi-middlerware-app-1 python seed_categories_minimal.py
```

## 📊 Database Schema

### Story Categories
```sql
CREATE TABLE story_categories (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(512),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Enhanced Stories
```sql
CREATE TABLE stories (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) UNIQUE NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description VARCHAR(512),
    content TEXT NOT NULL,
    tags VARCHAR(255),
    published BOOLEAN DEFAULT FALSE,
    author_id BIGINT NOT NULL,
    category_id BIGINT,
    story_type VARCHAR(50) DEFAULT 'article',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id),
    FOREIGN KEY (category_id) REFERENCES story_categories(id)
);
```

### Support System
```sql
CREATE TABLE supports (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    support_type VARCHAR(50) NOT NULL,
    source_type VARCHAR(50),
    source_id BIGINT,
    user_id BIGINT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE support_files (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    support_id BIGINT NOT NULL,
    file_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (support_id) REFERENCES supports(id),
    FOREIGN KEY (file_id) REFERENCES files(id)
);
```

### File Storage & Thumbnails
```sql
-- Files table
CREATE TABLE files (
    id INT PRIMARY KEY AUTO_INCREMENT,
    filename VARCHAR(255),
    file_url VARCHAR(512) NOT NULL,
    content_type VARCHAR(100),
    file_extension VARCHAR(20),
    size FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Thumbnails table
CREATE TABLE thumbnails (
    id INT PRIMARY KEY AUTO_INCREMENT,
    original_file_id INT NOT NULL,
    width INT NOT NULL,
    height INT NOT NULL,
    quality INT DEFAULT 80,
    format VARCHAR(10) DEFAULT 'webp',
    file_url VARCHAR(512) NOT NULL,
    file_size FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP,
    access_count INT DEFAULT 0,
    FOREIGN KEY (original_file_id) REFERENCES files(id) ON DELETE CASCADE,
    UNIQUE KEY unique_thumbnail (original_file_id, width, height, format, quality)
);
```

## 🖼️ File Storage & CDN System

### Features
- ✅ **File Upload** - Support multiple formats (images, PDFs, etc.)
- ✅ **S3 Integration** - Scalable cloud storage
- ✅ **Image Processing** - Auto resize, format conversion
- ✅ **Thumbnail Generation** - On-demand with caching
- ✅ **CDN URLs** - Clean, branded URLs
- ✅ **Performance** - Lazy loading, database caching

### Thumbnail Sizes
Khi upload ảnh, system auto-generate các size phổ biến:
- **150x150** - Small thumbnail
- **300x300** - Medium thumbnail
- **600x600** - Large thumbnail
- **800x600** - Landscape format

### Usage Examples

#### Upload File
```bash
POST /v1/files/public-upload
Content-Type: multipart/form-data

# Response includes thumbnail URLs
{
  "id": 8,
  "filename": "template_141.png",
  "file_url": "https://bucket.s3.region.amazonaws.com/uploads/uuid.png",
  "content_type": "image/png",
  "thumbnails": [
    {
      "width": 150,
      "height": 150,
      "url": "http://localhost:8000/v1/files/thumbnail/8?w=150&h=150"
    },
    {
      "width": 300,
      "height": 300,
      "url": "http://localhost:8000/v1/files/thumbnail/8?w=300&h=300"
    }
  ]
}
```

#### Get Thumbnail
```bash
# Redirect to optimized image
GET /v1/files/thumbnail/8?w=400&h=400&format=webp&q=80

# Get thumbnail info
GET /v1/files/thumbnail/8/info?w=400&h=400

# List all thumbnails for file
GET /v1/files/thumbnail/8/list
```

#### Supported Parameters
- **w, h** - Width, height (50-2000px)
- **format** - webp, jpg, png (default: webp)
- **q** - Quality 10-100 (default: 80)

### CDN Benefits
1. **Performance** - Cached thumbnails, optimized formats
2. **Bandwidth** - Serve exact size needed
3. **SEO** - Clean URLs, proper headers
4. **Security** - Hide S3 structure, access control
5. **Analytics** - Track usage patterns

## 🔌 API Endpoints

### Story APIs
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/v1/story/categories/` | List categories | No |
| POST | `/v1/story/categories/` | Create category | Admin |
| GET | `/v1/story/public/` | List public stories | No |
| POST | `/v1/story/create` | Create story | Story Manager |
| GET | `/v1/story/public/{slug}` | Get public story | No |

### Support APIs
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/v1/support/` | Create support request | User |
| GET | `/v1/support/` | List support requests | User |
| POST | `/v1/support/recruitment/{story_id}` | Submit job application | User |
| GET | `/v1/support/source/{type}/{id}` | Get supports by source | Admin |

### File Storage APIs
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/v1/files/upload` | Upload file | Yes |
| POST | `/v1/files/public-upload` | Upload file (public) | No |
| GET | `/v1/files/` | List files | Yes |
| GET | `/v1/files/public/` | List public images | No |
| GET | `/v1/files/{file_id}` | Get file info | Yes |
| GET | `/v1/files/public/{file_id}` | Get public file info | No |

### Thumbnail APIs  
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/v1/files/thumbnail/{file_id}` | Get thumbnail (redirect) | No |
| GET | `/v1/files/thumbnail/{file_id}/info` | Get thumbnail info | No |
| GET | `/v1/files/thumbnail/{file_id}/list` | List file thumbnails | Yes |
| GET | `/v1/files/public/thumbnail/{file_id}` | Public thumbnail | No |

### Query Parameters
- `story_type`: article, report, recruitment
- `category_id`: ID của category
- `keyword`: Tìm kiếm theo từ khóa
- `support_type`: general, recruitment, technical
- `status`: pending, in_progress, resolved
- `w, h`: Thumbnail width, height (50-2000px)
- `format`: webp, jpg, png (default: webp)
- `q`: Quality 10-100 (default: 80)

## 📧 Email Notifications

### Workflow
1. **Recruitment Story Created** → Email thông báo cho admin
2. **Job Application Submitted** → Email xác nhận cho user + thông báo cho admin
3. **Support Request Created** → Email xác nhận cho user

### Email Types
- `send_notification_email()`: Thông báo chung
- `send_confirmation_email()`: Xác nhận support request
- `send_recruitment_notification()`: Thông báo recruitment story mới
- `send_job_application_notification()`: Thông báo job application

## 🧪 Testing

### 1. Test API Workflow
```bash
python test_workflow.py
```

### 2. Test Email Notifications
```bash
docker exec -it backend-fastapi-middlerware-app-1 python test_email.py
```

### 3. Manual Testing
```bash
# Test categories
curl http://localhost:8000/v1/story/categories/

# Test stories
curl http://localhost:8000/v1/story/public/

# Test support (requires auth)
curl http://localhost:8000/v1/support/
```

## 🔍 Monitoring & Debugging

### 1. View API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 2. Database Management
- **Adminer**: http://localhost:8080
  - Server: `db`
  - Username: `user`
  - Password: `password`
  - Database: `users_db`

### 3. Container Logs
```bash
# App logs
docker logs backend-fastapi-middlerware-app-1

# Database logs
docker logs backend-fastapi-middlerware-db-1

# Redis logs
docker logs backend-fastapi-middlerware-redis-1
```

## 📈 Usage Examples

### 1. Create Recruitment Story
```bash
curl -X POST "http://localhost:8000/v1/story/create" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tuyển dụng Developer Python",
    "description": "Cần tuyển developer Python có kinh nghiệm",
    "content": "Chi tiết công việc...",
    "story_type": "recruitment",
    "category_id": 3,
    "published": true
  }'
```

### 2. Submit Job Application
```bash
curl -X POST "http://localhost:8000/v1/support/recruitment/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ứng tuyển vị trí Developer Python",
    "content": "Tôi quan tâm đến vị trí này...",
    "support_type": "recruitment",
    "file_ids": [1, 2]
  }'
```

## 🔐 Permissions

| Role | Permissions |
|------|-------------|
| **Admin** | Tạo categories, quản lý tất cả supports |
| **Story Manager** | Tạo stories |
| **User** | Tạo support requests, xem supports của mình |

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG=false`
- [ ] Configure production database
- [ ] Set up proper email credentials
- [ ] Configure CORS properly
- [ ] Set up SSL certificates
- [ ] Configure logging
- [ ] Set up monitoring

### Docker Commands
```bash
# Build and start
docker-compose up -d --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f app

# Restart specific service
docker-compose restart app
```

## 📝 Changelog

### v2.0.0 - Enhanced Story System
- ✅ Added Story Categories and Types
- ✅ Implemented Support System with file attachments
- ✅ Added Email Notifications
- ✅ Created Recruitment Workflow
- ✅ Enhanced Database Schema
- ✅ Added API Documentation
- ✅ Implemented Source Tracking
- ✅ Added File Management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. 