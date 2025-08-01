# API Documentation - Enhanced Story System

## Overview
Hệ thống đã được mở rộng với các tính năng mới:
- Story Categories và Types
- Support System với file attachments
- Email Notifications
- Recruitment Flow

## Environment Variables
Thêm các biến môi trường sau vào file `.env`:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ADMIN_EMAIL=admin@example.com
FROM_EMAIL=noreply@example.com
```

## Story APIs

### Categories
- `POST /v1/story/categories/` - Tạo category mới (Admin only)
- `GET /v1/story/categories/` - Lấy danh sách categories
- `GET /v1/story/categories/{category_id}` - Lấy category theo ID

### Stories với Types và Categories
- `POST /v1/story/create` - Tạo story mới với email notifications
- `GET /v1/story/` - Lấy danh sách stories (Admin)
- `GET /v1/story/public/` - Lấy danh sách stories công khai
- `GET /v1/story/{slug}` - Lấy story theo slug (Admin)
- `GET /v1/story/public/{slug}` - Lấy story công khai theo slug

**Query Parameters:**
- `story_type`: article, report, recruitment
- `category_id`: ID của category
- `keyword`: Tìm kiếm theo từ khóa

## Support APIs

### Support Requests
- `POST /v1/support/` - Tạo support request mới
- `GET /v1/support/` - Lấy danh sách support requests
- `GET /v1/support/{support_id}` - Lấy support request theo ID
- `PUT /v1/support/{support_id}` - Cập nhật support request (Admin)
- `DELETE /v1/support/{support_id}` - Xóa support request (Admin)

### Recruitment Applications
- `POST /v1/support/recruitment/{story_id}` - Tạo đơn ứng tuyển cho story

### Source Tracking
- `GET /v1/support/source/{source_type}/{source_id}` - Lấy supports theo source

## Email Notifications

### Khi tạo Recruitment Story
- Gửi email thông báo cho admin khi có story type "recruitment" mới

### Khi submit Support Request
- Gửi email xác nhận cho user
- Nếu là recruitment application, gửi thông báo cho admin

## Database Schema

### Story Categories
```sql
CREATE TABLE story_categories (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(512),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Enhanced Stories
```sql
ALTER TABLE stories ADD COLUMN category_id BIGINT REFERENCES story_categories(id);
ALTER TABLE stories ADD COLUMN story_type VARCHAR(50) DEFAULT 'article';
```

### Support System
```sql
CREATE TABLE supports (
    id BIGINT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    support_type VARCHAR(50) NOT NULL,
    source_type VARCHAR(50),
    source_id BIGINT,
    user_id BIGINT NOT NULL REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE support_files (
    id BIGINT PRIMARY KEY,
    support_id BIGINT NOT NULL REFERENCES supports(id),
    file_id BIGINT NOT NULL REFERENCES files(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Usage Examples

### 1. Tạo Category
```bash
curl -X POST "http://localhost:8000/v1/story/categories/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tuyển dụng",
    "description": "Thông tin tuyển dụng và việc làm"
  }'
```

### 2. Tạo Recruitment Story
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

### 3. Submit Job Application
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

## Seeding Data
Chạy script để tạo categories mặc định:
```bash
python seed_categories.py
```

## Permissions
- **Admin**: Có thể tạo categories, quản lý tất cả supports
- **Story Manager**: Có thể tạo stories
- **User**: Có thể tạo support requests và xem supports của mình 