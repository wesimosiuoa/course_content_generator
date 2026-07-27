-- Learning System Database Implementation
-- Generated from ERD Diagram

CREATE DATABASE IF NOT EXISTS learning_system_db;
USE learning_system_db;

-- USER Table
CREATE TABLE IF NOT EXISTS USER (
    userId VARCHAR(50) PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    passwordHash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
);

-- COURSE Table
CREATE TABLE IF NOT EXISTS COURSE (
    courseId VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    difficultyLevel ENUM('Beginner', 'Intermediate', 'Advanced', 'Expert') NOT NULL,
    estimatedHours INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_difficulty (difficultyLevel),
    INDEX idx_title (title)
);

-- LEARNERPROFILE Table
CREATE TABLE IF NOT EXISTS LEARNERPROFILE (
    profileId VARCHAR(50) PRIMARY KEY,
    userId VARCHAR(50) NOT NULL UNIQUE,
    skillLevel ENUM('Beginner', 'Intermediate', 'Advanced', 'Expert') DEFAULT 'Beginner',
    learningGoals TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_learnerprofile_user
        FOREIGN KEY (userId)
        REFERENCES USER(userId)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX idx_user_profile (userId)
);

-- Junction table for LEARNERPROFILE - COURSE (completed courses)
CREATE TABLE IF NOT EXISTS COMPLETED_COURSES (
    profileId VARCHAR(50) NOT NULL,
    courseId VARCHAR(50) NOT NULL,
    completion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    grade DECIMAL(5,2),
    feedback TEXT,
    PRIMARY KEY (profileId, courseId),
    CONSTRAINT fk_completed_profile
        FOREIGN KEY (profileId)
        REFERENCES LEARNERPROFILE(profileId)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_completed_course
        FOREIGN KEY (courseId)
        REFERENCES COURSE(courseId)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX idx_completion_date (completion_date)
);

-- SEARCHBEHAVIOR Table
CREATE TABLE IF NOT EXISTS SEARCHBEHAVIOR (
    searchId VARCHAR(50) PRIMARY KEY,
    profileId VARCHAR(50) NOT NULL,
    searchHistory TEXT,
    preferredFormat ENUM('Video', 'Text', 'Interactive', 'Mixed') DEFAULT 'Mixed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_searched TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_searchbehavior_profile
        FOREIGN KEY (profileId)
        REFERENCES LEARNERPROFILE(profileId)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX idx_profile_search (profileId)
);

-- COURSEOUTLINE Table
CREATE TABLE IF NOT EXISTS COURSEOUTLINE (
    outlineId VARCHAR(50) PRIMARY KEY,
    courseId VARCHAR(50) NOT NULL UNIQUE,
    learningObjectives JSON,
    prerequisites TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_courseoutline_course
        FOREIGN KEY (courseId)
        REFERENCES COURSE(courseId)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- LEARNINGMATERIAL Table (Supertype)
CREATE TABLE IF NOT EXISTS LEARNINGMATERIAL (
    materialId VARCHAR(50) PRIMARY KEY,
    courseId VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    contentType ENUM('Notes', 'PPTX', 'Video', 'Assessment') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_material_course
        FOREIGN KEY (courseId)
        REFERENCES COURSE(courseId)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX idx_course_material (courseId),
    INDEX idx_content_type (contentType)
);

-- NOTES Table (Subtype)
CREATE TABLE IF NOT EXISTS NOTES (
    materialId VARCHAR(50) PRIMARY KEY,
    content LONGTEXT NOT NULL,
    format ENUM('Markdown', 'PDF', 'DOCX', 'PlainText') DEFAULT 'PlainText',
    word_count INT DEFAULT 0,
    CONSTRAINT fk_notes_material
        FOREIGN KEY (materialId)
        REFERENCES LEARNINGMATERIAL(materialId)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- PPTX Table (Subtype)
CREATE TABLE IF NOT EXISTS PPTX (
    materialId VARCHAR(50) PRIMARY KEY,
    slideCount INT DEFAULT 0,
    slides JSON,
    file_size BIGINT,
    CONSTRAINT fk_pptx_material
        FOREIGN KEY (materialId)
        REFERENCES LEARNINGMATERIAL(materialId)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX idx_slide_count (slideCount)
);

-- VIDEO Table (Subtype)
CREATE TABLE IF NOT EXISTS VIDEO (
    materialId VARCHAR(50) PRIMARY KEY,
    scriptContent LONGTEXT,
    duration INT DEFAULT 0, -- in seconds
    scenes JSON,
    video_url VARCHAR(500),
    CONSTRAINT fk_video_material
        FOREIGN KEY (materialId)
        REFERENCES LEARNINGMATERIAL(materialId)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX idx_duration (duration)
);

-- ASSESSMENT Table (Subtype)
CREATE TABLE IF NOT EXISTS ASSESSMENT (
    materialId VARCHAR(50) PRIMARY KEY,
    questions JSON,
    passing_score INT DEFAULT 70,
    time_limit INT, -- in minutes
    max_attempts INT DEFAULT 3,
    CONSTRAINT fk_assessment_material
        FOREIGN KEY (materialId)
        REFERENCES LEARNINGMATERIAL(materialId)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- LLMSERVICE Table
CREATE TABLE IF NOT EXISTS LLMSERVICE (
    serviceId VARCHAR(50) PRIMARY KEY,
    apiKey VARCHAR(255) NOT NULL,
    model VARCHAR(100) NOT NULL,
    provider ENUM('OpenAI', 'Claude', 'Gemini', 'Custom') DEFAULT 'OpenAI',
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INT DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_provider (provider)
);

-- DATABASEMANAGER Table
CREATE TABLE IF NOT EXISTS DATABASEMANAGER (
    managerId VARCHAR(50) PRIMARY KEY,
    connectionString VARCHAR(500) NOT NULL,
    db_type ENUM('MySQL', 'PostgreSQL', 'MongoDB', 'SQLite') DEFAULT 'MySQL',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- CONTENTGENERATOR Table
CREATE TABLE IF NOT EXISTS CONTENTGENERATOR (
    generatorId VARCHAR(50) PRIMARY KEY,
    llmServiceId VARCHAR(50) NOT NULL,
    generator_name VARCHAR(100),
    version VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_generator_llm
        FOREIGN KEY (llmServiceId)
        REFERENCES LLMSERVICE(serviceId)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX idx_generator_active (is_active)
);

-- RETRIEVERSERVICE Table
CREATE TABLE IF NOT EXISTS RETRIEVERSERVICE (
    serviceId VARCHAR(50) PRIMARY KEY,
    dbManagerId VARCHAR(50) NOT NULL,
    service_name VARCHAR(100),
    retrieval_method ENUM('Keyword', 'Semantic', 'Hybrid') DEFAULT 'Keyword',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_retriever_dbmanager
        FOREIGN KEY (dbManagerId)
        REFERENCES DATABASEMANAGER(managerId)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX idx_retriever_active (is_active)
);

-- Create triggers for subtype consistency
DELIMITER $$

CREATE TRIGGER before_notes_insert
BEFORE INSERT ON NOTES
FOR EACH ROW
BEGIN
    DECLARE material_type VARCHAR(20);
    SELECT contentType INTO material_type 
    FROM LEARNINGMATERIAL 
    WHERE materialId = NEW.materialId;
    
    IF material_type != 'Notes' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Material type must be Notes for NOTES table';
    END IF;
END$$

CREATE TRIGGER before_pptx_insert
BEFORE INSERT ON PPTX
FOR EACH ROW
BEGIN
    DECLARE material_type VARCHAR(20);
    SELECT contentType INTO material_type 
    FROM LEARNINGMATERIAL 
    WHERE materialId = NEW.materialId;
    
    IF material_type != 'PPTX' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Material type must be PPTX for PPTX table';
    END IF;
END$$

CREATE TRIGGER before_video_insert
BEFORE INSERT ON VIDEO
FOR EACH ROW
BEGIN
    DECLARE material_type VARCHAR(20);
    SELECT contentType INTO material_type 
    FROM LEARNINGMATERIAL 
    WHERE materialId = NEW.materialId;
    
    IF material_type != 'Video' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Material type must be Video for VIDEO table';
    END IF;
END$$

CREATE TRIGGER before_assessment_insert
BEFORE INSERT ON ASSESSMENT
FOR EACH ROW
BEGIN
    DECLARE material_type VARCHAR(20);
    SELECT contentType INTO material_type 
    FROM LEARNINGMATERIAL 
    WHERE materialId = NEW.materialId;
    
    IF material_type != 'Assessment' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Material type must be Assessment for ASSESSMENT table';
    END IF;
END$$

DELIMITER ;

-- Create indexes for better performance
CREATE INDEX idx_learningmaterial_created ON LEARNINGMATERIAL(created_at);
CREATE INDEX idx_user_created ON USER(created_at);
CREATE INDEX idx_course_created ON COURSE(created_at);
CREATE INDEX idx_searchbehavior_last_searched ON SEARCHBEHAVIOR(last_searched);

-- Create view for course progress tracking
CREATE VIEW CourseProgress AS
SELECT 
    lp.profileId,
    lp.userId,
    c.courseId,
    c.title,
    c.difficultyLevel,
    cc.completion_date,
    cc.grade,
    CASE 
        WHEN cc.courseId IS NOT NULL THEN 'Completed'
        ELSE 'In Progress'
    END as status
FROM LEARNERPROFILE lp
CROSS JOIN COURSE c
LEFT JOIN COMPLETED_COURSES cc ON lp.profileId = cc.profileId AND c.courseId = cc.courseId;

-- Create view for user learning summary
CREATE VIEW UserLearningSummary AS
SELECT 
    u.userId,
    u.username,
    u.email,
    lp.profileId,
    lp.skillLevel,
    COUNT(DISTINCT cc.courseId) as completed_courses_count,
    SUM(c.estimatedHours) as total_learning_hours,
    GROUP_CONCAT(DISTINCT c.difficultyLevel SEPARATOR ', ') as attempted_levels,
    MAX(cc.completion_date) as last_completion_date
FROM USER u
JOIN LEARNERPROFILE lp ON u.userId = lp.userId
LEFT JOIN COMPLETED_COURSES cc ON lp.profileId = cc.profileId
LEFT JOIN COURSE c ON cc.courseId = c.courseId
GROUP BY u.userId, u.username, u.email, lp.profileId, lp.skillLevel;

-- Insert sample data for demonstration
INSERT INTO USER (userId, username, email, passwordHash) VALUES
('user001', 'john_doe', 'john@example.com', 'hashed_password_123'),
('user002', 'jane_smith', 'jane@example.com', 'hashed_password_456');

INSERT INTO LEARNERPROFILE (profileId, userId, skillLevel, learningGoals) VALUES
('profile001', 'user001', 'Beginner', '["Learn Python", "Master Data Analysis", "Build Web Apps"]'),
('profile002', 'user002', 'Intermediate', '["Advanced ML", "Deep Learning", "AI Ethics"]');

INSERT INTO COURSE (courseId, title, description, difficultyLevel, estimatedHours) VALUES
('course001', 'Python Basics', 'Introduction to Python programming', 'Beginner', 20),
('course002', 'Data Science 101', 'Fundamentals of data science', 'Intermediate', 40),
('course003', 'Machine Learning', 'Introduction to ML algorithms', 'Advanced', 60);

INSERT INTO COMPLETED_COURSES (profileId, courseId, grade) VALUES
('profile001', 'course001', 85.5),
('profile002', 'course002', 92.0);

-- Display table creation summary
SELECT 
    table_name,
    table_rows as 'Rows',
    round(((data_length + index_length) / 1024 / 1024), 2) as 'Size (MB)'
FROM information_schema.TABLES 
WHERE table_schema = 'learning_system_db'
ORDER BY table_name;