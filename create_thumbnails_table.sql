-- Migration script to create thumbnails table
-- Run this SQL script on your database to create the thumbnails table

CREATE TABLE IF NOT EXISTS thumbnails (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_file_id INT NOT NULL,
    width INT NOT NULL,
    height INT NOT NULL,
    quality INT DEFAULT 80,
    format VARCHAR(10) DEFAULT 'webp',
    file_url VARCHAR(512) NOT NULL,
    file_size FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP NULL,
    access_count INT DEFAULT 0,
    
    -- Foreign key constraint
    CONSTRAINT fk_thumbnails_original_file 
        FOREIGN KEY (original_file_id) REFERENCES files(id) ON DELETE CASCADE,
    
    -- Unique constraint to prevent duplicate thumbnails
    CONSTRAINT unique_thumbnail 
        UNIQUE (original_file_id, width, height, format, quality),
    
    -- Index for fast lookups
    INDEX idx_thumbnail_lookup (original_file_id, width, height, format, quality)
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_thumbnails_access_stats ON thumbnails(last_accessed, access_count);
CREATE INDEX IF NOT EXISTS idx_thumbnails_created_at ON thumbnails(created_at);
