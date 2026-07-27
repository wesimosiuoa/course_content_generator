-- Assessment Tables for Course Management System
-- Quizzes at end of each lesson, SAQ at end of each module, Final exam on last module

-- 1. Quiz Questions (for lesson-end quizzes)
CREATE TABLE IF NOT EXISTS quiz_questions (
  `id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `course_id` INT(11) NOT NULL,
  `module_index` INT(11) NOT NULL,
  `lesson_index` INT(11) NOT NULL,
  `question_text` TEXT NOT NULL,
  `question_type` ENUM('multiple_choice', 'true_false', 'short_answer') DEFAULT 'multiple_choice',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
  INDEX `idx_lesson_quiz` (`course_id`, `module_index`, `lesson_index`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 2. Quiz Answer Options (for multiple choice questions)
CREATE TABLE IF NOT EXISTS quiz_answer_options (
  `id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `question_id` INT(11) NOT NULL,
  `option_text` TEXT NOT NULL,
  `is_correct` TINYINT(1) DEFAULT 0,
  `order_index` INT(11) DEFAULT 0,
  FOREIGN KEY (`question_id`) REFERENCES `quiz_questions`(`id`) ON DELETE CASCADE,
  INDEX `idx_question_options` (`question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 3. Student Quiz Responses
CREATE TABLE IF NOT EXISTS student_quiz_responses (
  `id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT(11) NOT NULL,
  `course_id` INT(11) NOT NULL,
  `module_index` INT(11) NOT NULL,
  `lesson_index` INT(11) NOT NULL,
  `question_id` INT(11) NOT NULL,
  `selected_option_id` INT(11),
  `short_answer_text` TEXT,
  `is_correct` TINYINT(1) DEFAULT 0,
  `score` DECIMAL(5,2) DEFAULT 0,
  `attempted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`question_id`) REFERENCES `quiz_questions`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`selected_option_id`) REFERENCES `quiz_answer_options`(`id`) ON DELETE SET NULL,
  INDEX `idx_student_quiz` (`user_id`, `course_id`, `module_index`, `lesson_index`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 4. Lesson Quiz Results (summary for each lesson)
CREATE TABLE IF NOT EXISTS lesson_quiz_results (
  `id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT(11) NOT NULL,
  `course_id` INT(11) NOT NULL,
  `module_index` INT(11) NOT NULL,
  `lesson_index` INT(11) NOT NULL,
  `total_questions` INT(11) DEFAULT 0,
  `correct_answers` INT(11) DEFAULT 0,
  `score_percentage` DECIMAL(5,2) DEFAULT 0,
  `passed` TINYINT(1) DEFAULT 0,
  `completed_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
  INDEX `idx_lesson_result` (`user_id`, `course_id`, `module_index`, `lesson_index`),
  UNIQUE KEY `unique_lesson_quiz` (`user_id`, `course_id`, `module_index`, `lesson_index`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 5. Short Answer Questions (module-end assessments)
CREATE TABLE IF NOT EXISTS short_answer_questions (
  `id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `course_id` INT(11) NOT NULL,
  `module_index` INT(11) NOT NULL,
  `question_text` TEXT NOT NULL,
  `question_type` ENUM('essay', 'short_answer') DEFAULT 'short_answer',
  `max_score` INT(11) DEFAULT 10,
  `rubric` JSON,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
  INDEX `idx_module_saq` (`course_id`, `module_index`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 6. Student Short Answer Responses
CREATE TABLE IF NOT EXISTS student_saq_responses (
  `id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT(11) NOT NULL,
  `course_id` INT(11) NOT NULL,
  `module_index` INT(11) NOT NULL,
  `saq_id` INT(11) NOT NULL,
  `answer_text` LONGTEXT NOT NULL,
  `score` DECIMAL(5,2) DEFAULT NULL,
  `feedback` TEXT,
  `is_graded` TINYINT(1) DEFAULT 0,
  `graded_by_user_id` INT(11),
  `submitted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `graded_at` TIMESTAMP NULL,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`saq_id`) REFERENCES `short_answer_questions`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`graded_by_user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
  INDEX `idx_student_saq` (`user_id`, `course_id`, `module_index`),
  UNIQUE KEY `unique_saq_submission` (`user_id`, `saq_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 7. Student SAQ Reevaluation Requests
CREATE TABLE IF NOT EXISTS saq_reevaluation_requests (
  `id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `response_id` INT(11) NOT NULL,
  `user_id` INT(11) NOT NULL,
  `reason` TEXT NOT NULL,
  `status` ENUM('pending', 'reviewed', 'declined') DEFAULT 'pending',
  `requested_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `reviewed_at` TIMESTAMP NULL,
  FOREIGN KEY (`response_id`) REFERENCES `student_saq_responses`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_reeval_response` (`response_id`),
  INDEX `idx_reeval_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 8. Module Assessment Results (summary for each module)
CREATE TABLE IF NOT EXISTS module_assessment_results (
  `id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT(11) NOT NULL,
  `course_id` INT(11) NOT NULL,
  `module_index` INT(11) NOT NULL,
  `quiz_score_percentage` DECIMAL(5,2) DEFAULT 0,
  `saq_score_percentage` DECIMAL(5,2) DEFAULT NULL,
  `module_score_percentage` DECIMAL(5,2) DEFAULT 0,
  `completed` TINYINT(1) DEFAULT 0,
  `completed_at` TIMESTAMP NULL,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
  INDEX `idx_module_assessment` (`user_id`, `course_id`, `module_index`),
  UNIQUE KEY `unique_module_assessment` (`user_id`, `course_id`, `module_index`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 8. Final Assessment (for last module)
CREATE TABLE IF NOT EXISTS final_assessments (
  `id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `course_id` INT(11) NOT NULL,
  `question_id` INT(11) NOT NULL,
  `question_text` TEXT NOT NULL,
  `max_score` INT(11) DEFAULT 10,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
  INDEX `idx_final_assessment` (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 9. Student Final Assessment Responses
CREATE TABLE IF NOT EXISTS student_final_responses (
  `id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT(11) NOT NULL,
  `course_id` INT(11) NOT NULL,
  `final_assessment_id` INT(11) NOT NULL,
  `answer_text` LONGTEXT NOT NULL,
  `score` DECIMAL(5,2) DEFAULT NULL,
  `feedback` TEXT,
  `is_graded` TINYINT(1) DEFAULT 0,
  `graded_by_user_id` INT(11),
  `submitted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `graded_at` TIMESTAMP NULL,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`final_assessment_id`) REFERENCES `final_assessments`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`graded_by_user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
  INDEX `idx_student_final` (`user_id`, `course_id`),
  UNIQUE KEY `unique_final_submission` (`user_id`, `final_assessment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 10. Course Final Grade and Certificate
CREATE TABLE IF NOT EXISTS course_completion_grades (
  `id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT(11) NOT NULL,
  `course_id` INT(11) NOT NULL,
  `module_assessments_avg` DECIMAL(5,2) DEFAULT 0,
  `final_assessment_score` DECIMAL(5,2) DEFAULT 0,
  `weighted_score` DECIMAL(5,2) DEFAULT 0,
  `final_grade` VARCHAR(2),
  `passed` TINYINT(1) DEFAULT 0,
  `certificate_issued` TINYINT(1) DEFAULT 0,
  `certificate_issued_date` TIMESTAMP NULL,
  `completed_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
  INDEX `idx_course_grade` (`user_id`, `course_id`),
  UNIQUE KEY `unique_course_grade` (`user_id`, `course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 11. Certificate Records
CREATE TABLE IF NOT EXISTS certificates (
  `id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT(11) NOT NULL,
  `course_id` INT(11) NOT NULL,
  `certificate_code` VARCHAR(50) UNIQUE NOT NULL,
  `issue_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `certificate_url` VARCHAR(500),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
  INDEX `idx_certificate` (`user_id`, `course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
