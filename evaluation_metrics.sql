-- Evaluation metrics tables for AICG admin performance dashboard
-- Database: aicg

CREATE TABLE IF NOT EXISTS generation_logs (
  id INT(11) NOT NULL AUTO_INCREMENT,
  user_id INT(11) DEFAULT NULL,
  generation_type VARCHAR(32) NOT NULL,
  duration_ms INT(11) NOT NULL,
  success TINYINT(1) NOT NULL DEFAULT 1,
  meta_json TEXT DEFAULT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_generation_type (generation_type),
  KEY idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sus_responses (
  id INT(11) NOT NULL AUTO_INCREMENT,
  user_id INT(11) NOT NULL,
  q1 TINYINT NOT NULL,
  q2 TINYINT NOT NULL,
  q3 TINYINT NOT NULL,
  q4 TINYINT NOT NULL,
  q5 TINYINT NOT NULL,
  q6 TINYINT NOT NULL,
  q7 TINYINT NOT NULL,
  q8 TINYINT NOT NULL,
  q9 TINYINT NOT NULL,
  q10 TINYINT NOT NULL,
  sus_score DECIMAL(5,2) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_sus_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS manual_evaluations (
  id INT(11) NOT NULL AUTO_INCREMENT,
  course_id INT(11) DEFAULT NULL,
  evaluator_id INT(11) DEFAULT NULL,
  metric_name VARCHAR(64) NOT NULL,
  score DECIMAL(6,2) NOT NULL,
  max_score DECIMAL(6,2) NOT NULL DEFAULT 5.00,
  notes TEXT DEFAULT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_manual_metric (metric_name),
  KEY idx_manual_course (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
