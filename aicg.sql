-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 17, 2026 at 08:00 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `aicg`
--

-- --------------------------------------------------------

--
-- Table structure for table `certificates`
--

CREATE TABLE `certificates` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `certificate_code` varchar(50) NOT NULL,
  `issue_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `certificate_url` varchar(500) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `courses`
--

CREATE TABLE `courses` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `content` longtext NOT NULL,
  `content_hash` varchar(64) DEFAULT NULL,
  `generated_from_preferences` text DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `is_public` tinyint(1) DEFAULT 1,
  `popularity_score` int(11) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `courses`
--

INSERT INTO `courses` (`id`, `title`, `description`, `content`, `content_hash`, `generated_from_preferences`, `created_by`, `is_public`, `popularity_score`, `created_at`) VALUES
(1, 'Convolutional Neural Networks: Foundational Understanding', '', '{\"assessment\": \"Final project and quiz\", \"certification\": \"Certificate of Completion\", \"domain\": \"Artificial Intelligence\", \"duration\": 6, \"learning_outcomes\": [\"Understand the basics of convolutional neural networks\", \"Learn how to design and implement CNN architectures\", \"Apply CNNs to various computer vision tasks\", \"Analyze and evaluate the performance of CNN models\", \"Explore advanced topics in CNN research and development\"], \"level\": \"Advanced\", \"modules\": [{\"description\": \"Overview of CNN basics, history, and applications\", \"lessons\": [{\"summary\": \"Introduction to CNN concepts, including convolution, pooling, and activation functions\", \"title\": \"CNN Fundamentals\"}, {\"summary\": \"Overview of popular CNN architectures, including LeNet, AlexNet, and VGG\", \"title\": \"CNN Architectures\"}, {\"summary\": \"Discussion of CNN applications in computer vision, including image classification, object detection, and segmentation\", \"title\": \"CNN Applications\"}], \"title\": \"Introduction to CNNs\"}, {\"description\": \"Practical guide to designing and implementing CNNs\", \"lessons\": [{\"summary\": \"Best practices for designing effective CNN architectures\", \"title\": \"CNN Design Principles\"}, {\"summary\": \"Step-by-step guide to implementing CNNs using popular deep learning frameworks\", \"title\": \"CNN Implementation\"}, {\"summary\": \"Techniques for optimizing CNN performance, including regularization, dropout, and batch normalization\", \"title\": \"CNN Optimization\"}], \"title\": \"CNN Design and Implementation\"}, {\"description\": \"In-depth exploration of CNN applications in computer vision\", \"lessons\": [{\"summary\": \"Using CNNs for image classification tasks, including dataset preparation and model evaluation\", \"title\": \"Image Classification\"}, {\"summary\": \"Using CNNs for object detection tasks, including bounding box regression and non-maximum suppression\", \"title\": \"Object Detection\"}, {\"summary\": \"Using CNNs for image segmentation tasks, including semantic segmentation and instance segmentation\", \"title\": \"Image Segmentation\"}], \"title\": \"CNN Applications in Computer Vision\"}, {\"description\": \"Exploration of advanced topics in CNN research and development\", \"lessons\": [{\"summary\": \"Using pre-trained CNN models for transfer learning and fine-tuning\", \"title\": \"Transfer Learning\"}, {\"summary\": \"Introduction to attention mechanisms in CNNs, including self-attention and spatial attention\", \"title\": \"Attention Mechanisms\"}, {\"summary\": \"Techniques for explaining and interpreting CNN decisions, including saliency maps and feature importance\", \"title\": \"Explainability and Interpretability\"}], \"title\": \"Advanced Topics in CNNs\"}, {\"description\": \"Best practices for evaluating and deploying CNN models\", \"lessons\": [{\"summary\": \"Metrics and techniques for evaluating CNN performance, including accuracy, precision, and recall\", \"title\": \"Model Evaluation\"}, {\"summary\": \"Strategies for deploying CNN models in production environments, including model serving and monitoring\", \"title\": \"Model Deployment\"}, {\"summary\": \"Best practices for maintaining and updating CNN models over time, including model versioning and testing\", \"title\": \"Model Maintenance\"}], \"title\": \"CNN Evaluation and Deployment\"}], \"overview\": \"This course provides a comprehensive introduction to Convolutional Neural Networks (CNNs), covering the fundamental concepts, architectures, and applications of CNNs.\", \"prerequisites\": \"None\", \"resources\": [{\"author\": \"Ian Goodfellow, Yoshua Bengio, Aaron Courville\", \"title\": \"Deep Learning\", \"url\": \"https://www.deeplearningbook.org/\"}, {\"author\": \"Stanford University\", \"title\": \"Convolutional Neural Networks for Visual Recognition\", \"url\": \"https://cs231n.github.io/\"}, {\"author\": \"PyTorch Team\", \"title\": \"PyTorch Documentation\", \"url\": \"https://pytorch.org/docs/stable/index.html\"}, {\"author\": \"TensorFlow Team\", \"title\": \"TensorFlow Documentation\", \"url\": \"https://www.tensorflow.org/docs\"}, {\"author\": \"Keras Team\", \"title\": \"Keras Documentation\", \"url\": \"https://keras.io/\"}], \"target_audience\": \"Researchers, developers, and students interested in deep learning and computer vision\", \"title\": \"Convolutional Neural Networks: Foundational Understanding\"}', '065c17422efec6126a9a28d19131ea7dbdbfc9819c9b32fa6b96e1ab47637d4c', '{}', 1, 1, 1, '2026-04-01 20:01:33'),
(2, 'Advanced Communication Skills and Political Science', '', '{\"assessment\": \"Final research paper and presentation on a selected topic in political communication\", \"certification\": \"Advanced Certificate in Communication and Political Science\", \"domain\": \"Communication and Politics\", \"duration\": 6, \"learning_outcomes\": [\"Analyze the role of communication in political processes\", \"Evaluate the impact of political ideologies on communication strategies\", \"Develop effective communication plans for political campaigns\", \"Assess the influence of media on political discourse\", \"Apply theoretical frameworks to real-world political communication scenarios\"], \"level\": \"Advanced\", \"modules\": [{\"description\": \"Foundational concepts and theories in political communication\", \"lessons\": [{\"summary\": \"Overview of key terms and concepts in political communication\", \"title\": \"Defining Political Communication\"}, {\"summary\": \"In-depth examination of major theoretical frameworks\", \"title\": \"Theories of Political Communication\"}, {\"summary\": \"Evolution of political communication over time\", \"title\": \"Historical Development of Political Communication\"}], \"title\": \"Introduction to Political Communication\"}, {\"description\": \"Effective communication techniques for political campaigns and governance\", \"lessons\": [{\"summary\": \"Techniques for creating compelling political messages\", \"title\": \"Crafting Political Messages\"}, {\"summary\": \"Building and maintaining relationships with media outlets\", \"title\": \"Media Relations in Politics\"}, {\"summary\": \"Managing political crises through effective communication\", \"title\": \"Crisis Communication in Politics\"}], \"title\": \"Communication Strategies in Politics\"}, {\"description\": \"The impact of political ideologies on communication strategies\", \"lessons\": [{\"summary\": \"How liberal ideologies influence political communication\", \"title\": \"Liberalism and Communication\"}, {\"summary\": \"The impact of conservative ideologies on political messaging\", \"title\": \"Conservatism and Communication\"}, {\"summary\": \"Socialist ideologies and their implications for political communication\", \"title\": \"Socialism and Communication\"}], \"title\": \"Political Ideologies and Communication\"}, {\"description\": \"The role of media in shaping political discourse\", \"lessons\": [{\"summary\": \"How traditional media outlets shape political discourse\", \"title\": \"The Influence of Traditional Media\"}, {\"summary\": \"The role of social media in modern political communication\", \"title\": \"The Impact of Social Media\"}, {\"summary\": \"Understanding and addressing media bias in political communication\", \"title\": \"Media Bias and Political Communication\"}], \"title\": \"Media and Political Discourse\"}, {\"description\": \"Real-world applications of political communication theories and strategies\", \"lessons\": [{\"summary\": \"Analysis of effective communication strategies in political campaigns\", \"title\": \"Successful Political Campaigns\"}, {\"summary\": \"Case studies of political communication during national and international crises\", \"title\": \"Political Communication in Times of Crisis\"}, {\"summary\": \"Emerging trends and technologies in political communication\", \"title\": \"The Future of Political Communication\"}], \"title\": \"Case Studies in Political Communication\"}], \"overview\": \"This course provides a foundational understanding of communication skills and political science, focusing on theoretical aspects to enhance critical thinking and analytical skills.\", \"prerequisites\": \"None\", \"resources\": [{\"author\": \"David L. Swanson\", \"title\": \"Theories of Political Communication\", \"url\": \"https://www.routledge.com/Theories-of-Political-Communication/Swanson/p/book/9780415809114\"}, {\"author\": \"Kirsten A. Johnson\", \"title\": \"Political Communication: A New Introduction for Campaigns and Beyond\", \"url\": \"https://www.routledge.com/Political-Communication-A-New-Introduction-for-Campaigns-and-Beyond/Johnson/p/book/9781138285350\"}, {\"author\": \"Ingrid Volkmer\", \"title\": \"Media and Politics in a Globalizing World\", \"url\": \"https://www.politybooks.com/bookdetail/?isbn=9780745633543\"}, {\"author\": \"Kathleen Hall Jamieson and Kate Kenski\", \"title\": \"The Oxford Handbook of Political Communication\", \"url\": \"https://global.oup.com/academic/product/the-oxford-handbook-of-political-communication-9780199793362\"}, {\"author\": \"Adam Sheingate\", \"title\": \"Communication in Politics: Institutions, Interests, and Ideas\", \"url\": \"https://www.routledge.com/Communication-in-Politics-Institutions-Interests-and-Ideas/Sheingate/p/book/9780415834454\"}], \"target_audience\": \"Individuals seeking advanced knowledge in communication and political science\", \"title\": \"Advanced Communication Skills and Political Science\"}', 'db351a1db504cde2ab6223aa9e3fa7eca0e4a0910af85f120bb308b5bb4321fa', '{}', 2, 1, 1, '2026-04-09 07:06:44'),
(3, 'Crash Course for New Principal on Leadership Skills', '', '{\"assessment\": \"Final project presentation and written exam\", \"certification\": \"Certificate of Completion in Leadership Skills\", \"domain\": [], \"duration\": 6, \"learning_outcomes\": [\"Understand the fundamentals of leadership\", \"Develop effective communication skills\", \"Learn to build and manage high-performing teams\", \"Understand conflict resolution and management\", \"Develop strategic planning and decision-making skills\"], \"level\": \"Advanced\", \"modules\": [{\"description\": \"This module introduces the basics of leadership, including key concepts and theories.\", \"lessons\": [{\"summary\": \"This lesson defines leadership and its importance in organizations.\", \"title\": \"What is Leadership?\"}, {\"summary\": \"This lesson explores various leadership theories and their applications.\", \"title\": \"Leadership Theories\"}, {\"summary\": \"This lesson discusses different leadership styles and their effectiveness.\", \"title\": \"Leadership Styles\"}], \"title\": \"Introduction to Leadership\"}, {\"description\": \"This module focuses on developing effective communication skills for leaders.\", \"lessons\": [{\"summary\": \"This lesson covers the principles of effective verbal communication.\", \"title\": \"Verbal Communication\"}, {\"summary\": \"This lesson explores the importance of non-verbal communication in leadership.\", \"title\": \"Non-Verbal Communication\"}, {\"summary\": \"This lesson teaches leaders how to practice active listening.\", \"title\": \"Active Listening\"}], \"title\": \"Communication Skills\"}, {\"description\": \"This module teaches leaders how to build and manage high-performing teams.\", \"lessons\": [{\"summary\": \"This lesson discusses the importance of team dynamics in achieving organizational goals.\", \"title\": \"Team Dynamics\"}, {\"summary\": \"This lesson provides leaders with practical strategies for building effective teams.\", \"title\": \"Team Building Strategies\"}, {\"summary\": \"This lesson teaches leaders how to manage and resolve conflicts within teams.\", \"title\": \"Conflict Resolution\"}], \"title\": \"Team Building and Management\"}, {\"description\": \"This module focuses on developing strategic planning and decision-making skills for leaders.\", \"lessons\": [{\"summary\": \"This lesson introduces leaders to the principles of strategic planning.\", \"title\": \"Strategic Planning\"}, {\"summary\": \"This lesson explores various decision-making models and their applications.\", \"title\": \"Decision-Making Models\"}, {\"summary\": \"This lesson teaches leaders how to identify and manage risks in decision-making.\", \"title\": \"Risk Management\"}], \"title\": \"Strategic Planning and Decision-Making\"}, {\"description\": \"This module provides leaders with practical examples and case studies of leadership in action.\", \"lessons\": [{\"summary\": \"This lesson presents real-life case studies of effective leadership.\", \"title\": \"Case Studies in Leadership\"}, {\"summary\": \"This lesson explores how leadership skills can be applied in various contexts.\", \"title\": \"Leadership in Different Contexts\"}, {\"summary\": \"This lesson teaches leaders how to sustain their leadership momentum over time.\", \"title\": \"Sustaining Leadership Momentum\"}], \"title\": \"Leadership in Practice\"}], \"overview\": \"This course provides a foundational understanding of leadership skills for new principals, covering key concepts and theories to enhance their leadership abilities.\", \"prerequisites\": \"None\", \"resources\": [{\"author\": \"James M. Kouzes and Barry Z. Posner\", \"title\": \"The Leadership Challenge\", \"url\": \"https://www.amazon.com/Leadership-Challenge-James-M-Kouzes/dp/0470651727\"}, {\"author\": \"Patrick Lencioni\", \"title\": \"The Five Dysfunctions of a Team\", \"url\": \"https://www.amazon.com/Five-Dysfunctions-Team-Leadership-Fable/dp/0787960756\"}, {\"author\": \"Daniel H. Pink\", \"title\": \"Drive: The Surprising Truth About What Motivates Us\", \"url\": \"https://www.amazon.com/Drive-Surprising-Truth-About-Motivates/dp/1594484805\"}, {\"author\": \"Stephen Covey\", \"title\": \"The 7 Habits of Highly Effective People\", \"url\": \"https://www.amazon.com/Habits-Highly-Effective-People-Powerful/dp/0743269519\"}, {\"author\": \"Stanley McChrystal, Jeff Eggers, and Jay Mangone\", \"title\": \"Leaders: Myth and Reality\", \"url\": \"https://www.amazon.com/Leaders-Myth-Reality-Stanley-McChrystal/dp/0735216276\"}], \"target_audience\": \"New principals with no prior experience\", \"title\": \"Crash Course for New Principal on Leadership Skills\"}', '6eb6cd3dfba44e848edd947eb6d875a4dfc8262bb9577fdabbdcd3aa8ec5c91e', '{}', 2, 1, 1, '2026-04-16 10:44:15');

-- --------------------------------------------------------

--
-- Table structure for table `course_completion_grades`
--

CREATE TABLE `course_completion_grades` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `module_assessments_avg` decimal(5,2) DEFAULT 0.00,
  `final_assessment_score` decimal(5,2) DEFAULT 0.00,
  `weighted_score` decimal(5,2) DEFAULT 0.00,
  `final_grade` varchar(2) DEFAULT NULL,
  `passed` tinyint(1) DEFAULT 0,
  `certificate_issued` tinyint(1) DEFAULT 0,
  `certificate_issued_date` timestamp NULL DEFAULT NULL,
  `completed_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `course_feedback`
--

CREATE TABLE `course_feedback` (
  `id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `reaction` enum('like','dislike') NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `course_feedback`
--

INSERT INTO `course_feedback` (`id`, `course_id`, `user_id`, `reaction`, `created_at`) VALUES
(1, 1, 1, 'like', '2026-04-01 20:01:33'),
(2, 2, 2, 'like', '2026-04-09 07:06:44'),
(3, 3, 2, 'like', '2026-04-16 10:44:15');

-- --------------------------------------------------------

--
-- Table structure for table `enrollments`
--

CREATE TABLE `enrollments` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `progress` int(11) DEFAULT 0,
  `liked` tinyint(1) DEFAULT 0,
  `completed` tinyint(1) DEFAULT 0,
  `enrolled_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `last_accessed` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `enrollments`
--

INSERT INTO `enrollments` (`id`, `user_id`, `course_id`, `progress`, `liked`, `completed`, `enrolled_at`, `last_accessed`) VALUES
(1, 1, 1, 0, 0, 0, '2026-04-01 20:02:28', NULL),
(2, 2, 1, 0, 0, 0, '2026-04-09 07:02:55', NULL),
(3, 2, 2, 0, 0, 0, '2026-04-09 07:07:11', NULL),
(4, 2, 3, 0, 0, 0, '2026-04-16 10:48:24', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `final_assessments`
--

CREATE TABLE `final_assessments` (
  `id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  `question_text` text NOT NULL,
  `max_score` int(11) DEFAULT 10,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `lesson_quiz_results`
--

CREATE TABLE `lesson_quiz_results` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `module_index` int(11) NOT NULL,
  `lesson_index` int(11) NOT NULL,
  `total_questions` int(11) DEFAULT 0,
  `correct_answers` int(11) DEFAULT 0,
  `score_percentage` decimal(5,2) DEFAULT 0.00,
  `passed` tinyint(1) DEFAULT 0,
  `completed_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `lesson_quiz_results`
--

INSERT INTO `lesson_quiz_results` (`id`, `user_id`, `course_id`, `module_index`, `lesson_index`, `total_questions`, `correct_answers`, `score_percentage`, `passed`, `completed_at`) VALUES
(1, 1, 1, 0, 0, 21, 5, 23.81, 0, '2026-04-08 17:21:32'),
(2, 1, 1, 0, 1, 3, 3, 100.00, 1, '2026-04-09 05:56:24'),
(3, 1, 1, 0, 2, 4, 4, 100.00, 1, '2026-04-09 06:09:20'),
(4, 2, 2, 0, 0, 4, 1, 100.00, 0, '2026-04-09 07:09:06'),
(5, 2, 2, 0, 1, 4, 0, 100.00, 0, '2026-04-09 07:10:59'),
(6, 2, 2, 0, 2, 4, 0, 100.00, 0, '2026-04-09 07:12:57'),
(7, 2, 1, 0, 0, 22, 5, 22.73, 0, '2026-04-09 09:33:38'),
(8, 2, 2, 1, 0, 4, 0, 100.00, 0, '2026-04-11 05:38:14'),
(9, 2, 2, 1, 1, 4, 0, 100.00, 0, '2026-04-11 05:34:24'),
(10, 2, 2, 1, 2, 6, 1, 100.00, 0, '2026-04-11 05:40:14'),
(11, 2, 2, 2, 0, 4, 0, 100.00, 0, '2026-04-11 05:43:13'),
(12, 2, 2, 2, 1, 8, 0, 100.00, 0, '2026-04-11 05:46:13'),
(13, 2, 2, 2, 2, 4, 0, 100.00, 0, '2026-04-11 05:48:12'),
(14, 2, 2, 3, 0, 8, 2, 100.00, 0, '2026-04-11 05:51:19'),
(15, 2, 2, 3, 1, 4, 1, 100.00, 0, '2026-04-11 05:53:06'),
(16, 2, 2, 3, 2, 7, 0, 100.00, 0, '2026-04-11 05:56:31'),
(17, 2, 2, 4, 0, 7, 3, 100.00, 0, '2026-04-11 06:00:11'),
(18, 2, 2, 4, 1, 7, 0, 100.00, 0, '2026-04-11 06:02:46'),
(19, 2, 2, 4, 2, 7, 2, 100.00, 0, '2026-04-11 06:05:25'),
(20, 2, 3, 0, 0, 4, 0, 0.00, 0, '2026-04-16 10:48:00');

-- --------------------------------------------------------

--
-- Table structure for table `module_assessment_results`
--

CREATE TABLE `module_assessment_results` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `module_index` int(11) NOT NULL,
  `quiz_score_percentage` decimal(5,2) DEFAULT 0.00,
  `saq_score_percentage` decimal(5,2) DEFAULT NULL,
  `module_score_percentage` decimal(5,2) DEFAULT 0.00,
  `completed` tinyint(1) DEFAULT 0,
  `completed_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `module_assessment_results`
--

INSERT INTO `module_assessment_results` (`id`, `user_id`, `course_id`, `module_index`, `quiz_score_percentage`, `saq_score_percentage`, `module_score_percentage`, `completed`, `completed_at`) VALUES
(1, 2, 2, 0, 8.33, 0.00, 3.33, 1, NULL),
(2, 2, 2, 1, 5.56, 0.00, 2.22, 1, NULL),
(3, 2, 2, 2, 0.00, 0.00, 0.00, 1, NULL),
(4, 2, 2, 3, 16.67, 0.00, 6.67, 1, NULL),
(5, 2, 2, 4, 23.81, 0.00, 9.52, 1, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `quiz_answer_options`
--

CREATE TABLE `quiz_answer_options` (
  `id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  `option_text` text NOT NULL,
  `is_correct` tinyint(1) DEFAULT 0,
  `order_index` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `quiz_answer_options`
--

INSERT INTO `quiz_answer_options` (`id`, `question_id`, `option_text`, `is_correct`, `order_index`) VALUES
(1, 2, 'To reduce the spatial dimensions of the input data', 0, 0),
(2, 2, 'To increase the number of features extracted from the input data', 0, 1),
(3, 2, 'To apply filters to the input data and capture local patterns', 1, 2),
(4, 2, 'To normalize the input data', 0, 3),
(5, 3, 'Sigmoid', 0, 0),
(6, 3, 'ReLU', 0, 1),
(7, 3, 'Tanh', 0, 2),
(8, 3, 'Softmax', 1, 3),
(9, 4, 'To increase the spatial dimensions of the input data', 0, 0),
(10, 4, 'To reduce the number of parameters in the network', 0, 1),
(11, 4, 'To downsample the input data and reduce spatial dimensions', 1, 2),
(12, 4, 'To introduce non-linearity into the network', 0, 3),
(13, 5, 'Average pooling', 0, 0),
(14, 5, 'Max pooling', 1, 1),
(15, 5, 'Min pooling', 0, 2),
(16, 5, 'Sum pooling', 0, 3),
(17, 6, 'To increase the computational cost of the network', 0, 0),
(18, 6, 'To reduce the number of features extracted from the input data', 0, 1),
(19, 6, 'To capture different patterns and features from the input data', 1, 2),
(20, 6, 'To reduce the spatial dimensions of the input data', 0, 3),
(21, 7, 'To reduce spatial dimensions of the input data', 0, 0),
(22, 7, 'To increase the number of features in the input data', 0, 1),
(23, 7, 'To apply filters to small regions of the input data', 1, 2),
(24, 7, 'To normalize the input data', 0, 3),
(25, 8, 'Sigmoid', 0, 0),
(26, 8, 'Tanh', 0, 1),
(27, 8, 'ReLU', 0, 2),
(28, 8, 'Softmax', 1, 3),
(29, 9, 'To increase the spatial dimensions of the input data', 0, 0),
(30, 9, 'To reduce the number of features in the input data', 0, 1),
(31, 9, 'To apply non-linear transformations to the input data', 0, 2),
(32, 9, 'To downsample the input data and reduce spatial dimensions', 1, 3),
(33, 10, 'Pooling', 0, 0),
(34, 10, 'Flattening', 0, 1),
(35, 10, 'Convolution', 1, 2),
(36, 10, 'Activation', 0, 3),
(37, 11, 'To reduce spatial dimensions of the input data', 0, 0),
(38, 11, 'To increase the number of features in the input data', 0, 1),
(39, 11, 'To apply filters to small regions of the input data', 1, 2),
(40, 11, 'To normalize the input data', 0, 3),
(41, 12, 'Average pooling', 1, 0),
(42, 12, 'Max pooling', 0, 1),
(43, 12, 'Min pooling', 0, 2),
(44, 12, 'Standard deviation pooling', 0, 3),
(45, 13, 'To reduce overfitting by adding noise to the model', 0, 0),
(46, 13, 'To increase the capacity of the model by adding more layers', 0, 1),
(47, 13, 'To introduce non-linearity into the model', 1, 2),
(48, 13, 'To improve the interpretability of the model', 0, 3),
(49, 14, 'Sigmoid', 0, 0),
(50, 14, 'Tanh', 0, 1),
(51, 14, 'ReLU', 0, 2),
(52, 14, 'Softmax', 1, 3),
(53, 15, 'To reduce spatial dimensions of the input data', 0, 0),
(54, 15, 'To increase the number of features in the input data', 0, 1),
(55, 15, 'To apply filters to small regions of the input data', 1, 2),
(56, 15, 'To normalize the input data', 0, 3),
(57, 16, 'ReLU (Rectified Linear Unit)', 0, 0),
(58, 16, 'Sigmoid', 1, 1),
(59, 16, 'Tanh (Hyperbolic Tangent)', 0, 2),
(60, 16, 'Softmax', 0, 3),
(61, 17, 'To increase the spatial dimensions of the input data', 0, 0),
(62, 17, 'To reduce the number of features in the input data', 0, 1),
(63, 17, 'To apply filters to small regions of the input data', 0, 2),
(64, 17, 'To downsample the input data and reduce spatial dimensions', 1, 3),
(65, 18, 'Average pooling', 0, 0),
(66, 18, 'Max pooling', 1, 1),
(67, 18, 'Min pooling', 0, 2),
(68, 18, 'Sum pooling', 0, 3),
(69, 19, 'To reduce spatial dimensions of the input data', 0, 0),
(70, 19, 'To apply non-linear transformations to the input data', 0, 1),
(71, 19, 'To extract local features from small regions of the input data', 1, 2),
(72, 19, 'To perform classification based on the input data', 0, 3),
(73, 20, 'To increase the spatial dimensions of the input data', 0, 0),
(74, 20, 'To reduce the spatial dimensions of the input data and retain important features', 1, 1),
(75, 20, 'To apply non-linear transformations to the input data', 0, 2),
(76, 20, 'To extract local features from small regions of the input data', 0, 3),
(77, 21, 'Sigmoid', 0, 0),
(78, 21, 'ReLU (Rectified Linear Unit)', 1, 1),
(79, 21, 'Tanh (Hyperbolic Tangent)', 0, 2),
(80, 21, 'Softmax', 0, 3),
(81, 22, 'To reduce the number of parameters in the model', 0, 0),
(82, 22, 'To increase the number of parameters in the model', 0, 1),
(83, 22, 'To take advantage of spatial hierarchies in the input data', 1, 2),
(84, 22, 'To apply non-linear transformations to the input data', 0, 3),
(85, 23, 'AlexNet', 0, 0),
(86, 23, 'VGG', 0, 1),
(87, 23, 'LeNet', 1, 2),
(88, 23, 'ResNet', 0, 3),
(89, 24, 'Number of fully connected layers', 0, 0),
(90, 24, 'Use of batch normalization', 0, 1),
(91, 24, 'Depth of the network', 1, 2),
(92, 24, 'Type of activation function used', 0, 3),
(93, 25, 'Use of large kernel sizes', 0, 0),
(94, 25, 'Use of dropout regularization', 0, 1),
(95, 25, 'Use of average pooling', 0, 2),
(96, 25, 'Use of convolutional and pooling layers with a small number of parameters', 1, 3),
(97, 26, 'Improved generalization with smaller datasets', 0, 0),
(98, 26, 'Faster training times due to reduced parameters', 0, 1),
(99, 26, 'Increased robustness to overfitting with dropout', 0, 2),
(100, 26, 'Ability to learn more complex and abstract features', 1, 3),
(101, 27, 'Natural Language Processing', 0, 0),
(102, 27, 'Image Classification', 1, 1),
(103, 27, 'Speech Recognition', 0, 2),
(104, 27, 'Robotics', 0, 3),
(105, 28, 'Image Segmentation', 0, 0),
(106, 28, 'Object Detection', 1, 1),
(107, 28, 'Image Classification', 0, 2),
(108, 28, 'Image Generation', 0, 3),
(109, 29, 'Object Detection', 0, 0),
(110, 29, 'Image Classification', 0, 1),
(111, 29, 'Image Segmentation', 1, 2),
(112, 29, 'Image Registration', 0, 3),
(113, 30, 'Object Detection', 0, 0),
(114, 30, 'Image Segmentation', 0, 1),
(115, 30, 'Image Generation', 0, 2),
(116, 30, 'Image Classification', 1, 3),
(117, 31, 'Economic development', 0, 0),
(118, 31, 'Social interaction', 0, 1),
(119, 31, 'Exchange of information and ideas between politicians, media, and public', 1, 2),
(120, 31, 'Environmental conservation', 0, 3),
(121, 32, 'Social media marketing', 0, 0),
(122, 32, 'Agenda setting', 1, 1),
(123, 32, 'Financial management', 0, 2),
(124, 32, 'Human resource development', 0, 3),
(125, 33, 'They have no influence on public opinion', 0, 0),
(126, 33, 'They only report on political events', 0, 1),
(127, 33, 'They shape public opinion and set the agenda for political discussion', 1, 2),
(128, 33, 'They are only used for entertainment purposes', 0, 3),
(129, 34, 'To provide a neutral perspective on an issue', 0, 0),
(130, 34, 'To change the subject of discussion', 0, 1),
(131, 34, 'To influence public perception of an issue by selecting and emphasizing certain aspects', 1, 2),
(132, 34, 'To ignore opposing viewpoints', 0, 3),
(133, 35, 'Agenda-setting theory', 1, 0),
(134, 35, 'Social learning theory', 0, 1),
(135, 35, 'Cognitive dissonance theory', 0, 2),
(136, 35, 'Elaboration likelihood model', 0, 3),
(137, 36, 'The impact of media on political knowledge', 0, 0),
(138, 36, 'The influence of media on political attitudes and behaviors', 0, 1),
(139, 36, 'The long-term effects of media consumption on viewers\' perceptions of reality', 1, 2),
(140, 36, 'The role of media in political socialization', 0, 3),
(141, 37, 'Hypodermic needle theory', 0, 0),
(142, 37, 'Two-step flow theory', 1, 1),
(143, 37, 'Diffusion of innovations theory', 0, 2),
(144, 37, 'Social identity theory', 0, 3),
(145, 38, 'That media has a direct and powerful impact on public opinion', 0, 0),
(146, 38, 'That the way information is presented influences how it is perceived and interpreted', 1, 1),
(147, 38, 'That political communication is a one-way process', 0, 2),
(148, 38, 'That the media has no impact on political attitudes and behaviors', 0, 3),
(149, 39, 'Print media', 0, 0),
(150, 39, 'Oral rhetoric', 1, 1),
(151, 39, 'Social media', 0, 2),
(152, 39, 'Television', 0, 3),
(153, 40, 'Radio broadcasts', 0, 0),
(154, 40, 'Newspaper editorials', 1, 1),
(155, 40, 'Town hall meetings', 0, 2),
(156, 40, 'Social media campaigns', 0, 3),
(157, 41, 'Internet', 0, 0),
(158, 41, 'Television', 1, 1),
(159, 41, 'Radio', 0, 2),
(160, 41, 'Print press', 0, 3),
(161, 42, 'One-way communication', 0, 0),
(162, 42, 'Increased control by governments', 0, 1),
(163, 42, 'Two-way interaction between politicians and citizens', 1, 2),
(164, 42, 'Decreased accessibility of information', 0, 3),
(165, 43, 'To reduce the spatial dimensions of the input data', 0, 0),
(166, 43, 'To increase the number of features in the input data', 0, 1),
(167, 43, 'To extract local features from small regions of the input data', 1, 2),
(168, 43, 'To perform classification on the input data', 0, 3),
(169, 44, 'Sigmoid', 0, 0),
(170, 44, 'ReLU (Rectified Linear Unit)', 1, 1),
(171, 44, 'Tanh (Hyperbolic Tangent)', 0, 2),
(172, 44, 'Softmax', 0, 3),
(173, 45, 'To increase the spatial dimensions of the input data', 0, 0),
(174, 45, 'To extract local features from small regions of the input data', 0, 1),
(175, 45, 'To reduce the spatial dimensions of the input data and retain important features', 1, 2),
(176, 45, 'To perform classification on the input data', 0, 3),
(177, 46, 'To reduce the number of parameters in the model', 0, 0),
(178, 46, 'To increase the computational complexity of the model', 0, 1),
(179, 46, 'To extract multiple features from the input data', 1, 2),
(180, 46, 'To reduce the spatial dimensions of the input data', 0, 3),
(181, 47, 'To inform voters about policy details', 0, 0),
(182, 47, 'To persuade voters to support a candidate or issue', 1, 1),
(183, 47, 'To entertain voters with catchy slogans', 0, 2),
(184, 47, 'To confuse voters with complex jargon', 0, 3),
(185, 48, 'Using technical terms and jargon', 0, 0),
(186, 48, 'Focusing on abstract concepts and theories', 0, 1),
(187, 48, 'Sharing personal anecdotes and storytelling', 1, 2),
(188, 48, 'Reciting statistics and data', 0, 3),
(189, 49, 'To add variety and keep the message fresh', 0, 0),
(190, 49, 'To make the message more complex and nuanced', 0, 1),
(191, 49, 'To emphasize key points and make them more memorable', 1, 2),
(192, 49, 'To distract from the main issue', 0, 3),
(193, 50, 'So that the message can be tailored to appeal to a broad, general audience', 0, 0),
(194, 50, 'So that the message can be used to attack and criticize opponents', 0, 1),
(195, 50, 'So that the message can be used to promote a specific ideology', 0, 2),
(196, 50, 'So that the message can be tailored to resonate with and persuade a specific group of voters', 1, 3),
(197, 51, 'To gain financial support for campaigns', 0, 0),
(198, 51, 'To shape public opinion and influence policy', 1, 1),
(199, 51, 'To gather intelligence on political opponents', 0, 2),
(200, 51, 'To promote personal interests', 0, 3),
(201, 52, 'Providing false information to gain attention', 0, 0),
(202, 52, 'Being responsive to media inquiries and providing timely information', 1, 1),
(203, 52, 'Ignoring media requests and focusing on social media', 0, 2),
(204, 52, 'Using media outlets only for crisis management', 0, 3),
(205, 53, 'So they can manipulate the media to promote their agenda', 0, 0),
(206, 53, 'So they can build trust and credibility with the media and the public', 1, 1),
(207, 53, 'So they can avoid interacting with the media altogether', 0, 2),
(208, 53, 'So they can use the media to attack their opponents', 0, 3),
(209, 54, 'Increased public support and trust', 0, 0),
(210, 54, 'Improved relationships with other politicians and stakeholders', 0, 1),
(211, 54, 'Negative media coverage and loss of public credibility', 1, 2),
(212, 54, 'Increased financial support for campaigns', 0, 3),
(213, 55, 'To shift blame to opponents', 0, 0),
(214, 55, 'To maintain public trust and stability', 1, 1),
(215, 55, 'To gain political advantage over opponents', 0, 2),
(216, 55, 'To avoid media scrutiny', 0, 3),
(217, 56, 'Withholding information from the public', 0, 0),
(218, 56, 'Responding quickly and transparently', 1, 1),
(219, 56, 'Denying all responsibility', 0, 2),
(220, 56, 'Attacking the media', 0, 3),
(221, 57, 'Ignore the crisis and hope it goes away', 0, 0),
(222, 57, 'Conduct a thorough investigation and communicate findings', 1, 1),
(223, 57, 'Blame the crisis on external factors', 0, 2),
(224, 57, 'Make promises that cannot be kept', 0, 3),
(225, 58, 'To avoid preparing for potential crises', 0, 0),
(226, 58, 'To ensure a rapid and effective response to crises', 1, 1),
(227, 58, 'To reduce the importance of crisis communication', 0, 2),
(228, 58, 'To limit media coverage of crises', 0, 3),
(229, 59, 'To shift blame to opponents', 0, 0),
(230, 59, 'To maintain public trust and credibility', 1, 1),
(231, 59, 'To gain political advantage over opponents', 0, 2),
(232, 59, 'To ignore the crisis and hope it resolves itself', 0, 3),
(233, 60, 'Denying all responsibility for the crisis', 0, 0),
(234, 60, 'Providing timely and transparent information to the public', 1, 1),
(235, 60, 'Attacking the media for their coverage of the crisis', 0, 2),
(236, 60, 'Refusing to comment on the crisis until it is resolved', 0, 3),
(237, 61, 'To downplay the severity of the crisis', 0, 0),
(238, 61, 'To express empathy and concern for those affected', 1, 1),
(239, 61, 'To blame external factors or other parties for the crisis', 0, 2),
(240, 61, 'To remain silent and hope the crisis goes away', 0, 3),
(241, 62, 'To ensure they can quickly shift blame to others', 0, 0),
(242, 62, 'To minimize the damage to their reputation and maintain public trust', 1, 1),
(243, 62, 'To ignore crises and focus on other issues', 0, 2),
(244, 62, 'To use crises as opportunities to attack their opponents', 0, 3),
(245, 63, 'Restricting freedom of speech', 0, 0),
(246, 63, 'Promoting individual rights and freedoms', 1, 1),
(247, 63, 'Limiting access to information', 0, 2),
(248, 63, 'Suppressing public opinion', 0, 3),
(249, 64, 'To serve as a propaganda tool for the government', 0, 0),
(250, 64, 'To act as a watchdog and hold those in power accountable', 1, 1),
(251, 64, 'To provide only positive news and information', 0, 2),
(252, 64, 'To ignore political issues and focus on entertainment', 0, 3),
(253, 65, 'By encouraging politicians to be secretive and unaccountable', 0, 0),
(254, 65, 'By promoting transparency and accountability in political communication', 1, 1),
(255, 65, 'By limiting the amount of information that can be shared with the public', 0, 2),
(256, 65, 'By restricting the use of certain communication channels', 0, 3),
(257, 66, 'A focus on censorship and control', 0, 0),
(258, 66, 'An emphasis on diversity of viewpoints and opinions', 1, 1),
(259, 66, 'A reliance on propaganda and manipulation', 0, 2),
(260, 66, 'A restriction on access to information and knowledge', 0, 3),
(261, 67, 'To promote social change', 0, 0),
(262, 67, 'To preserve traditional values', 1, 1),
(263, 67, 'To increase government intervention', 0, 2),
(264, 67, 'To reduce economic inequality', 0, 3),
(265, 68, 'Emphasis on individual freedom', 1, 0),
(266, 68, 'Focus on collective action', 0, 1),
(267, 68, 'Prioritization of government control', 0, 2),
(268, 68, 'Rejection of social norms', 0, 3),
(269, 69, 'By promoting compromise and bipartisanship', 0, 0),
(270, 69, 'By emphasizing the importance of tradition and heritage', 1, 1),
(271, 69, 'By advocating for radical social change', 0, 2),
(272, 69, 'By dismissing the role of ideology in politics', 0, 3),
(273, 70, 'Using emotional appeals to sway public opinion', 0, 0),
(274, 70, 'Framing issues in terms of individual responsibility', 1, 1),
(275, 70, 'Citing expert opinions to build credibility', 0, 2),
(276, 70, 'Making promises of widespread social reform', 0, 3),
(277, 71, 'To promote social change', 0, 0),
(278, 71, 'To maintain traditional values', 1, 1),
(279, 71, 'To increase government spending', 0, 2),
(280, 71, 'To reduce individual freedoms', 0, 3),
(281, 72, 'By using emotional appeals to sway public opinion', 0, 0),
(282, 72, 'By emphasizing the importance of individual responsibility', 1, 1),
(283, 72, 'By promoting a strong centralized government', 0, 2),
(284, 72, 'By advocating for radical social reform', 0, 3),
(285, 73, 'A focus on collective action', 0, 0),
(286, 73, 'An emphasis on limited government intervention', 1, 1),
(287, 73, 'A call for increased government regulation', 0, 2),
(288, 73, 'A promotion of social welfare programs', 0, 3),
(289, 74, 'To confuse their opponents', 0, 0),
(290, 74, 'To appeal to a wider audience', 1, 1),
(291, 74, 'To demonstrate their intellectual superiority', 0, 2),
(292, 74, 'To hide their true intentions', 0, 3),
(293, 75, 'To promote individualism and private ownership', 0, 0),
(294, 75, 'To facilitate collective decision-making and social equality', 1, 1),
(295, 75, 'To advocate for authoritarian rule and censorship', 0, 2),
(296, 75, 'To prioritize economic growth over social welfare', 0, 3),
(297, 76, 'Emphasis on hierarchical structures and top-down control', 0, 0),
(298, 76, 'Focus on profit-driven media and advertising', 0, 1),
(299, 76, 'Promotion of participatory democracy and community engagement', 1, 2),
(300, 76, 'Reliance on propaganda and disinformation campaigns', 0, 3),
(301, 77, 'Competition and individual achievement', 0, 0),
(302, 77, 'Solidarity and collective action', 1, 1),
(303, 77, 'Economic efficiency and productivity', 0, 2),
(304, 77, 'Nationalism and cultural homogeneity', 0, 3),
(305, 78, 'As a tool for promoting private interests and corporate power', 0, 0),
(306, 78, 'As a means of social control and government propaganda', 0, 1),
(307, 78, 'As a platform for marginalized voices and social critique', 1, 2),
(308, 78, 'As a neutral and objective reflection of reality', 0, 3),
(309, 79, 'To provide entertainment only', 0, 0),
(310, 79, 'To shape public opinion and influence political agendas', 1, 1),
(311, 79, 'To solely report on sports and weather', 0, 2),
(312, 79, 'To act as a platform for advertising only', 0, 3),
(313, 80, 'By ignoring all political events', 0, 0),
(314, 80, 'By selectively reporting on certain political issues', 1, 1),
(315, 80, 'By never interviewing political figures', 0, 2),
(316, 80, 'By refusing to cover any news', 0, 3),
(317, 81, 'Increased political polarization', 1, 0),
(318, 81, 'Complete uniformity in political opinion', 0, 1),
(319, 81, 'No impact on voter turnout', 0, 2),
(320, 81, 'Elimination of all political debates', 0, 3),
(321, 82, 'By suppressing all information', 0, 0),
(322, 82, 'By providing a platform for diverse viewpoints and discussion', 1, 1),
(323, 82, 'By only reporting on non-political issues', 0, 2),
(324, 82, 'By dictating what the public should think without discussion', 0, 3),
(325, 83, 'They have no influence on political discourse', 0, 0),
(326, 83, 'They provide a platform for politicians to reach a wide audience', 1, 1),
(327, 83, 'They are only used for entertainment purposes', 0, 2),
(328, 83, 'They are replaced by social media in shaping political discourse', 0, 3),
(329, 84, 'Through social media campaigns', 0, 0),
(330, 84, 'By providing biased and misleading information', 0, 1),
(331, 84, 'By framing and agenda-setting', 1, 2),
(332, 84, 'By ignoring political issues altogether', 0, 3),
(333, 85, 'They are highly interactive', 0, 0),
(334, 85, 'They are only available online', 0, 1),
(335, 85, 'They have a wide reach and audience', 1, 2),
(336, 85, 'They are not regulated by any authority', 0, 3),
(337, 86, 'Because they are the only source of news and information', 0, 0),
(338, 86, 'Because they have a wide reach and can shape public opinion', 1, 1),
(339, 86, 'Because they are more expensive than digital media', 0, 2),
(340, 86, 'Because they are no longer relevant in modern society', 0, 3),
(341, 87, 'By reducing the number of political news outlets', 0, 0),
(342, 87, 'By allowing politicians to directly communicate with the public', 1, 1),
(343, 87, 'By eliminating the need for traditional campaign advertising', 0, 2),
(344, 87, 'By restricting access to political information', 0, 3),
(345, 88, 'They ban all political advertising', 0, 0),
(346, 88, 'They allow it without any restrictions', 0, 1),
(347, 88, 'They fact-check all political ads before allowing them', 0, 2),
(348, 88, 'They have specific policies and regulations for political advertising', 1, 3),
(349, 89, 'It has led to a decrease in political polarization', 0, 0),
(350, 89, 'It has increased the spread of misinformation', 1, 1),
(351, 89, 'It has made political news less accessible', 0, 2),
(352, 89, 'It has eliminated the influence of traditional media', 0, 3),
(353, 90, 'Because they are the only way to reach young voters', 0, 0),
(354, 90, 'Because they offer a free way to advertise', 0, 1),
(355, 90, 'Because they allow for targeted and personalized advertising', 1, 2),
(356, 90, 'Because they have replaced traditional campaign rallies', 0, 3),
(357, 91, 'To discredit opposing political views', 0, 0),
(358, 91, 'To understand and critically evaluate information', 1, 1),
(359, 91, 'To promote a specific political agenda', 0, 2),
(360, 91, 'To ignore opposing viewpoints', 0, 3),
(361, 92, 'Confirmation bias', 1, 0),
(362, 92, 'Information overload', 0, 1),
(363, 92, 'Social influence', 0, 2),
(364, 92, 'Cognitive dissonance', 0, 3),
(365, 93, 'It can increase voter turnout', 0, 0),
(366, 93, 'It can lead to a more informed electorate', 0, 1),
(367, 93, 'It can create a polarized and misinformed public', 1, 2),
(368, 93, 'It can reduce political engagement', 0, 3),
(369, 94, 'Only consuming information from a single source', 0, 0),
(370, 94, 'Seeking out diverse perspectives and fact-checking information', 1, 1),
(371, 94, 'Ignoring media reports and relying on social media', 0, 2),
(372, 94, 'Relying solely on opinion pieces and editorials', 0, 3),
(373, 95, 'To discredit opposing political views', 0, 0),
(374, 95, 'To understand and address potential influences on public opinion', 1, 1),
(375, 95, 'To promote a specific political agenda', 0, 2),
(376, 95, 'To entertain the audience with controversial topics', 0, 3),
(377, 96, 'Presenting multiple, balanced viewpoints', 0, 0),
(378, 96, 'Using emotive language to sway public opinion', 1, 1),
(379, 96, 'Providing in-depth analysis of both sides of an issue', 0, 2),
(380, 96, 'Including diverse perspectives from experts and everyday people', 0, 3),
(381, 97, 'Increased civic engagement and informed decision-making', 0, 0),
(382, 97, 'Polarization of the public along party lines', 1, 1),
(383, 97, 'Improved critical thinking skills among the audience', 0, 2),
(384, 97, 'Enhanced trust in the media and political institutions', 0, 3),
(385, 98, 'By only consuming news from a single, trusted source', 0, 0),
(386, 98, 'Through critical thinking and seeking out diverse, credible sources', 1, 1),
(387, 98, 'By avoiding news and political discussions altogether', 0, 2),
(388, 98, 'By relying on social media platforms for news and information', 0, 3),
(389, 99, 'Emotional appeals', 1, 0),
(390, 99, 'Only focusing on policy details', 0, 1),
(391, 99, 'Ignoring the opponent\'s platform', 0, 2),
(392, 99, 'Never using social media', 0, 3),
(393, 100, 'Increased ability to target specific demographics', 1, 0),
(394, 100, 'Reduced need for in-person campaign events', 0, 1),
(395, 100, 'Complete control over the campaign\'s message', 0, 2),
(396, 100, 'Elimination of the need for a campaign website', 0, 3),
(397, 101, 'To persuade undecided voters', 1, 0),
(398, 101, 'To only appeal to the candidate\'s existing supporters', 0, 1),
(399, 101, 'To solely criticize the opponent', 0, 2),
(400, 101, 'To avoid taking a stance on any issues', 0, 3),
(401, 102, 'To build trust and credibility with voters', 1, 0),
(402, 102, 'To confuse the opponent\'s supporters', 0, 1),
(403, 102, 'To only appeal to a specific demographic', 0, 2),
(404, 102, 'To frequently change the campaign\'s platform', 0, 3),
(405, 103, 'Focusing solely on negative advertising', 0, 0),
(406, 103, 'Building a strong, authentic narrative', 1, 1),
(407, 103, 'Ignoring social media platforms', 0, 2),
(408, 103, 'Relying on celebrity endorsements only', 0, 3),
(409, 104, 'To alienate potential voters', 0, 0),
(410, 104, 'To build a negative image of opponents', 0, 1),
(411, 104, 'To persuade and mobilize target audiences', 1, 2),
(412, 104, 'To avoid discussing policy issues', 0, 3),
(413, 105, 'It has no significant impact on campaign outcomes', 0, 0),
(414, 105, 'It is used primarily for fundraising', 0, 1),
(415, 105, 'It serves as a platform for one-way communication only', 0, 2),
(416, 105, 'It enables targeted, interactive communication with voters', 1, 3),
(417, 106, 'So that campaigns can ignore their needs and concerns', 0, 0),
(418, 106, 'To develop messages that resonate with and motivate them', 1, 1),
(419, 106, 'To focus solely on the candidate\'s personal story', 0, 2),
(420, 106, 'To mimic the strategies of opposing campaigns', 0, 3),
(421, 107, 'To deflect blame from the government', 0, 0),
(422, 107, 'To inform and reassure the public', 1, 1),
(423, 107, 'To promote a specific political ideology', 0, 2),
(424, 107, 'To create confusion and disorder', 0, 3),
(425, 108, 'Coordinating messages across different government agencies', 1, 0),
(426, 108, 'Ignoring the opinions of other nations', 0, 1),
(427, 108, 'Focusing solely on domestic issues', 0, 2),
(428, 108, 'Disregarding the role of social media', 0, 3),
(429, 109, 'By providing misleading information to avoid panic', 0, 0),
(430, 109, 'By being transparent, empathetic, and consistent in their messaging', 1, 1),
(431, 109, 'By shifting blame to other countries or organizations', 0, 2),
(432, 109, 'By avoiding public appearances and statements', 0, 3),
(433, 110, 'Using language that is offensive to other cultures', 0, 0),
(434, 110, 'Focusing on the interests of their own nation alone', 0, 1),
(435, 110, 'Being sensitive to cultural differences and nuances', 1, 2),
(436, 110, 'Disregarding the potential for misinformation and disinformation', 0, 3),
(437, 111, 'To divert attention from the crisis', 0, 0),
(438, 111, 'To inform and reassure the public', 1, 1),
(439, 111, 'To blame the opposition party', 0, 2),
(440, 111, 'To declare a state of emergency', 0, 3),
(441, 112, 'Using complex technical jargon', 0, 0),
(442, 112, 'Being transparent and honest with the public', 1, 1),
(443, 112, 'Focusing solely on economic aspects', 0, 2),
(444, 112, 'Ignoring social media platforms', 0, 3),
(445, 113, 'It has no significant impact on public opinion', 0, 0),
(446, 113, 'It is used solely for propaganda purposes', 0, 1),
(447, 113, 'It provides a platform for real-time information and public engagement', 1, 2),
(448, 113, 'It is used only by government officials', 0, 3),
(449, 114, 'It helps to confuse the public', 0, 0),
(450, 114, 'It allows for flexibility in messaging', 0, 1),
(451, 114, 'It builds trust and credibility with the public', 1, 2),
(452, 114, 'It is required by law', 0, 3),
(453, 115, 'To divert attention from the crisis', 0, 0),
(454, 115, 'To inform and reassure the public', 1, 1),
(455, 115, 'To blame opposition parties for the crisis', 0, 2),
(456, 115, 'To suspend all media activity', 0, 3),
(457, 116, 'Coordinating a unified national response', 1, 0),
(458, 116, 'Ignoring international media coverage', 0, 1),
(459, 116, 'Focusing solely on domestic issues', 0, 2),
(460, 116, 'Disregarding the role of social media', 0, 3),
(461, 117, 'They have no significant role in crisis communication', 0, 0),
(462, 117, 'They are used solely for official statements', 0, 1),
(463, 117, 'They facilitate real-time information dissemination and public engagement', 1, 2),
(464, 117, 'They are used exclusively for opposition purposes', 0, 3),
(465, 118, 'To hide the true extent of the crisis', 0, 0),
(466, 118, 'To maintain public trust and credibility', 1, 1),
(467, 118, 'To confuse the public with contradictory information', 0, 2),
(468, 118, 'To prioritize political gain over public safety', 0, 3),
(469, 119, 'Decreasing social media usage', 0, 0),
(470, 119, 'Emerging trends and technologies', 1, 1),
(471, 119, 'Reduced access to information', 0, 2),
(472, 119, 'Less focus on citizen engagement', 0, 3),
(473, 120, 'To share only negative ads', 0, 0),
(474, 120, 'To engage with voters and share their message', 1, 1),
(475, 120, 'To solely promote their opponents', 0, 2),
(476, 120, 'To avoid interacting with the public', 0, 3),
(477, 121, 'Print newspapers', 0, 0),
(478, 121, 'Television advertising', 0, 1),
(479, 121, 'Social media analytics tools', 1, 2),
(480, 121, 'Landline phones', 0, 3),
(481, 122, 'So they can ignore the opinions of their constituents', 0, 0),
(482, 122, 'So they can effectively engage with voters and stay ahead of their opponents', 1, 1),
(483, 122, 'So they can reduce their online presence', 0, 2),
(484, 122, 'So they can stop using social media altogether', 0, 3),
(485, 123, 'They have no significant impact on political communication', 0, 0),
(486, 123, 'They serve as a primary source of news and information for voters', 1, 1),
(487, 123, 'They are only used for campaigning during election seasons', 0, 2),
(488, 123, 'They are irrelevant to political discourse and decision-making', 0, 3),
(489, 124, 'Increased use of print media', 0, 0),
(490, 124, 'Growing reliance on artificial intelligence for campaign messaging', 1, 1),
(491, 124, 'Decreased importance of digital literacy among politicians', 0, 2),
(492, 124, 'Reduced focus on data-driven decision making in political campaigns', 0, 3),
(493, 125, 'They make it more difficult to target specific demographics', 0, 0),
(494, 125, 'They have no impact on the targeting and delivery of political messages', 0, 1),
(495, 125, 'They enable more precise targeting and personalized messaging', 1, 2),
(496, 125, 'They lead to a one-size-fits-all approach to political communication', 0, 3),
(497, 126, 'The potential for increased transparency in political messaging', 0, 0),
(498, 126, 'The risk of disinformation and misinformation spreading quickly', 1, 1),
(499, 126, 'The decreased ability to track and analyze voter engagement', 0, 2),
(500, 126, 'The guaranteed authenticity of online political discourse', 0, 3),
(501, 127, 'To entertain the public', 0, 0),
(502, 127, 'To inform and persuade the public', 1, 1),
(503, 127, 'To conduct scientific research', 0, 2),
(504, 127, 'To promote business products', 0, 3),
(505, 128, 'Social media marketing', 0, 0),
(506, 128, 'Agenda setting', 1, 1),
(507, 128, 'Financial accounting', 0, 2),
(508, 128, 'Environmental conservation', 0, 3),
(509, 129, 'Public relations', 0, 0),
(510, 129, 'Propaganda', 0, 1),
(511, 129, 'Spin doctoring', 0, 2),
(512, 129, 'Framing', 1, 3),
(513, 130, 'Newspaper editorial', 1, 0),
(514, 130, 'Private conversation', 0, 1),
(515, 130, 'Personal diary entry', 0, 2),
(516, 130, 'Math textbook', 0, 3),
(517, 131, 'To solely manage daily tasks', 0, 0),
(518, 131, 'To inspire and motivate employees to achieve a common goal', 1, 1),
(519, 131, 'To only make financial decisions', 0, 2),
(520, 131, 'To micromanage every aspect of the business', 0, 3),
(521, 132, 'It is unnecessary for small businesses', 0, 0),
(522, 132, 'It helps to increase employee turnover', 0, 1),
(523, 132, 'It plays a crucial role in guiding the organization towards its vision and goals', 1, 2),
(524, 132, 'It is only relevant in non-profit organizations', 0, 3),
(525, 133, 'Being inflexible and unwilling to adapt', 0, 0),
(526, 133, 'Having excellent communication and interpersonal skills', 1, 1),
(527, 133, 'Focusing solely on personal gain', 0, 2),
(528, 133, 'Avoiding decision-making responsibilities', 0, 3),
(529, 134, 'They work alone to solve all problems', 0, 0),
(530, 134, 'They empower and enable their team members to work towards a common objective', 1, 1),
(531, 134, 'They ignore feedback and criticism from others', 0, 2),
(532, 134, 'They prioritize their own interests over the organization\'s goals', 0, 3);

-- --------------------------------------------------------

--
-- Table structure for table `quiz_questions`
--

CREATE TABLE `quiz_questions` (
  `id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `module_index` int(11) NOT NULL,
  `lesson_index` int(11) NOT NULL,
  `question_text` text NOT NULL,
  `question_type` enum('multiple_choice','true_false','short_answer') DEFAULT 'multiple_choice',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `quiz_questions`
--

INSERT INTO `quiz_questions` (`id`, `course_id`, `module_index`, `lesson_index`, `question_text`, `question_type`, `created_at`) VALUES
(1, 1, 0, 0, 'What is the primary purpose of the convolutional layer in a CNN?', 'multiple_choice', '2026-04-08 15:00:05'),
(2, 1, 0, 0, 'What is the primary purpose of the convolutional layer in a CNN?', 'multiple_choice', '2026-04-08 15:03:42'),
(3, 1, 0, 0, 'Which of the following activation functions is commonly used in the output layer of a CNN for multi-class classification problems?', 'multiple_choice', '2026-04-08 15:03:42'),
(4, 1, 0, 0, 'What is the primary function of the pooling layer in a CNN?', 'multiple_choice', '2026-04-08 15:03:42'),
(5, 1, 0, 0, 'Which of the following types of pooling is commonly used in CNNs due to its ability to preserve the most important information?', 'multiple_choice', '2026-04-08 15:03:42'),
(6, 1, 0, 0, 'What is the purpose of using multiple filters in a convolutional layer?', 'multiple_choice', '2026-04-08 15:03:42'),
(7, 1, 0, 0, 'What is the primary purpose of the convolutional layer in a CNN?', 'multiple_choice', '2026-04-08 16:30:18'),
(8, 1, 0, 0, 'Which of the following activation functions is commonly used in the output layer of a CNN for multi-class classification problems?', 'multiple_choice', '2026-04-08 16:30:18'),
(9, 1, 0, 0, 'What is the primary function of the pooling layer in a CNN?', 'multiple_choice', '2026-04-08 16:30:18'),
(10, 1, 0, 0, 'What is the term for the process of sliding a filter over the entire input data in a CNN?', 'multiple_choice', '2026-04-08 16:30:18'),
(11, 1, 0, 0, 'What is the primary purpose of the convolutional layer in a CNN?', 'multiple_choice', '2026-04-08 16:31:47'),
(12, 1, 0, 0, 'Which of the following pooling techniques is commonly used in CNNs to downsample the feature maps?', 'multiple_choice', '2026-04-08 16:31:47'),
(13, 1, 0, 0, 'What is the role of the activation function in a CNN?', 'multiple_choice', '2026-04-08 16:31:47'),
(14, 1, 0, 0, 'Which activation function is commonly used in the output layer of a CNN for multi-class classification problems?', 'multiple_choice', '2026-04-08 16:31:47'),
(15, 1, 0, 0, 'What is the primary purpose of the convolutional layer in a CNN?', 'multiple_choice', '2026-04-08 16:43:38'),
(16, 1, 0, 0, 'Which of the following activation functions is commonly used in the output layer of a CNN for binary classification problems?', 'multiple_choice', '2026-04-08 16:43:38'),
(17, 1, 0, 0, 'What is the primary function of the pooling layer in a CNN?', 'multiple_choice', '2026-04-08 16:43:38'),
(18, 1, 0, 0, 'Which of the following types of pooling is commonly used in CNNs due to its simplicity and effectiveness?', 'multiple_choice', '2026-04-08 16:43:38'),
(19, 1, 0, 0, 'What is the primary function of the convolutional layer in a CNN?', 'multiple_choice', '2026-04-08 17:18:31'),
(20, 1, 0, 0, 'What is the purpose of the pooling layer in a CNN?', 'multiple_choice', '2026-04-08 17:18:31'),
(21, 1, 0, 0, 'Which of the following activation functions is commonly used in the hidden layers of a CNN?', 'multiple_choice', '2026-04-08 17:18:31'),
(22, 1, 0, 0, 'What is the primary benefit of using convolutional layers in a CNN?', 'multiple_choice', '2026-04-08 17:18:31'),
(23, 1, 0, 1, 'Which of the following CNN architectures introduced the use of convolutional and pooling layers?', 'multiple_choice', '2026-04-09 05:51:23'),
(24, 1, 0, 1, 'What is the primary difference between AlexNet and VGG architectures?', 'multiple_choice', '2026-04-09 05:51:23'),
(25, 1, 0, 1, 'Which of the following is a characteristic of the LeNet architecture?', 'multiple_choice', '2026-04-09 05:51:23'),
(26, 1, 0, 1, 'What is the main advantage of using deeper CNN architectures like VGG?', 'multiple_choice', '2026-04-09 05:51:23'),
(27, 1, 0, 2, 'What is the primary application of CNNs in computer vision?', 'multiple_choice', '2026-04-09 06:06:43'),
(28, 1, 0, 2, 'Which of the following tasks involves locating and categorizing objects within an image?', 'multiple_choice', '2026-04-09 06:06:43'),
(29, 1, 0, 2, 'What is the term for the process of dividing an image into its constituent parts or objects?', 'multiple_choice', '2026-04-09 06:06:43'),
(30, 1, 0, 2, 'Which application of CNNs involves assigning a label to an entire image?', 'multiple_choice', '2026-04-09 06:06:43'),
(31, 2, 0, 0, 'What is the primary focus of political communication?', 'multiple_choice', '2026-04-09 07:08:36'),
(32, 2, 0, 0, 'Which of the following is a key concept in political communication?', 'multiple_choice', '2026-04-09 07:08:36'),
(33, 2, 0, 0, 'What role do media play in political communication?', 'multiple_choice', '2026-04-09 07:08:36'),
(34, 2, 0, 0, 'What is the purpose of framing in political communication?', 'multiple_choice', '2026-04-09 07:08:36'),
(35, 2, 0, 1, 'Which theory of political communication focuses on the role of media in shaping public opinion?', 'multiple_choice', '2026-04-09 07:10:20'),
(36, 2, 0, 1, 'What is the primary concern of the cultivation theory in political communication?', 'multiple_choice', '2026-04-09 07:10:20'),
(37, 2, 0, 1, 'Which theoretical framework suggests that political communication is a two-step flow, where information flows from media to opinion leaders and then to the general public?', 'multiple_choice', '2026-04-09 07:10:20'),
(38, 2, 0, 1, 'What is the main idea behind the framing theory in political communication?', 'multiple_choice', '2026-04-09 07:10:20'),
(39, 2, 0, 2, 'What is considered the earliest form of political communication?', 'multiple_choice', '2026-04-09 07:12:19'),
(40, 2, 0, 2, 'Which of the following best describes the primary method of political communication during the 19th century?', 'multiple_choice', '2026-04-09 07:12:19'),
(41, 2, 0, 2, 'The development of which technology significantly changed the landscape of political communication in the mid-20th century?', 'multiple_choice', '2026-04-09 07:12:19'),
(42, 2, 0, 2, 'What is a key characteristic of modern political communication, especially with the rise of the internet and social media?', 'multiple_choice', '2026-04-09 07:12:19'),
(43, 1, 0, 0, 'What is the primary purpose of the convolutional layer in a CNN?', 'multiple_choice', '2026-04-09 09:20:27'),
(44, 1, 0, 0, 'Which of the following activation functions is commonly used in the hidden layers of a CNN?', 'multiple_choice', '2026-04-09 09:20:27'),
(45, 1, 0, 0, 'What is the primary function of the pooling layer in a CNN?', 'multiple_choice', '2026-04-09 09:20:27'),
(46, 1, 0, 0, 'What is the purpose of using multiple filters in a convolutional layer?', 'multiple_choice', '2026-04-09 09:20:27'),
(47, 2, 1, 0, 'What is the primary goal of crafting a political message?', 'multiple_choice', '2026-04-11 05:30:48'),
(48, 2, 1, 0, 'Which technique is commonly used to make political messages more relatable?', 'multiple_choice', '2026-04-11 05:30:48'),
(49, 2, 1, 0, 'What is the purpose of using repetition in a political message?', 'multiple_choice', '2026-04-11 05:30:48'),
(50, 2, 1, 0, 'Why is it important to consider the target audience when crafting a political message?', 'multiple_choice', '2026-04-11 05:30:48'),
(51, 2, 1, 1, 'What is the primary goal of building relationships with media outlets in politics?', 'multiple_choice', '2026-04-11 05:32:26'),
(52, 2, 1, 1, 'Which of the following is a key strategy for maintaining relationships with media outlets?', 'multiple_choice', '2026-04-11 05:32:26'),
(53, 2, 1, 1, 'Why is it important for politicians to understand the needs and interests of media outlets?', 'multiple_choice', '2026-04-11 05:32:26'),
(54, 2, 1, 1, 'What is a potential consequence of failing to build and maintain relationships with media outlets?', 'multiple_choice', '2026-04-11 05:32:26'),
(55, 2, 1, 2, 'What is the primary goal of crisis communication in politics?', 'multiple_choice', '2026-04-11 05:39:21'),
(56, 2, 1, 2, 'Which of the following is a key principle of effective crisis communication?', 'multiple_choice', '2026-04-11 05:39:21'),
(57, 2, 1, 2, 'What should a politician do when faced with a crisis?', 'multiple_choice', '2026-04-11 05:39:21'),
(58, 2, 1, 2, 'Why is it important for politicians to have a crisis communication plan in place?', 'multiple_choice', '2026-04-11 05:39:21'),
(59, 2, 1, 2, 'What is the primary goal of crisis communication in politics?', 'multiple_choice', '2026-04-11 05:39:43'),
(60, 2, 1, 2, 'Which of the following is a key element of effective crisis communication in politics?', 'multiple_choice', '2026-04-11 05:39:43'),
(61, 2, 1, 2, 'What is the best way for a politician to respond to a crisis in the initial stages?', 'multiple_choice', '2026-04-11 05:39:43'),
(62, 2, 1, 2, 'Why is it important for politicians to have a crisis communication plan in place?', 'multiple_choice', '2026-04-11 05:39:44'),
(63, 2, 2, 0, 'What is the primary focus of liberal ideologies in the context of political communication?', 'multiple_choice', '2026-04-11 05:42:49'),
(64, 2, 2, 0, 'According to liberal ideologies, what is the role of the media in political communication?', 'multiple_choice', '2026-04-11 05:42:49'),
(65, 2, 2, 0, 'How do liberal ideologies influence the way politicians communicate with the public?', 'multiple_choice', '2026-04-11 05:42:49'),
(66, 2, 2, 0, 'What is a key characteristic of liberal approaches to political communication?', 'multiple_choice', '2026-04-11 05:42:49'),
(67, 2, 2, 1, 'What is the primary goal of conservative political messaging?', 'multiple_choice', '2026-04-11 05:45:18'),
(68, 2, 2, 1, 'Which of the following is a key characteristic of conservative communication strategies?', 'multiple_choice', '2026-04-11 05:45:18'),
(69, 2, 2, 1, 'How do conservative ideologies often influence political discourse?', 'multiple_choice', '2026-04-11 05:45:18'),
(70, 2, 2, 1, 'What is a common tactic used by conservatives to frame their message?', 'multiple_choice', '2026-04-11 05:45:18'),
(71, 2, 2, 1, 'What is the primary goal of conservative ideologies in political messaging?', 'multiple_choice', '2026-04-11 05:45:37'),
(72, 2, 2, 1, 'How do conservatives typically approach political communication?', 'multiple_choice', '2026-04-11 05:45:37'),
(73, 2, 2, 1, 'What is a key characteristic of conservative political messaging?', 'multiple_choice', '2026-04-11 05:45:37'),
(74, 2, 2, 1, 'Why do conservatives often use simple, clear language in their political messaging?', 'multiple_choice', '2026-04-11 05:45:37'),
(75, 2, 2, 2, 'What is the primary goal of socialist ideologies in terms of political communication?', 'multiple_choice', '2026-04-11 05:47:45'),
(76, 2, 2, 2, 'Which of the following is a key feature of socialist communication strategies?', 'multiple_choice', '2026-04-11 05:47:45'),
(77, 2, 2, 2, 'Socialist ideologies often prioritize which of the following values in their communication approaches?', 'multiple_choice', '2026-04-11 05:47:45'),
(78, 2, 2, 2, 'How do socialist ideologies typically view the role of media in society?', 'multiple_choice', '2026-04-11 05:47:45'),
(79, 2, 3, 0, 'What is the primary role of traditional media outlets in shaping political discourse?', 'multiple_choice', '2026-04-11 05:50:14'),
(80, 2, 3, 0, 'Which of the following is a way traditional media influences political discourse?', 'multiple_choice', '2026-04-11 05:50:14'),
(81, 2, 3, 0, 'What can be a consequence of traditional media\'s influence on political discourse?', 'multiple_choice', '2026-04-11 05:50:14'),
(82, 2, 3, 0, 'How do traditional media outlets contribute to the formation of public opinion?', 'multiple_choice', '2026-04-11 05:50:14'),
(83, 2, 3, 0, 'What role do traditional media outlets play in shaping political discourse?', 'multiple_choice', '2026-04-11 05:50:38'),
(84, 2, 3, 0, 'How do traditional media outlets influence public opinion?', 'multiple_choice', '2026-04-11 05:50:38'),
(85, 2, 3, 0, 'What is a key characteristic of traditional media outlets?', 'multiple_choice', '2026-04-11 05:50:38'),
(86, 2, 3, 0, 'Why are traditional media outlets still important in the digital age?', 'multiple_choice', '2026-04-11 05:50:38'),
(87, 2, 3, 1, 'What is a primary way social media has changed political communication?', 'multiple_choice', '2026-04-11 05:52:41'),
(88, 2, 3, 1, 'How do social media platforms typically handle political advertising?', 'multiple_choice', '2026-04-11 05:52:41'),
(89, 2, 3, 1, 'What has been a significant impact of social media on political discourse?', 'multiple_choice', '2026-04-11 05:52:41'),
(90, 2, 3, 1, 'Why are social media platforms important for political campaigns?', 'multiple_choice', '2026-04-11 05:52:41'),
(91, 2, 3, 2, 'What is the primary goal of identifying media bias in political communication?', 'multiple_choice', '2026-04-11 05:54:49'),
(92, 2, 3, 2, 'Which of the following is a common type of media bias?', 'multiple_choice', '2026-04-11 05:54:49'),
(93, 2, 3, 2, 'How can media bias affect political communication?', 'multiple_choice', '2026-04-11 05:54:49'),
(94, 2, 3, 2, 'What is an effective way to address media bias in political communication?', 'multiple_choice', '2026-04-11 05:54:49'),
(95, 2, 3, 2, 'What is the primary goal of identifying media bias in political communication?', 'multiple_choice', '2026-04-11 05:55:45'),
(96, 2, 3, 2, 'Which of the following is a common indicator of media bias in news reporting?', 'multiple_choice', '2026-04-11 05:55:45'),
(97, 2, 3, 2, 'What can be a consequence of unaddressed media bias in political communication?', 'multiple_choice', '2026-04-11 05:55:45'),
(98, 2, 3, 2, 'How can individuals effectively counteract the influence of media bias in their own political understanding?', 'multiple_choice', '2026-04-11 05:55:45'),
(99, 2, 4, 0, 'What is a key component of effective communication strategies in political campaigns?', 'multiple_choice', '2026-04-11 05:59:16'),
(100, 2, 4, 0, 'Which of the following is a key benefit of using social media in a political campaign?', 'multiple_choice', '2026-04-11 05:59:16'),
(101, 2, 4, 0, 'What is the primary goal of a political campaign\'s messaging strategy?', 'multiple_choice', '2026-04-11 05:59:16'),
(102, 2, 4, 0, 'Why is it important for a political campaign to have a clear and consistent message?', 'multiple_choice', '2026-04-11 05:59:16'),
(103, 2, 4, 0, 'What is a key component of effective communication in successful political campaigns?', 'multiple_choice', '2026-04-11 05:59:33'),
(104, 2, 4, 0, 'Which of the following is a common goal of political campaign communication strategies?', 'multiple_choice', '2026-04-11 05:59:33'),
(105, 2, 4, 0, 'What role does social media play in modern political campaigns?', 'multiple_choice', '2026-04-11 05:59:33'),
(106, 2, 4, 0, 'Why is understanding the target audience crucial in political campaign communication?', 'multiple_choice', '2026-04-11 05:59:33'),
(107, 2, 4, 1, 'What is the primary goal of political communication during a national crisis?', 'multiple_choice', '2026-04-11 06:01:48'),
(108, 2, 4, 1, 'Which of the following is a key challenge in political communication during international crises?', 'multiple_choice', '2026-04-11 06:01:48'),
(109, 2, 4, 1, 'How can political leaders effectively communicate with the public during a crisis?', 'multiple_choice', '2026-04-11 06:01:48'),
(110, 2, 4, 1, 'What is an important consideration for political communicators when crafting messages for international audiences during a crisis?', 'multiple_choice', '2026-04-11 06:01:48'),
(111, 2, 4, 1, 'What is the primary goal of political communication during a national crisis?', 'multiple_choice', '2026-04-11 06:02:15'),
(112, 2, 4, 1, 'Which of the following is a key characteristic of effective political communication in times of crisis?', 'multiple_choice', '2026-04-11 06:02:15'),
(113, 2, 4, 1, 'What is the role of social media in political communication during international crises?', 'multiple_choice', '2026-04-11 06:02:15'),
(114, 2, 4, 1, 'Why is consistency important in political communication during a crisis?', 'multiple_choice', '2026-04-11 06:02:15'),
(115, 2, 4, 1, 'What is a primary goal of political communication during a national crisis?', 'multiple_choice', '2026-04-11 06:03:53'),
(116, 2, 4, 1, 'Which of the following is a key challenge in political communication during international crises?', 'multiple_choice', '2026-04-11 06:03:53'),
(117, 2, 4, 1, 'What role do social media platforms play in political communication during times of crisis?', 'multiple_choice', '2026-04-11 06:03:53'),
(118, 2, 4, 1, 'Why is transparency important in political communication during crises?', 'multiple_choice', '2026-04-11 06:03:53'),
(119, 2, 4, 2, 'What is a key factor driving the evolution of political communication?', 'multiple_choice', '2026-04-11 06:04:24'),
(120, 2, 4, 2, 'How do politicians primarily use social media in their campaigns?', 'multiple_choice', '2026-04-11 06:04:24'),
(121, 2, 4, 2, 'What is an example of a technology that has changed the way political campaigns are run?', 'multiple_choice', '2026-04-11 06:04:24'),
(122, 2, 4, 2, 'Why is understanding emerging trends in political communication important for politicians?', 'multiple_choice', '2026-04-11 06:04:24'),
(123, 2, 4, 2, 'What role do social media platforms play in the future of political communication?', 'multiple_choice', '2026-04-11 06:04:50'),
(124, 2, 4, 2, 'Which of the following emerging trends is likely to influence political communication in the future?', 'multiple_choice', '2026-04-11 06:04:50'),
(125, 2, 4, 2, 'How do emerging technologies impact the way political messages are targeted and delivered to audiences?', 'multiple_choice', '2026-04-11 06:04:50'),
(126, 2, 4, 2, 'What is a key challenge posed by the use of emerging technologies in political communication?', 'multiple_choice', '2026-04-11 06:04:50'),
(127, 2, 0, 0, 'What is the primary goal of political communication?', 'multiple_choice', '2026-04-15 05:44:20'),
(128, 2, 0, 0, 'Which of the following is a key concept in political communication?', 'multiple_choice', '2026-04-15 05:44:20'),
(129, 2, 0, 0, 'What is the term for the process by which political leaders shape public opinion?', 'multiple_choice', '2026-04-15 05:44:20'),
(130, 2, 0, 0, 'Which of the following is an example of a political communication channel?', 'multiple_choice', '2026-04-15 05:44:20'),
(131, 3, 0, 0, 'What is the primary focus of leadership in an organization?', 'multiple_choice', '2026-04-16 10:47:38'),
(132, 3, 0, 0, 'Why is leadership important in organizations?', 'multiple_choice', '2026-04-16 10:47:38'),
(133, 3, 0, 0, 'What is a key characteristic of effective leaders?', 'multiple_choice', '2026-04-16 10:47:38'),
(134, 3, 0, 0, 'What do leaders primarily do to achieve organizational success?', 'multiple_choice', '2026-04-16 10:47:38');

-- --------------------------------------------------------

--
-- Table structure for table `saq_reevaluation_requests`
--

CREATE TABLE `saq_reevaluation_requests` (
  `id` int(11) NOT NULL,
  `response_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `reason` text NOT NULL,
  `status` enum('pending','reviewed','declined') DEFAULT 'pending',
  `requested_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `reviewed_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `search_logs`
--

CREATE TABLE `search_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `query` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `search_logs`
--

INSERT INTO `search_logs` (`id`, `user_id`, `query`, `created_at`) VALUES
(1, 1, 'Convolutional Neural Networks', '2026-04-01 20:00:18'),
(2, 1, 'Convolutional Neural Networks', '2026-04-01 20:01:09'),
(3, 1, 'Convolutional Neural Networks', '2026-04-01 20:01:17'),
(4, 1, 'Convolutional Neural Networks', '2026-04-01 20:01:51'),
(5, 2, 'Public Speaking in Political Science', '2026-04-09 07:03:53'),
(6, 2, 'Public Speaking in Political Science', '2026-04-09 07:04:01'),
(7, 2, 'Communication Skills and Political Science', '2026-04-09 07:06:24'),
(8, 2, 'Communication Skills and Political Science', '2026-04-09 07:06:37'),
(9, 2, 'Communication Skills and Political Science', '2026-04-09 07:06:55'),
(10, 2, 'Crash Course for New Principal on Leadership Skills', '2026-04-16 10:43:55'),
(11, 2, 'Crash Course for New Principal on Leadership Skills', '2026-04-16 10:44:05');

-- --------------------------------------------------------

--
-- Table structure for table `short_answer_questions`
--

CREATE TABLE `short_answer_questions` (
  `id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `module_index` int(11) NOT NULL,
  `question_text` text NOT NULL,
  `question_type` enum('essay','short_answer') DEFAULT 'short_answer',
  `max_score` int(11) DEFAULT 10,
  `rubric` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`rubric`)),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `short_answer_questions`
--

INSERT INTO `short_answer_questions` (`id`, `course_id`, `module_index`, `question_text`, `question_type`, `max_score`, `rubric`, `created_at`) VALUES
(1, 1, 0, 'Explain how the convolutional and pooling layers in a CNN architecture enable the network to learn spatial hierarchies of features from images, and discuss the implications of this for image classification tasks.', 'short_answer', 10, '{\"criterion_1\": \"Clear explanation of convolutional and pooling layers\", \"criterion_2\": \"Description of how these layers learn spatial hierarchies of features\", \"criterion_3\": \"Discussion of implications for image classification tasks\"}', '2026-04-09 06:20:01'),
(2, 1, 0, 'Compare and contrast the architectures of LeNet and AlexNet, including the number of layers, types of layers used, and the impact on performance for image classification tasks.', 'short_answer', 10, '{\"criterion_1\": \"Accurate description of LeNet and AlexNet architectures\", \"criterion_2\": \"Comparison of key differences between the two architectures\", \"criterion_3\": \"Analysis of the impact on performance for image classification tasks\"}', '2026-04-09 06:20:01'),
(3, 1, 0, 'Describe a scenario where a CNN-based object detection system would be preferred over a traditional computer vision approach, and explain how the CNN architecture would be designed to address the specific requirements of the scenario.', 'short_answer', 10, '{\"criterion_1\": \"Clear description of the scenario and its requirements\", \"criterion_2\": \"Explanation of why a CNN-based approach is preferred\", \"criterion_3\": \"Description of the CNN architecture design for the scenario\", \"criterion_4\": \"Discussion of potential challenges and limitations\"}', '2026-04-09 06:20:01'),
(4, 2, 0, 'Analyze how a contemporary political issue, such as climate change, is framed by different political actors, and discuss the implications of these framing strategies for public opinion and policy outcomes.', 'short_answer', 10, '{\"criterion_1\": \"Clear and concise description of the political issue and its framing by different actors\", \"criterion_2\": \"Effective application of theoretical frameworks from the module to analyze the framing strategies\", \"criterion_3\": \"Thoughtful discussion of the implications for public opinion and policy outcomes, with supporting evidence\"}', '2026-04-09 07:13:41'),
(5, 2, 0, 'Compare and contrast the role of traditional media and social media in shaping political communication, using historical and contemporary examples to illustrate your points.', 'short_answer', 10, '{\"criterion_1\": \"Accurate and detailed comparison of traditional and social media in political communication\", \"criterion_2\": \"Effective use of historical and contemporary examples to support the comparison\", \"criterion_3\": \"Insightful analysis of the implications of the shift from traditional to social media for political communication\"}', '2026-04-09 07:13:41'),
(6, 2, 0, 'Discuss the ways in which the evolution of political communication over time has influenced the relationship between politicians, the media, and the public, and evaluate the impact of these changes on democratic processes.', 'short_answer', 10, '{\"criterion_1\": \"Clear and well-organized description of the historical development of political communication\", \"criterion_2\": \"Effective analysis of the impact of these changes on the relationship between politicians, media, and the public\", \"criterion_3\": \"Thoughtful evaluation of the implications for democratic processes, with supporting evidence and arguments\"}', '2026-04-09 07:13:41'),
(7, 2, 1, 'Analyze the role of framing in crafting political messages. How can politicians use framing to influence public opinion, and what are the potential risks of using this technique?', 'short_answer', 10, '{\"criterion_1\": \"Clearly defines framing and its purpose in political messaging\", \"criterion_2\": \"Provides effective examples of how framing can influence public opinion\", \"criterion_3\": \"Discusses potential risks and limitations of using framing in political messaging\"}', '2026-04-11 05:40:45'),
(8, 2, 1, 'A politician is facing a crisis due to a scandal. Describe the key components of an effective crisis communication strategy in this situation, including the role of media relations and message crafting.', 'short_answer', 10, '{\"criterion_1\": \"Identifies key components of an effective crisis communication strategy\", \"criterion_2\": \"Explains the importance of media relations in crisis communication\", \"criterion_3\": \"Discusses how message crafting can be used to mitigate the crisis\"}', '2026-04-11 05:40:45'),
(9, 2, 1, 'Compare and contrast the communication strategies used by politicians in building relationships with traditional media outlets versus social media platforms. How do these strategies impact the politician\'s ability to reach their target audience?', 'short_answer', 10, '{\"criterion_1\": \"Clearly describes the differences between traditional and social media communication strategies\", \"criterion_2\": \"Analyzes the impact of each strategy on reaching the target audience\", \"criterion_3\": \"Evaluates the effectiveness of each strategy in achieving political goals\"}', '2026-04-11 05:40:45'),
(10, 2, 2, 'Analyze how liberal and conservative ideologies influence the framing of economic policies in political communication, and discuss the implications of these differences for public perception.', 'short_answer', 10, '{\"criterion_1\": \"Clear and concise explanation of key differences between liberal and conservative ideologies in the context of economic policy framing\", \"criterion_2\": \"Effective analysis of how these ideological differences impact political communication strategies\", \"criterion_3\": \"Thoughtful discussion of the implications for public perception, including potential consequences for political engagement and decision-making\"}', '2026-04-11 05:48:43'),
(11, 2, 2, 'Compare and contrast the role of media in socialist and liberal political systems, considering how each ideology\'s principles shape the relationship between media, government, and the public.', 'short_answer', 10, '{\"criterion_1\": \"Accurate description of the principles of socialist and liberal ideologies as they relate to media and political communication\", \"criterion_2\": \"Insightful comparison of the role of media in each system, including differences in ownership, regulation, and access\", \"criterion_3\": \"Nuanced discussion of the implications of these differences for democratic participation and the dissemination of information\"}', '2026-04-11 05:48:43'),
(12, 2, 2, 'Design a political communication strategy for a socialist party in a country with a predominantly liberal political culture, considering how to effectively convey socialist ideals and policies to a skeptical audience.', 'short_answer', 10, '{\"criterion_1\": \"Clear understanding of socialist ideals and their application to political communication in a liberal context\", \"criterion_2\": \"Creative and strategic approach to conveying socialist policies and values to a liberal audience\", \"criterion_3\": \"Effective consideration of potential challenges and obstacles, including how to address criticisms and misconceptions about socialism\"}', '2026-04-11 05:48:43'),
(13, 2, 3, 'Analyze how traditional media and social media differently influence political discourse, providing examples of each.', 'short_answer', 10, '{\"criterion_1\": \"Clear distinction between traditional and social media\'s influence on political discourse\", \"criterion_2\": \"Effective use of relevant examples to support the analysis\", \"criterion_3\": \"Depth of understanding of the module concepts demonstrated in the comparison\"}', '2026-04-11 05:57:06'),
(14, 2, 3, 'Discuss the implications of media bias on political communication, considering the role of both traditional and social media.', 'short_answer', 10, '{\"criterion_1\": \"Comprehensive understanding of media bias and its impact on political communication\", \"criterion_2\": \"Critical evaluation of how media bias affects political discourse in different media platforms\", \"criterion_3\": \"Clarity and coherence in presenting the discussion\", \"criterion_4\": \"Relevance of examples or cases used to illustrate the implications\"}', '2026-04-11 05:57:06'),
(15, 2, 3, 'Explain how politicians might strategically use social media to counterbalance the influence of traditional media, considering the potential benefits and drawbacks.', 'short_answer', 10, '{\"criterion_1\": \"Understanding of the strategic use of social media in political communication\", \"criterion_2\": \"Identification of potential benefits of using social media to counter traditional media influence\", \"criterion_3\": \"Analysis of potential drawbacks or challenges in this strategy\", \"criterion_4\": \"Quality of reasoning and logical flow in the explanation\"}', '2026-04-11 05:57:06'),
(16, 2, 4, 'Analyze a recent political campaign that successfully utilized social media to mobilize supporters. What strategies did the campaign employ, and how did they contribute to the campaign\'s overall success?', 'short_answer', 10, '{\"criterion_1\": \"Clearly identifies and describes the campaign\'s social media strategies\", \"criterion_2\": \"Effectively analyzes the impact of these strategies on the campaign\'s success\", \"criterion_3\": \"Demonstrates understanding of key concepts in political communication, such as audience engagement and message tailoring\"}', '2026-04-11 06:06:16'),
(17, 2, 4, 'A national crisis has occurred, and the government must communicate with the public to provide updates and instructions. What communication strategies would you recommend, and how would you evaluate their effectiveness?', 'short_answer', 10, '{\"criterion_1\": \"Provides a clear and comprehensive communication plan for the crisis situation\", \"criterion_2\": \"Demonstrates understanding of the importance of transparency, empathy, and clarity in crisis communication\", \"criterion_3\": \"Effectively discusses methods for evaluating the effectiveness of the communication strategies\", \"criterion_4\": \"Shows ability to think critically about the role of emerging trends and technologies in crisis communication\"}', '2026-04-11 06:06:16'),
(18, 2, 4, 'How might the increasing use of artificial intelligence and data analytics in political communication change the way politicians engage with their constituents? What are the potential benefits and drawbacks of these emerging trends?', 'short_answer', 10, '{\"criterion_1\": \"Clearly describes the potential impact of AI and data analytics on political communication\", \"criterion_2\": \"Effectively weighs the potential benefits and drawbacks of these emerging trends\", \"criterion_3\": \"Demonstrates understanding of key concepts in political communication, such as personalization and micro-targeting\"}', '2026-04-11 06:06:16');

-- --------------------------------------------------------

--
-- Table structure for table `student_final_responses`
--

CREATE TABLE `student_final_responses` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `final_assessment_id` int(11) NOT NULL,
  `answer_text` longtext NOT NULL,
  `score` decimal(5,2) DEFAULT NULL,
  `feedback` text DEFAULT NULL,
  `is_graded` tinyint(1) DEFAULT 0,
  `graded_by_user_id` int(11) DEFAULT NULL,
  `submitted_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `graded_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `student_quiz_responses`
--

CREATE TABLE `student_quiz_responses` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `module_index` int(11) NOT NULL,
  `lesson_index` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  `selected_option_id` int(11) DEFAULT NULL,
  `short_answer_text` text DEFAULT NULL,
  `is_correct` tinyint(1) DEFAULT 0,
  `score` decimal(5,2) DEFAULT 0.00,
  `attempted_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `student_quiz_responses`
--

INSERT INTO `student_quiz_responses` (`id`, `user_id`, `course_id`, `module_index`, `lesson_index`, `question_id`, `selected_option_id`, `short_answer_text`, `is_correct`, `score`, `attempted_at`) VALUES
(1, 1, 1, 0, 0, 2, 1, NULL, 0, 0.00, '2026-04-08 15:16:18'),
(2, 1, 1, 0, 0, 3, 6, NULL, 0, 0.00, '2026-04-08 15:16:18'),
(3, 1, 1, 0, 0, 4, 9, NULL, 0, 0.00, '2026-04-08 15:16:18'),
(4, 1, 1, 0, 0, 5, 13, NULL, 0, 0.00, '2026-04-08 15:16:18'),
(5, 1, 1, 0, 0, 6, 17, NULL, 0, 0.00, '2026-04-08 15:16:18'),
(6, 1, 1, 0, 0, 2, 3, NULL, 1, 1.00, '2026-04-08 15:23:55'),
(7, 1, 1, 0, 0, 3, 8, NULL, 1, 1.00, '2026-04-08 15:23:55'),
(8, 1, 1, 0, 0, 4, 11, NULL, 1, 1.00, '2026-04-08 15:23:55'),
(9, 1, 1, 0, 0, 5, 14, NULL, 1, 1.00, '2026-04-08 15:23:55'),
(10, 1, 1, 0, 0, 6, 19, NULL, 1, 1.00, '2026-04-08 15:23:55'),
(11, 1, 1, 0, 0, 2, 2, NULL, 0, 0.00, '2026-04-08 17:08:08'),
(12, 1, 1, 0, 0, 3, 8, NULL, 1, 1.00, '2026-04-08 17:08:08'),
(13, 1, 1, 0, 0, 4, 11, NULL, 1, 1.00, '2026-04-08 17:08:08'),
(14, 1, 1, 0, 0, 5, 14, NULL, 1, 1.00, '2026-04-08 17:08:08'),
(15, 1, 1, 0, 0, 6, 20, NULL, 0, 0.00, '2026-04-08 17:08:08'),
(16, 1, 1, 0, 0, 7, 22, NULL, 0, 0.00, '2026-04-08 17:08:08'),
(17, 1, 1, 0, 0, 8, 28, NULL, 1, 1.00, '2026-04-08 17:08:08'),
(18, 1, 1, 0, 0, 9, 29, NULL, 0, 0.00, '2026-04-08 17:08:08'),
(19, 1, 1, 0, 0, 10, 36, NULL, 0, 0.00, '2026-04-08 17:08:08'),
(20, 1, 1, 0, 0, 11, 37, NULL, 0, 0.00, '2026-04-08 17:08:08'),
(21, 1, 1, 0, 0, 12, 42, NULL, 0, 0.00, '2026-04-08 17:08:08'),
(22, 1, 1, 0, 0, 13, 45, NULL, 0, 0.00, '2026-04-08 17:08:08'),
(23, 1, 1, 0, 0, 14, 52, NULL, 1, 1.00, '2026-04-08 17:08:08'),
(24, 1, 1, 0, 0, 15, 55, NULL, 1, 1.00, '2026-04-08 17:08:08'),
(25, 1, 1, 0, 0, 17, 61, NULL, 0, 0.00, '2026-04-08 17:08:08'),
(26, 1, 1, 0, 0, 18, 66, NULL, 1, 1.00, '2026-04-08 17:08:08'),
(27, 1, 1, 0, 0, 2, 2, NULL, 0, 0.00, '2026-04-08 17:21:32'),
(28, 1, 1, 0, 0, 3, 8, NULL, 1, 1.00, '2026-04-08 17:21:32'),
(29, 1, 1, 0, 0, 4, 10, NULL, 0, 0.00, '2026-04-08 17:21:32'),
(30, 1, 1, 0, 0, 5, 14, NULL, 1, 1.00, '2026-04-08 17:21:32'),
(31, 1, 1, 0, 0, 6, 19, NULL, 1, 1.00, '2026-04-08 17:21:32'),
(32, 1, 1, 0, 0, 7, 22, NULL, 0, 0.00, '2026-04-08 17:21:32'),
(33, 1, 1, 0, 0, 8, 27, NULL, 0, 0.00, '2026-04-08 17:21:32'),
(34, 1, 1, 0, 0, 9, 29, NULL, 0, 0.00, '2026-04-08 17:21:32'),
(35, 1, 1, 0, 0, 10, 34, NULL, 0, 0.00, '2026-04-08 17:21:32'),
(36, 1, 1, 0, 0, 11, 38, NULL, 0, 0.00, '2026-04-08 17:21:32'),
(37, 1, 1, 0, 0, 12, 42, NULL, 0, 0.00, '2026-04-08 17:21:32'),
(38, 1, 1, 0, 0, 13, 46, NULL, 0, 0.00, '2026-04-08 17:21:32'),
(39, 1, 1, 0, 0, 14, 50, NULL, 0, 0.00, '2026-04-08 17:21:32'),
(40, 1, 1, 0, 0, 15, 56, NULL, 0, 0.00, '2026-04-08 17:21:32'),
(41, 1, 1, 0, 0, 16, 59, NULL, 0, 0.00, '2026-04-08 17:21:32'),
(42, 1, 1, 0, 0, 17, 61, NULL, 0, 0.00, '2026-04-08 17:21:32'),
(43, 1, 1, 0, 0, 18, 66, NULL, 1, 1.00, '2026-04-08 17:21:32'),
(44, 1, 1, 0, 0, 19, 71, NULL, 1, 1.00, '2026-04-08 17:21:32'),
(45, 1, 1, 0, 0, 20, 76, NULL, 0, 0.00, '2026-04-08 17:21:32'),
(46, 1, 1, 0, 0, 21, 80, NULL, 0, 0.00, '2026-04-08 17:21:32'),
(47, 1, 1, 0, 0, 22, 81, NULL, 0, 0.00, '2026-04-08 17:21:32'),
(48, 1, 1, 0, 1, 24, 91, NULL, 1, 1.00, '2026-04-09 05:56:24'),
(49, 1, 1, 0, 1, 25, 96, NULL, 1, 1.00, '2026-04-09 05:56:24'),
(50, 1, 1, 0, 1, 26, 100, NULL, 1, 1.00, '2026-04-09 05:56:24'),
(51, 1, 1, 0, 2, 27, 102, NULL, 1, 1.00, '2026-04-09 06:09:20'),
(52, 1, 1, 0, 2, 28, 106, NULL, 1, 1.00, '2026-04-09 06:09:20'),
(53, 1, 1, 0, 2, 29, 111, NULL, 1, 1.00, '2026-04-09 06:09:20'),
(54, 1, 1, 0, 2, 30, 116, NULL, 1, 1.00, '2026-04-09 06:09:20'),
(55, 2, 2, 0, 0, 31, 118, NULL, 0, 0.00, '2026-04-09 07:09:06'),
(56, 2, 2, 0, 0, 32, 122, NULL, 1, 1.00, '2026-04-09 07:09:06'),
(57, 2, 2, 0, 0, 33, 125, NULL, 0, 0.00, '2026-04-09 07:09:06'),
(58, 2, 2, 0, 0, 34, 130, NULL, 0, 0.00, '2026-04-09 07:09:06'),
(59, 2, 2, 0, 1, 35, 135, NULL, 0, 0.00, '2026-04-09 07:10:59'),
(60, 2, 2, 0, 1, 36, 137, NULL, 0, 0.00, '2026-04-09 07:10:59'),
(61, 2, 2, 0, 1, 37, 141, NULL, 0, 0.00, '2026-04-09 07:10:59'),
(62, 2, 2, 0, 1, 38, 147, NULL, 0, 0.00, '2026-04-09 07:10:59'),
(63, 2, 2, 0, 2, 39, 149, NULL, 0, 0.00, '2026-04-09 07:12:57'),
(64, 2, 2, 0, 2, 40, 153, NULL, 0, 0.00, '2026-04-09 07:12:57'),
(65, 2, 2, 0, 2, 41, 159, NULL, 0, 0.00, '2026-04-09 07:12:57'),
(66, 2, 2, 0, 2, 42, 161, NULL, 0, 0.00, '2026-04-09 07:12:57'),
(67, 2, 1, 0, 0, 2, 2, NULL, 0, 0.00, '2026-04-09 09:21:15'),
(68, 2, 1, 0, 0, 3, 7, NULL, 0, 0.00, '2026-04-09 09:21:15'),
(69, 2, 1, 0, 0, 5, 13, NULL, 0, 0.00, '2026-04-09 09:21:15'),
(70, 2, 1, 0, 0, 7, 21, NULL, 0, 0.00, '2026-04-09 09:21:15'),
(71, 2, 1, 0, 0, 8, 28, NULL, 1, 1.00, '2026-04-09 09:21:15'),
(72, 2, 1, 0, 0, 10, 33, NULL, 0, 0.00, '2026-04-09 09:21:15'),
(73, 2, 1, 0, 0, 13, 46, NULL, 0, 0.00, '2026-04-09 09:21:15'),
(74, 2, 1, 0, 0, 15, 53, NULL, 0, 0.00, '2026-04-09 09:21:15'),
(75, 2, 1, 0, 0, 16, 60, NULL, 0, 0.00, '2026-04-09 09:21:15'),
(76, 2, 1, 0, 0, 18, 65, NULL, 0, 0.00, '2026-04-09 09:21:15'),
(77, 2, 1, 0, 0, 19, 71, NULL, 1, 1.00, '2026-04-09 09:21:15'),
(78, 2, 1, 0, 0, 21, 77, NULL, 0, 0.00, '2026-04-09 09:21:15'),
(79, 2, 1, 0, 0, 43, 167, NULL, 1, 1.00, '2026-04-09 09:21:15'),
(80, 2, 1, 0, 0, 44, 169, NULL, 0, 0.00, '2026-04-09 09:21:15'),
(81, 2, 1, 0, 0, 45, 176, NULL, 0, 0.00, '2026-04-09 09:21:15'),
(82, 2, 1, 0, 0, 46, 178, NULL, 0, 0.00, '2026-04-09 09:21:15'),
(83, 2, 1, 0, 0, 2, 1, NULL, 0, 0.00, '2026-04-09 09:33:38'),
(84, 2, 1, 0, 0, 3, 8, NULL, 1, 1.00, '2026-04-09 09:33:38'),
(85, 2, 1, 0, 0, 4, 12, NULL, 0, 0.00, '2026-04-09 09:33:38'),
(86, 2, 1, 0, 0, 5, 13, NULL, 0, 0.00, '2026-04-09 09:33:38'),
(87, 2, 1, 0, 0, 6, 20, NULL, 0, 0.00, '2026-04-09 09:33:38'),
(88, 2, 1, 0, 0, 7, 24, NULL, 0, 0.00, '2026-04-09 09:33:38'),
(89, 2, 1, 0, 0, 8, 25, NULL, 0, 0.00, '2026-04-09 09:33:38'),
(90, 2, 1, 0, 0, 9, 32, NULL, 1, 1.00, '2026-04-09 09:33:38'),
(91, 2, 1, 0, 0, 10, 33, NULL, 0, 0.00, '2026-04-09 09:33:38'),
(92, 2, 1, 0, 0, 11, 40, NULL, 0, 0.00, '2026-04-09 09:33:38'),
(93, 2, 1, 0, 0, 13, 45, NULL, 0, 0.00, '2026-04-09 09:33:38'),
(94, 2, 1, 0, 0, 14, 52, NULL, 1, 1.00, '2026-04-09 09:33:38'),
(95, 2, 1, 0, 0, 16, 58, NULL, 1, 1.00, '2026-04-09 09:33:38'),
(96, 2, 1, 0, 0, 17, 64, NULL, 1, 1.00, '2026-04-09 09:33:38'),
(97, 2, 1, 0, 0, 18, 68, NULL, 0, 0.00, '2026-04-09 09:33:38'),
(98, 2, 1, 0, 0, 19, 69, NULL, 0, 0.00, '2026-04-09 09:33:38'),
(99, 2, 1, 0, 0, 20, 76, NULL, 0, 0.00, '2026-04-09 09:33:38'),
(100, 2, 1, 0, 0, 22, 82, NULL, 0, 0.00, '2026-04-09 09:33:38'),
(101, 2, 1, 0, 0, 43, 168, NULL, 0, 0.00, '2026-04-09 09:33:38'),
(102, 2, 1, 0, 0, 44, 172, NULL, 0, 0.00, '2026-04-09 09:33:38'),
(103, 2, 1, 0, 0, 45, 173, NULL, 0, 0.00, '2026-04-09 09:33:38'),
(104, 2, 1, 0, 0, 46, 180, NULL, 0, 0.00, '2026-04-09 09:33:38'),
(105, 2, 2, 1, 0, 47, 181, NULL, 0, 0.00, '2026-04-11 05:31:17'),
(106, 2, 2, 1, 0, 48, 186, NULL, 0, 0.00, '2026-04-11 05:31:17'),
(107, 2, 2, 1, 0, 49, 192, NULL, 0, 0.00, '2026-04-11 05:31:17'),
(108, 2, 2, 1, 0, 50, 195, NULL, 0, 0.00, '2026-04-11 05:31:17'),
(109, 2, 2, 1, 1, 51, 198, NULL, 1, 1.00, '2026-04-11 05:33:33'),
(110, 2, 2, 1, 1, 52, 204, NULL, 0, 0.00, '2026-04-11 05:33:33'),
(111, 2, 2, 1, 1, 53, 205, NULL, 0, 0.00, '2026-04-11 05:33:33'),
(112, 2, 2, 1, 1, 54, 209, NULL, 0, 0.00, '2026-04-11 05:33:33'),
(113, 2, 2, 1, 1, 51, 197, NULL, 0, 0.00, '2026-04-11 05:34:24'),
(114, 2, 2, 1, 1, 52, 204, NULL, 0, 0.00, '2026-04-11 05:34:24'),
(115, 2, 2, 1, 1, 53, 208, NULL, 0, 0.00, '2026-04-11 05:34:24'),
(116, 2, 2, 1, 1, 54, 209, NULL, 0, 0.00, '2026-04-11 05:34:24'),
(117, 2, 2, 1, 0, 47, 181, NULL, 0, 0.00, '2026-04-11 05:35:02'),
(118, 2, 2, 1, 0, 48, 187, NULL, 1, 1.00, '2026-04-11 05:35:02'),
(119, 2, 2, 1, 0, 49, 192, NULL, 0, 0.00, '2026-04-11 05:35:02'),
(120, 2, 2, 1, 0, 50, 193, NULL, 0, 0.00, '2026-04-11 05:35:02'),
(121, 2, 2, 1, 0, 47, 181, NULL, 0, 0.00, '2026-04-11 05:38:14'),
(122, 2, 2, 1, 0, 48, 188, NULL, 0, 0.00, '2026-04-11 05:38:14'),
(123, 2, 2, 1, 0, 49, 192, NULL, 0, 0.00, '2026-04-11 05:38:14'),
(124, 2, 2, 1, 0, 50, 193, NULL, 0, 0.00, '2026-04-11 05:38:14'),
(125, 2, 2, 1, 2, 55, 213, NULL, 0, 0.00, '2026-04-11 05:40:14'),
(126, 2, 2, 1, 2, 56, 220, NULL, 0, 0.00, '2026-04-11 05:40:14'),
(127, 2, 2, 1, 2, 58, 225, NULL, 0, 0.00, '2026-04-11 05:40:14'),
(128, 2, 2, 1, 2, 59, 232, NULL, 0, 0.00, '2026-04-11 05:40:14'),
(129, 2, 2, 1, 2, 61, 237, NULL, 0, 0.00, '2026-04-11 05:40:14'),
(130, 2, 2, 1, 2, 62, 242, NULL, 1, 1.00, '2026-04-11 05:40:14'),
(131, 2, 2, 2, 0, 63, 245, NULL, 0, 0.00, '2026-04-11 05:43:13'),
(132, 2, 2, 2, 0, 64, 252, NULL, 0, 0.00, '2026-04-11 05:43:13'),
(133, 2, 2, 2, 0, 65, 256, NULL, 0, 0.00, '2026-04-11 05:43:13'),
(134, 2, 2, 2, 0, 66, 257, NULL, 0, 0.00, '2026-04-11 05:43:13'),
(135, 2, 2, 2, 1, 67, 261, NULL, 0, 0.00, '2026-04-11 05:46:13'),
(136, 2, 2, 2, 1, 68, 266, NULL, 0, 0.00, '2026-04-11 05:46:13'),
(137, 2, 2, 2, 1, 69, 272, NULL, 0, 0.00, '2026-04-11 05:46:13'),
(138, 2, 2, 2, 1, 70, 273, NULL, 0, 0.00, '2026-04-11 05:46:13'),
(139, 2, 2, 2, 1, 71, 279, NULL, 0, 0.00, '2026-04-11 05:46:13'),
(140, 2, 2, 2, 1, 72, 284, NULL, 0, 0.00, '2026-04-11 05:46:13'),
(141, 2, 2, 2, 1, 73, 288, NULL, 0, 0.00, '2026-04-11 05:46:13'),
(142, 2, 2, 2, 1, 74, 289, NULL, 0, 0.00, '2026-04-11 05:46:13'),
(143, 2, 2, 2, 2, 75, 293, NULL, 0, 0.00, '2026-04-11 05:48:12'),
(144, 2, 2, 2, 2, 76, 300, NULL, 0, 0.00, '2026-04-11 05:48:12'),
(145, 2, 2, 2, 2, 77, 304, NULL, 0, 0.00, '2026-04-11 05:48:12'),
(146, 2, 2, 2, 2, 78, 305, NULL, 0, 0.00, '2026-04-11 05:48:12'),
(147, 2, 2, 3, 0, 79, 309, NULL, 0, 0.00, '2026-04-11 05:51:19'),
(148, 2, 2, 3, 0, 80, 314, NULL, 1, 1.00, '2026-04-11 05:51:19'),
(149, 2, 2, 3, 0, 81, 320, NULL, 0, 0.00, '2026-04-11 05:51:19'),
(150, 2, 2, 3, 0, 82, 321, NULL, 0, 0.00, '2026-04-11 05:51:19'),
(151, 2, 2, 3, 0, 83, 326, NULL, 1, 1.00, '2026-04-11 05:51:19'),
(152, 2, 2, 3, 0, 84, 329, NULL, 0, 0.00, '2026-04-11 05:51:19'),
(153, 2, 2, 3, 0, 85, 334, NULL, 0, 0.00, '2026-04-11 05:51:19'),
(154, 2, 2, 3, 0, 86, 339, NULL, 0, 0.00, '2026-04-11 05:51:19'),
(155, 2, 2, 3, 1, 87, 341, NULL, 0, 0.00, '2026-04-11 05:53:06'),
(156, 2, 2, 3, 1, 88, 348, NULL, 1, 1.00, '2026-04-11 05:53:06'),
(157, 2, 2, 3, 1, 89, 352, NULL, 0, 0.00, '2026-04-11 05:53:06'),
(158, 2, 2, 3, 1, 90, 353, NULL, 0, 0.00, '2026-04-11 05:53:06'),
(159, 2, 2, 3, 2, 91, 357, NULL, 0, 0.00, '2026-04-11 05:56:31'),
(160, 2, 2, 3, 2, 92, 364, NULL, 0, 0.00, '2026-04-11 05:56:31'),
(161, 2, 2, 3, 2, 93, 368, NULL, 0, 0.00, '2026-04-11 05:56:31'),
(162, 2, 2, 3, 2, 94, 369, NULL, 0, 0.00, '2026-04-11 05:56:31'),
(163, 2, 2, 3, 2, 95, 376, NULL, 0, 0.00, '2026-04-11 05:56:31'),
(164, 2, 2, 3, 2, 97, 381, NULL, 0, 0.00, '2026-04-11 05:56:31'),
(165, 2, 2, 3, 2, 98, 388, NULL, 0, 0.00, '2026-04-11 05:56:31'),
(166, 2, 2, 4, 0, 99, 390, NULL, 0, 0.00, '2026-04-11 06:00:11'),
(167, 2, 2, 4, 0, 100, 396, NULL, 0, 0.00, '2026-04-11 06:00:11'),
(168, 2, 2, 4, 0, 102, 401, NULL, 1, 1.00, '2026-04-11 06:00:11'),
(169, 2, 2, 4, 0, 103, 405, NULL, 0, 0.00, '2026-04-11 06:00:11'),
(170, 2, 2, 4, 0, 104, 409, NULL, 0, 0.00, '2026-04-11 06:00:11'),
(171, 2, 2, 4, 0, 105, 416, NULL, 1, 1.00, '2026-04-11 06:00:11'),
(172, 2, 2, 4, 0, 106, 418, NULL, 1, 1.00, '2026-04-11 06:00:11'),
(173, 2, 2, 4, 1, 107, 421, NULL, 0, 0.00, '2026-04-11 06:02:46'),
(174, 2, 2, 4, 1, 108, 428, NULL, 0, 0.00, '2026-04-11 06:02:46'),
(175, 2, 2, 4, 1, 109, 432, NULL, 0, 0.00, '2026-04-11 06:02:46'),
(176, 2, 2, 4, 1, 110, 433, NULL, 0, 0.00, '2026-04-11 06:02:46'),
(177, 2, 2, 4, 1, 111, 440, NULL, 0, 0.00, '2026-04-11 06:02:46'),
(178, 2, 2, 4, 1, 113, 445, NULL, 0, 0.00, '2026-04-11 06:02:46'),
(179, 2, 2, 4, 1, 114, 450, NULL, 0, 0.00, '2026-04-11 06:02:46'),
(180, 2, 2, 4, 2, 119, 469, NULL, 0, 0.00, '2026-04-11 06:05:25'),
(181, 2, 2, 4, 2, 120, 476, NULL, 0, 0.00, '2026-04-11 06:05:25'),
(182, 2, 2, 4, 2, 121, 480, NULL, 0, 0.00, '2026-04-11 06:05:25'),
(183, 2, 2, 4, 2, 122, 482, NULL, 1, 1.00, '2026-04-11 06:05:25'),
(184, 2, 2, 4, 2, 124, 489, NULL, 0, 0.00, '2026-04-11 06:05:25'),
(185, 2, 2, 4, 2, 125, 495, NULL, 1, 1.00, '2026-04-11 06:05:25'),
(186, 2, 2, 4, 2, 126, 500, NULL, 0, 0.00, '2026-04-11 06:05:25'),
(187, 2, 3, 0, 0, 131, 520, NULL, 0, 0.00, '2026-04-16 10:48:00'),
(188, 2, 3, 0, 0, 132, 521, NULL, 0, 0.00, '2026-04-16 10:48:00'),
(189, 2, 3, 0, 0, 133, 525, NULL, 0, 0.00, '2026-04-16 10:48:00'),
(190, 2, 3, 0, 0, 134, 529, NULL, 0, 0.00, '2026-04-16 10:48:00');

-- --------------------------------------------------------

--
-- Table structure for table `student_saq_responses`
--

CREATE TABLE `student_saq_responses` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `module_index` int(11) NOT NULL,
  `saq_id` int(11) NOT NULL,
  `answer_text` longtext NOT NULL,
  `score` decimal(5,2) DEFAULT NULL,
  `feedback` text DEFAULT NULL,
  `is_graded` tinyint(1) DEFAULT 0,
  `graded_by_user_id` int(11) DEFAULT NULL,
  `submitted_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `graded_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `student_saq_responses`
--

INSERT INTO `student_saq_responses` (`id`, `user_id`, `course_id`, `module_index`, `saq_id`, `answer_text`, `score`, `feedback`, `is_graded`, `graded_by_user_id`, `submitted_at`, `graded_at`) VALUES
(1, 1, 1, 0, 1, 'Explain how the convolutional and pooling layers in a CNN architecture enable the network to learn spatial hierarchies of features from images, and discuss the implications of this for image classification tasks.', 0.00, 'Unable to grade automatically. Please review manually.', 1, NULL, '2026-04-09 06:52:23', '2026-04-09 06:52:24'),
(2, 1, 1, 0, 2, 'Compare and contrast the architectures of LeNet and AlexNet, including the number of layers, types of layers used, and the impact on performance for image classification tasks.', 0.00, 'Unable to grade automatically. Please review manually.', 1, NULL, '2026-04-09 06:52:24', '2026-04-09 06:52:24'),
(3, 1, 1, 0, 3, 'Describe a scenario where a CNN-based object detection system would be preferred over a traditional computer vision approach, and explain how the CNN architecture would be designed to address the specific requirements of the scenario.', 0.00, 'Unable to grade automatically. Please review manually.', 1, NULL, '2026-04-09 06:52:24', '2026-04-09 06:52:24'),
(13, 2, 2, 0, 4, 'Analyze how a contemporary political issue, such as climate change, is framed by different political actors, and discuss the implications of these framing strategies for public opinion and policy outcomes.', 0.00, 'Unable to grade automatically. Please review manually.', 1, NULL, '2026-04-09 07:14:07', '2026-04-09 07:14:07'),
(14, 2, 2, 0, 5, 'Compare and contrast the role of traditional media and social media in shaping political communication, using historical and contemporary examples to illustrate your points.', 0.00, 'Unable to grade automatically. Please review manually.', 1, NULL, '2026-04-09 07:14:07', '2026-04-09 07:14:07'),
(15, 2, 2, 0, 6, 'Discuss the ways in which the evolution of political communication over time has influenced the relationship between politicians, the media, and the public, and evaluate the impact of these changes on democratic processes.', 0.00, 'Unable to grade automatically. Please review manually.', 1, NULL, '2026-04-09 07:14:07', '2026-04-09 07:14:07'),
(16, 2, 2, 1, 7, 'Analyze the role of framing in crafting political messages. How can politicians use framing to influence public opinion, and what are the potential risks of using this technique?', 0.00, 'Unable to grade automatically. Please review manually.', 1, NULL, '2026-04-11 05:41:07', '2026-04-11 05:41:07'),
(17, 2, 2, 1, 8, 'A politician is facing a crisis due to a scandal. Describe the key components of an effective crisis communication strategy in this situation, including the role of media relations and message crafting.', 0.00, 'Unable to grade automatically. Please review manually.', 1, NULL, '2026-04-11 05:41:07', '2026-04-11 05:41:07'),
(18, 2, 2, 1, 9, 'Compare and contrast the communication strategies used by politicians in building relationships with traditional media outlets versus social media platforms. How do these strategies impact the politician\'s ability to reach their target audience?', 0.00, 'Unable to grade automatically. Please review manually.', 1, NULL, '2026-04-11 05:41:07', '2026-04-11 05:41:07'),
(19, 2, 2, 2, 10, 'Analyze how liberal and conservative ideologies influence the framing of economic policies in political communication, and discuss the implications of these differences for public perception.', 0.00, 'Unable to grade automatically. Please review manually.', 1, NULL, '2026-04-11 05:49:06', '2026-04-11 05:49:06'),
(20, 2, 2, 2, 11, 'Compare and contrast the role of media in socialist and liberal political systems, considering how each ideology\'s principles shape the relationship between media, government, and the public.', 0.00, 'Unable to grade automatically. Please review manually.', 1, NULL, '2026-04-11 05:49:06', '2026-04-11 05:49:06'),
(21, 2, 2, 2, 12, 'Design a political communication strategy for a socialist party in a country with a predominantly liberal political culture, considering how to effectively convey socialist ideals and policies to a skeptical audience.', 0.00, 'Unable to grade automatically. Please review manually.', 1, NULL, '2026-04-11 05:49:06', '2026-04-11 05:49:06'),
(22, 2, 2, 3, 13, 'Analyze how traditional media and social media differently influence political discourse, providing examples of each.', 0.00, 'Unable to grade automatically. Please review manually.', 1, NULL, '2026-04-11 05:57:28', '2026-04-11 05:57:28'),
(23, 2, 2, 3, 14, 'Discuss the implications of media bias on political communication, considering the role of both traditional and social media.', 0.00, 'Unable to grade automatically. Please review manually.', 1, NULL, '2026-04-11 05:57:28', '2026-04-11 05:57:28'),
(24, 2, 2, 3, 15, 'Explain how politicians might strategically use social media to counterbalance the influence of traditional media, considering the potential benefits and drawbacks.', 0.00, 'Unable to grade automatically. Please review manually.', 1, NULL, '2026-04-11 05:57:28', '2026-04-11 05:57:28'),
(25, 2, 2, 4, 16, 'Analyze a recent political campaign that successfully utilized social media to mobilize supporters. What strategies did the campaign employ, and how did they contribute to the campaign\'s overall success?', 0.00, 'Unable to grade automatically. Please review manually.', 1, NULL, '2026-04-11 06:06:39', '2026-04-11 06:06:39'),
(26, 2, 2, 4, 17, 'A national crisis has occurred, and the government must communicate with the public to provide updates and instructions. What communication strategies would you recommend, and how would you evaluate their effectiveness?', 0.00, 'Unable to grade automatically. Please review manually.', 1, NULL, '2026-04-11 06:06:39', '2026-04-11 06:06:39'),
(27, 2, 2, 4, 18, 'How might the increasing use of artificial intelligence and data analytics in political communication change the way politicians engage with their constituents? What are the potential benefits and drawbacks of these emerging trends?', 0.00, 'Unable to grade automatically. Please review manually.', 1, NULL, '2026-04-11 06:06:39', '2026-04-11 06:06:39');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `full_name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('student','instructor','admin') NOT NULL DEFAULT 'student',
  `expertise_domain` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `full_name`, `email`, `password_hash`, `role`, `expertise_domain`, `created_at`, `updated_at`) VALUES
(1, 'ATLELEHANG WESI', 'wezimosiuoa@gmail.com', 'scrypt:32768:8:1$UfLaxb1GTz1aZFD2$b4395a71bd5136854885da90f1635e9532ec3e272e731952c1e78f85a7f910e79d8f850dc1118e34ea5519450e355c25041687879c2ded5c869aed11a2d84a43', 'student', NULL, '2026-04-01 19:53:05', '2026-04-01 19:53:05'),
(2, 'TEBA ', 'TEBA@GMAIL.COM', 'scrypt:32768:8:1$AZuWSPY6UrXadjvB$f4b9b479e0bfdd9107be033d3f71227bac95115e21f8a9be253409642f82900565b44f6322b8da589e7c71b590918538ee2c1bf7cbbbb532e26288bddf9d2e0d', 'student', NULL, '2026-04-09 07:02:45', '2026-04-09 07:02:45');

-- --------------------------------------------------------

--
-- Table structure for table `user_preferences`
--

CREATE TABLE `user_preferences` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `level` varchar(50) DEFAULT 'Beginner',
  `preferred_domains` text DEFAULT NULL,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `domain` varchar(255) DEFAULT NULL,
  `topic` varchar(255) DEFAULT NULL,
  `goal` varchar(255) DEFAULT NULL,
  `duration` varchar(50) DEFAULT NULL,
  `learning_preference` varchar(255) DEFAULT NULL,
  `prior_knowledge` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_preferences`
--

INSERT INTO `user_preferences` (`id`, `user_id`, `level`, `preferred_domains`, `updated_at`, `domain`, `topic`, `goal`, `duration`, `learning_preference`, `prior_knowledge`) VALUES
(1, 6, 'Intermediate', '[\"Marketing\"]', '2026-03-02 01:52:44', NULL, NULL, NULL, NULL, NULL, NULL),
(5, 1, 'Advanced', NULL, '2026-04-01 20:00:54', 'Software Engineering', 'Convolutional Neural Networks ', 'Foundational Understanding', '6', 'Theory-Oriented', 'none '),
(6, 2, 'Advanced', NULL, '2026-04-09 07:04:45', 'Communication & Study Skills', 'Communication Skills and Political Science', 'Foundational Understanding', '6', 'Theory-Oriented', 'none ');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `certificates`
--
ALTER TABLE `certificates`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `certificate_code` (`certificate_code`),
  ADD KEY `course_id` (`course_id`),
  ADD KEY `idx_certificate` (`user_id`,`course_id`);

--
-- Indexes for table `courses`
--
ALTER TABLE `courses`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `content_hash` (`content_hash`),
  ADD KEY `fk_course_creator` (`created_by`),
  ADD KEY `idx_course_public` (`is_public`);

--
-- Indexes for table `course_completion_grades`
--
ALTER TABLE `course_completion_grades`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_course_grade` (`user_id`,`course_id`),
  ADD KEY `course_id` (`course_id`),
  ADD KEY `idx_course_grade` (`user_id`,`course_id`);

--
-- Indexes for table `course_feedback`
--
ALTER TABLE `course_feedback`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_user_course` (`course_id`,`user_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `enrollments`
--
ALTER TABLE `enrollments`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_user_course` (`user_id`,`course_id`),
  ADD KEY `idx_enrollment_user` (`user_id`),
  ADD KEY `idx_enrollment_course` (`course_id`);

--
-- Indexes for table `final_assessments`
--
ALTER TABLE `final_assessments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_final_assessment` (`course_id`);

--
-- Indexes for table `lesson_quiz_results`
--
ALTER TABLE `lesson_quiz_results`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_lesson_quiz` (`user_id`,`course_id`,`module_index`,`lesson_index`),
  ADD KEY `course_id` (`course_id`),
  ADD KEY `idx_lesson_result` (`user_id`,`course_id`,`module_index`,`lesson_index`);

--
-- Indexes for table `module_assessment_results`
--
ALTER TABLE `module_assessment_results`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_module_assessment` (`user_id`,`course_id`,`module_index`),
  ADD KEY `course_id` (`course_id`),
  ADD KEY `idx_module_assessment` (`user_id`,`course_id`,`module_index`);

--
-- Indexes for table `quiz_answer_options`
--
ALTER TABLE `quiz_answer_options`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_question_options` (`question_id`);

--
-- Indexes for table `quiz_questions`
--
ALTER TABLE `quiz_questions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_lesson_quiz` (`course_id`,`module_index`,`lesson_index`);

--
-- Indexes for table `saq_reevaluation_requests`
--
ALTER TABLE `saq_reevaluation_requests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_reeval_response` (`response_id`),
  ADD KEY `idx_reeval_user` (`user_id`);

--
-- Indexes for table `search_logs`
--
ALTER TABLE `search_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- Indexes for table `short_answer_questions`
--
ALTER TABLE `short_answer_questions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_module_saq` (`course_id`,`module_index`);

--
-- Indexes for table `student_final_responses`
--
ALTER TABLE `student_final_responses`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_final_submission` (`user_id`,`final_assessment_id`),
  ADD KEY `course_id` (`course_id`),
  ADD KEY `final_assessment_id` (`final_assessment_id`),
  ADD KEY `graded_by_user_id` (`graded_by_user_id`),
  ADD KEY `idx_student_final` (`user_id`,`course_id`);

--
-- Indexes for table `student_quiz_responses`
--
ALTER TABLE `student_quiz_responses`
  ADD PRIMARY KEY (`id`),
  ADD KEY `course_id` (`course_id`),
  ADD KEY `question_id` (`question_id`),
  ADD KEY `selected_option_id` (`selected_option_id`),
  ADD KEY `idx_student_quiz` (`user_id`,`course_id`,`module_index`,`lesson_index`);

--
-- Indexes for table `student_saq_responses`
--
ALTER TABLE `student_saq_responses`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_saq_submission` (`user_id`,`saq_id`),
  ADD KEY `course_id` (`course_id`),
  ADD KEY `saq_id` (`saq_id`),
  ADD KEY `graded_by_user_id` (`graded_by_user_id`),
  ADD KEY `idx_student_saq` (`user_id`,`course_id`,`module_index`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `idx_email` (`email`);

--
-- Indexes for table `user_preferences`
--
ALTER TABLE `user_preferences`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `certificates`
--
ALTER TABLE `certificates`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `courses`
--
ALTER TABLE `courses`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `course_completion_grades`
--
ALTER TABLE `course_completion_grades`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `course_feedback`
--
ALTER TABLE `course_feedback`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `enrollments`
--
ALTER TABLE `enrollments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `final_assessments`
--
ALTER TABLE `final_assessments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `lesson_quiz_results`
--
ALTER TABLE `lesson_quiz_results`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `module_assessment_results`
--
ALTER TABLE `module_assessment_results`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `quiz_answer_options`
--
ALTER TABLE `quiz_answer_options`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=533;

--
-- AUTO_INCREMENT for table `quiz_questions`
--
ALTER TABLE `quiz_questions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=135;

--
-- AUTO_INCREMENT for table `saq_reevaluation_requests`
--
ALTER TABLE `saq_reevaluation_requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `search_logs`
--
ALTER TABLE `search_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `short_answer_questions`
--
ALTER TABLE `short_answer_questions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT for table `student_final_responses`
--
ALTER TABLE `student_final_responses`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `student_quiz_responses`
--
ALTER TABLE `student_quiz_responses`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=191;

--
-- AUTO_INCREMENT for table `student_saq_responses`
--
ALTER TABLE `student_saq_responses`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `user_preferences`
--
ALTER TABLE `user_preferences`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `certificates`
--
ALTER TABLE `certificates`
  ADD CONSTRAINT `certificates_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `certificates_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `course_completion_grades`
--
ALTER TABLE `course_completion_grades`
  ADD CONSTRAINT `course_completion_grades_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `course_completion_grades_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `course_feedback`
--
ALTER TABLE `course_feedback`
  ADD CONSTRAINT `course_feedback_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `course_feedback_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `final_assessments`
--
ALTER TABLE `final_assessments`
  ADD CONSTRAINT `final_assessments_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `lesson_quiz_results`
--
ALTER TABLE `lesson_quiz_results`
  ADD CONSTRAINT `lesson_quiz_results_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `lesson_quiz_results_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `module_assessment_results`
--
ALTER TABLE `module_assessment_results`
  ADD CONSTRAINT `module_assessment_results_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `module_assessment_results_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `quiz_answer_options`
--
ALTER TABLE `quiz_answer_options`
  ADD CONSTRAINT `quiz_answer_options_ibfk_1` FOREIGN KEY (`question_id`) REFERENCES `quiz_questions` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `quiz_questions`
--
ALTER TABLE `quiz_questions`
  ADD CONSTRAINT `quiz_questions_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `saq_reevaluation_requests`
--
ALTER TABLE `saq_reevaluation_requests`
  ADD CONSTRAINT `saq_reevaluation_requests_ibfk_1` FOREIGN KEY (`response_id`) REFERENCES `student_saq_responses` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `saq_reevaluation_requests_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `search_logs`
--
ALTER TABLE `search_logs`
  ADD CONSTRAINT `fk_search_logs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `short_answer_questions`
--
ALTER TABLE `short_answer_questions`
  ADD CONSTRAINT `short_answer_questions_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `student_final_responses`
--
ALTER TABLE `student_final_responses`
  ADD CONSTRAINT `student_final_responses_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `student_final_responses_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `student_final_responses_ibfk_3` FOREIGN KEY (`final_assessment_id`) REFERENCES `final_assessments` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `student_final_responses_ibfk_4` FOREIGN KEY (`graded_by_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `student_quiz_responses`
--
ALTER TABLE `student_quiz_responses`
  ADD CONSTRAINT `student_quiz_responses_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `student_quiz_responses_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `student_quiz_responses_ibfk_3` FOREIGN KEY (`question_id`) REFERENCES `quiz_questions` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `student_quiz_responses_ibfk_4` FOREIGN KEY (`selected_option_id`) REFERENCES `quiz_answer_options` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `student_saq_responses`
--
ALTER TABLE `student_saq_responses`
  ADD CONSTRAINT `student_saq_responses_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `student_saq_responses_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `student_saq_responses_ibfk_3` FOREIGN KEY (`saq_id`) REFERENCES `short_answer_questions` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `student_saq_responses_ibfk_4` FOREIGN KEY (`graded_by_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
