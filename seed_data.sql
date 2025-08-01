-- Seed Data for Enhanced Story System
-- Run this in Adminer or MySQL client

-- Insert users
INSERT INTO users (id, username, hashed_password, is_active, is_verified) VALUES
(1, 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4tbQJELp2O', 1, 1),
(2, 'story_manager', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4tbQJELp2O', 1, 1),
(3, 'user1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4tbQJELp2O', 1, 1),
(4, 'user2', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4tbQJELp2O', 1, 1),
(5, 'support_manager', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4tbQJELp2O', 1, 1);

-- Insert employees
INSERT INTO employees (id, user_id, first_name, last_name, email, phone_number, address, status) VALUES
(1, 1, 'Admin', 'User', 'admin@example.com', '0123456789', '123 Admin Street', 1),
(2, 2, 'Story', 'Manager', 'manager@example.com', '0123456790', '456 Manager Street', 1),
(3, 3, 'John', 'Doe', 'john.doe@example.com', '0123456791', '789 User Street', 1),
(4, 4, 'Jane', 'Smith', 'jane.smith@example.com', '0123456792', '321 User Street', 1),
(5, 5, 'Support', 'Manager', 'support@example.com', '0123456793', '654 Support Street', 1);

-- Insert roles
INSERT INTO roles (id, name, description) VALUES
(1, 'admin', 'Administrator role'),
(2, 'story_manager', 'Story manager role'),
(3, 'user', 'Regular user role'),
(4, 'support_manager', 'Support manager role');

-- Insert user roles
INSERT INTO user_roles (user_id, role_id) VALUES
(1, 1),  -- admin user has admin role
(2, 2),  -- story_manager user has story_manager role
(3, 3),  -- user1 has user role
(4, 3),  -- user2 has user role
(5, 4);  -- support_manager has support_manager role

-- Insert story categories
INSERT INTO story_categories (id, name, slug, description) VALUES
(1, 'Công nghệ', 'cong-nghe', 'Các bài viết về công nghệ'),
(2, 'Tuyển dụng', 'tuyen-dung', 'Thông tin tuyển dụng'),
(3, 'Báo cáo', 'bao-cao', 'Các báo cáo và nghiên cứu');

-- Insert stories
INSERT INTO stories (id, title, slug, content, author_id, category_id, story_type, published, created_at) VALUES
(1, 'Tuyển dụng Developer Python', 'tuyen-dung-developer-python', 'Chúng tôi đang tìm kiếm Developer Python có kinh nghiệm...', 2, 2, 'recruitment', 1, '2024-12-31 10:00:00'),
(2, 'Tuyển dụng Frontend Developer', 'tuyen-dung-frontend-developer', 'Cần Frontend Developer có kinh nghiệm React, TypeScript...', 2, 2, 'recruitment', 1, '2024-12-31 10:30:00'),
(3, 'Giới thiệu FastAPI', 'gioi-thieu-fastapi', 'FastAPI là một framework Python hiện đại...', 2, 1, 'article', 1, '2024-12-31 11:00:00'),
(4, 'Báo cáo thị trường IT 2024', 'bao-cao-thi-truong-it-2024', 'Thị trường IT Việt Nam năm 2024...', 2, 3, 'report', 1, '2024-12-31 11:30:00'),
(5, 'Hướng dẫn Docker cơ bản', 'huong-dan-docker-co-ban', 'Docker là công cụ containerization...', 2, 1, 'article', 1, '2024-12-31 12:00:00');

-- Insert files
INSERT INTO files (id, filename, file_url, content_type, file_extension, size, created_at) VALUES
(1, 'cv_john_doe.pdf', 'https://example.com/files/cv_john_doe.pdf', 'application/pdf', 'pdf', 1024000, '2024-12-31 10:00:00'),
(2, 'portfolio_jane_smith.pdf', 'https://example.com/files/portfolio_jane_smith.pdf', 'application/pdf', 'pdf', 2048000, '2024-12-31 10:30:00'),
(3, 'screenshot_error.png', 'https://example.com/files/screenshot_error.png', 'image/png', 'png', 512000, '2024-12-31 11:00:00');

-- Insert supports (updated schema with email instead of user_id)
INSERT INTO supports (id, title, content, email, support_type, source_type, source_id, file_ids, status, created_at) VALUES
(1, 'Ứng tuyển vị trí Developer Python', 'Tôi quan tâm đến vị trí Developer Python. Tôi có 3 năm kinh nghiệm với Python và Django. Mong được phản hồi sớm.', 'john.doe@example.com', 'recruitment', 'story', 1, '1', 'pending', '2024-12-31 10:00:00'),
(2, 'Hỏi về FastAPI deployment', 'Tôi đang gặp vấn đề khi deploy FastAPI lên server. Có thể tư vấn giúp tôi không?', 'jane.smith@example.com', 'technical', NULL, NULL, NULL, 'in_progress', '2024-12-31 10:30:00'),
(3, 'Ứng tuyển Frontend Developer', 'Tôi có 2 năm kinh nghiệm với React và TypeScript. Mong được tham gia team.', 'developer@example.com', 'recruitment', 'story', 2, '2', 'pending', '2024-12-31 11:00:00'),
(4, 'Báo lỗi hệ thống', 'Tôi không thể đăng nhập vào hệ thống. Hiển thị lỗi 500 Internal Server Error.', 'user@example.com', 'general', NULL, NULL, '3', 'pending', '2024-12-31 11:30:00'),
(5, 'Hỏi về API documentation', 'Tôi cần hướng dẫn sử dụng API. Có thể cung cấp thêm ví dụ không?', 'api_user@example.com', 'technical', NULL, NULL, NULL, 'resolved', '2024-12-31 12:00:00'); 