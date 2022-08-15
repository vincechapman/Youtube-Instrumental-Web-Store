DROP TABLE IF EXISTS video;

CREATE TABLE video (
    id VARCHAR(20) PRIMARY KEY,
    title VARCHAR(101) NOT NULL,
    published_at VARCHAR(20) NOT NULL,
    thumbnail TEXT NOT NULL,
    description TEXT,
    beat_name VARCHAR(100),
    tags TEXT,
    mixdown_folder TEXT,
    stems_folder TEXT,
    link_to_video_audio TEXT);