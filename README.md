# FastAPI Monolithic Backend

Dự án backend được xây dựng với FastAPI theo kiến trúc monolithic, tích hợp xác thực người dùng, phân quyền (RBAC), và các module quản lý `Employee`, `Role`, `Story`.

## Yêu cầu

*   [Docker](https://www.docker.com/products/docker-desktop/)
*   [Docker Compose](https://docs.docker.com/compose/install/)

## Cài đặt

1.  **Clone a repository:**

    ```bash
    git clone <your-repository-url>
    cd Backend-FastAPI-middlerware
    ```

2.  **Tạo file môi trường `.env`:**

    Tạo một file mới tên là `.env` ở thư mục gốc của dự án và sao chép nội dung dưới đây vào. Thay đổi các giá trị nếu cần thiết, đặc biệt là `SECRET_KEY`.

    ```env
    # App settings
    APP_NAME="FastAPI App"
    DEBUG=True
    ENABLE_SSL=False
    ENV="development"
    PROJECT_NAME="FastAPI Monolithic"
    API_V1_STR="/v1"

    # JWT settings
    SECRET_KEY="your-super-secret-key-change-me"
    ALGORITHM="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    REFRESH_TOKEN_EXPIRE_DAYS=7

    # Database settings (sử dụng giá trị từ docker-compose.yml)
    DB_HOST=db
    DB_PORT=3306
    DB_USER=user
    DB_PASSWORD=password
    DB_NAME=mydatabase

    # AWS S3 Settings (Tùy chọn - cho chức năng lưu trữ file)
    AWS_ACCESS_KEY_ID=""
    AWS_SECRET_ACCESS_KEY=""
    AWS_REGION_NAME=""
    AWS_S3_BUCKET_NAME=""
    ```

## Chạy ứng dụng

1.  **Khởi chạy với Docker Compose:**

    Mở terminal và chạy lệnh sau từ thư mục gốc của dự án:

    ```bash
    docker-compose up -d --build
    ```

    Lệnh này sẽ build image cho service `app` và khởi chạy các container cho ứng dụng FastAPI, database (MySQL), Redis, và Adminer.

2.  **Kiểm tra trạng thái các container:**

    ```bash
    docker-compose ps
    ```

## Tạo dữ liệu mẫu (Seeding)

Sau khi các container đã khởi chạy, bạn có thể thêm dữ liệu mẫu (người dùng, vai trò, truyện) vào database bằng cách chạy lệnh sau:

```bash
docker-compose exec app python seed_all.py
```

Lệnh này sẽ thực thi script `seed_all.py` bên trong container `app`.

## Các dịch vụ

*   **API Endpoint:** `http://localhost:8000`
*   **API Docs (Swagger UI):** `http://localhost:8000/docs`
*   **Adminer (Quản lý Database):** `http://localhost:8080`
    *   **System:** `MySQL`
    *   **Server:** `db` (tên service trong `docker-compose.yml`)
    *   **Username:** `user`
    *   **Password:** `password`
    *   **Database:** `mydatabase`

## Cấu trúc thư mục

```
.
├── core/               # Các module lõi (auth, config, db, middleware)
├── employee/           # Module quản lý nhân viên
├── file_storage/       # Module quản lý file
├── role/               # Module quản lý vai trò (RBAC)
├── story/              # Module quản lý truyện
├── users/              # Module quản lý người dùng
├── certs/              # Chứng chỉ SSL (nếu có)
├── main.py             # Entrypoint của ứng dụng FastAPI
├── seed_all.py         # Script tạo dữ liệu mẫu
├── requirements.txt    # Danh sách các thư viện Python
├── Dockerfile          # Cấu hình build Docker image cho app
└── docker-compose.yml  # Cấu hình các services (app, db, redis, adminer)
```
