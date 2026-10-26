-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 26, 2026 at 07:03 PM
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
-- Database: `aims_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `account_archive`
--

CREATE TABLE `account_archive` (
  `arc_user_id` int(11) NOT NULL,
  `original_user_id` int(11) DEFAULT NULL,
  `gmail` varchar(255) DEFAULT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `role` varchar(50) DEFAULT NULL,
  `archived_date` datetime DEFAULT NULL,
  `archive_reason` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `categories`
--

CREATE TABLE `categories` (
  `category_id` int(11) NOT NULL,
  `category_name` varchar(255) DEFAULT NULL,
  `category_desc` text DEFAULT NULL,
  `requires_return` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `categories`
--

INSERT INTO `categories` (`category_id`, `category_name`, `category_desc`, `requires_return`) VALUES
(1, 'Assets', 'Assets are durable, high-value items intended for long-term use within an organization. Because of their cost and lifespan, these items are strictly tracked, maintained, and often assigned to specific individuals. They are expected to be returned to inventory when a project ends or when an employee leaves.', 1),
(2, 'Consumable', 'Consumables are items that are depleted, worn out, or disposed of through normal day-to-day operations. They are generally lower in cost, purchased in bulk, and are not tracked individually after being dispensed. Once a consumable is issued, it is considered \"used up\" and does not need to be returned.', 0),
(3, 'Apparel', 'Refers to clothing, garments, attire, or items worn on the body', 1);

-- --------------------------------------------------------

--
-- Table structure for table `inventory_items`
--

CREATE TABLE `inventory_items` (
  `item_id` int(11) NOT NULL,
  `category_id` int(11) DEFAULT NULL,
  `item_name` varchar(255) DEFAULT NULL,
  `item_code` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `stock` int(11) DEFAULT NULL,
  `serial_no` varchar(100) DEFAULT NULL,
  `unit` varchar(50) DEFAULT NULL,
  `added_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `expiration_date` datetime DEFAULT NULL,
  `image_path` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `inventory_items`
--

INSERT INTO `inventory_items` (`item_id`, `category_id`, `item_name`, `item_code`, `description`, `stock`, `serial_no`, `unit`, `added_date`, `updated_date`, `expiration_date`, `image_path`) VALUES
(1, 3, 'Chef Uniform w/ Hat (Small)', 'ISHTM-A-1S', '(Unisex) A crisp, double-breasted white chef\'s jacket with a Mandarin collar and ¾-length sleeves with folded cuffs.', 100, '', 'set', '2026-10-26 21:34:48', '2026-10-26 22:04:11', NULL, NULL),
(2, 3, 'Chef Uniform w/ Hat (Medium)', 'ISHTM-A-2M', '(Unisex) A crisp, double-breasted white chef\'s jacket with a Mandarin collar and ¾-length sleeves with folded cuffs.', 100, '', 'set', '2026-10-26 21:38:20', '2026-10-26 22:04:21', NULL, NULL),
(3, 3, 'Chef Uniform w/ Hat (Large)', 'ISHTM-A-3L', '(Unisex) A crisp, double-breasted white chef\'s jacket with a Mandarin collar and ¾-length sleeves with folded cuffs.', 100, '', 'set', '2026-10-26 21:39:52', '2026-10-26 22:04:28', NULL, NULL),
(4, 1, 'Lenovo Laptop', 'CCS-LAP1', 'Lenovo ThinkPad laptop, angled at 45 degrees to capture both its ultrathin profile and its bright active display', 1, '302123', 'unit', '2026-10-26 21:42:41', '2026-10-26 21:42:41', NULL, NULL),
(5, 1, 'ROG Zephyrus G16 Laptop', 'CCS-LAP2', 'The 2024 ASUS ROG Zephyrus G16 is a premium, sub-2kg aluminum powerhouse that combines up to an Intel Core Ultra 9 185H processor and an NVIDIA GeForce RTX 4090 GPU with 32GB of high-speed RAM, up to 4TB of storage, and a vibrant 16-inch 2.5K 240Hz Nebula display.', 1, '301241', 'pcs', '2026-10-26 21:51:02', '2026-10-26 21:51:02', NULL, NULL),
(6, 2, 'Exam Booklet', 'ALL-CON1', 'Examination Booklet for Prelim, Midterm, Final exams', 499, '', 'pcs', '2026-10-26 21:52:48', '2026-10-26 21:52:48', NULL, NULL),
(7, 2, 'RJ45 CAT 5e Wire', 'CCS-C1', '(1 Meter wire) For Cisco, Network Activities', 300, '', 'pcs', '2026-10-26 21:54:53', '2026-10-26 21:54:53', NULL, NULL),
(8, 1, 'HDMI Cable', 'ALL-A1', 'HDMI Cable for Smart TV, TV, Any devices compatible with HDMI', 15, '', 'pcs', '2026-10-26 22:00:18', '2026-10-26 22:04:49', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `item_requests`
--

CREATE TABLE `item_requests` (
  `request_id` int(11) NOT NULL,
  `item_id` int(11) DEFAULT NULL,
  `requester_id` int(11) DEFAULT NULL,
  `quantity` int(11) DEFAULT NULL,
  `request_date` datetime DEFAULT NULL,
  `due_date` datetime DEFAULT NULL,
  `request_status` varchar(50) DEFAULT NULL,
  `processed_by` int(11) DEFAULT NULL,
  `approved_by` int(11) DEFAULT NULL,
  `confirmed_by` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `notif_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `notif_message` text DEFAULT NULL,
  `notif_type` varchar(50) DEFAULT NULL,
  `notif_isread` tinyint(1) DEFAULT NULL,
  `notif_create` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `personal_info`
--

CREATE TABLE `personal_info` (
  `personal_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `student_id` varchar(50) DEFAULT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `middle_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `birthday` date DEFAULT NULL,
  `contact_number` varchar(50) DEFAULT NULL,
  `department` varchar(100) DEFAULT NULL,
  `course` varchar(100) DEFAULT NULL,
  `gender` varchar(20) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `personal_info`
--

INSERT INTO `personal_info` (`personal_id`, `user_id`, `student_id`, `first_name`, `middle_name`, `last_name`, `birthday`, `contact_number`, `department`, `course`, `gender`, `address`) VALUES
(1, 1, 'AD198900013', 'Taylor Alisan', 'Swift', 'Kelce', '1989-12-13', '09198900013', 'College of Teacher Education', 'BSEd - Bachelor in Secondary Education', 'Male', 'Nashville'),
(1, 2, 'SU202400769', 'John Carlo', 'Magtibay', 'Manalo', '2006-02-08', '09260682711', 'College of Computer Studies', 'BSCS - Bachelor of Science in Computer Science', 'Male', '2436 Main Street, Springfield, IL 62704');

-- --------------------------------------------------------

--
-- Table structure for table `system_logs`
--

CREATE TABLE `system_logs` (
  `log_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `action` varchar(50) NOT NULL,
  `table_affected` varchar(100) NOT NULL,
  `record_id` varchar(255) DEFAULT NULL,
  `timestamp` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `transaction_id` int(11) NOT NULL,
  `request_id` int(11) DEFAULT NULL,
  `transaction_type` varchar(100) DEFAULT NULL,
  `transaction_date` datetime DEFAULT NULL,
  `quantity` int(11) DEFAULT NULL,
  `conditon_status` varchar(100) DEFAULT NULL,
  `condition_notes` text DEFAULT NULL,
  `handled_by` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `transactions_archive`
--

CREATE TABLE `transactions_archive` (
  `arc_transaction_id` int(11) NOT NULL,
  `request_id` int(11) DEFAULT NULL,
  `transaction_type` varchar(100) DEFAULT NULL,
  `transaction_date` datetime DEFAULT NULL,
  `quantity` int(11) DEFAULT NULL,
  `conditon_status` varchar(100) DEFAULT NULL,
  `condition_notes` text DEFAULT NULL,
  `handled_by` int(11) DEFAULT NULL,
  `archived_date` datetime DEFAULT NULL,
  `archive_reason` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_account`
--

CREATE TABLE `user_account` (
  `user_id` int(11) NOT NULL,
  `gmail` varchar(255) DEFAULT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `role` varchar(50) DEFAULT NULL,
  `creationdate` datetime DEFAULT NULL,
  `status` varchar(65) NOT NULL DEFAULT 'Active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_account`
--

INSERT INTO `user_account` (`user_id`, `gmail`, `password_hash`, `role`, `creationdate`, `status`) VALUES
(1, 'admin@gmail.com', 'pbkdf2_sha256$600000$17b3da4a900c266c4ae098aa310ecc82$c478f7c76096bf6cbaa19fda3148b443dec353b3ea5444ceec9816f93d537a63', 'Admin', '2026-10-20 15:00:29', 'Active'),
(2, 'jcmanalo@gmail.com', 'pbkdf2_sha256$600000$9b40d5a7cf00bf6315b9981aa47f841f$e0cb9d531f120746a94dde5cbaeb536526152a452f9aaee3319a60c4101a4e6c', 'Student', '2026-10-25 22:19:15', 'Active');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `account_archive`
--
ALTER TABLE `account_archive`
  ADD PRIMARY KEY (`arc_user_id`),
  ADD KEY `original_user_id` (`original_user_id`);

--
-- Indexes for table `categories`
--
ALTER TABLE `categories`
  ADD PRIMARY KEY (`category_id`);

--
-- Indexes for table `inventory_items`
--
ALTER TABLE `inventory_items`
  ADD PRIMARY KEY (`item_id`),
  ADD KEY `category_id` (`category_id`);

--
-- Indexes for table `item_requests`
--
ALTER TABLE `item_requests`
  ADD PRIMARY KEY (`request_id`),
  ADD KEY `item_id` (`item_id`),
  ADD KEY `requester_id` (`requester_id`),
  ADD KEY `processed_by` (`processed_by`),
  ADD KEY `item_requests_ibfk_4` (`approved_by`),
  ADD KEY `item_requests_ibfk_5` (`confirmed_by`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`notif_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `personal_info`
--
ALTER TABLE `personal_info`
  ADD PRIMARY KEY (`personal_id`),
  ADD KEY `personal_info_ibfk_1` (`user_id`);

--
-- Indexes for table `system_logs`
--
ALTER TABLE `system_logs`
  ADD PRIMARY KEY (`log_id`);

--
-- Indexes for table `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`transaction_id`),
  ADD KEY `request_id` (`request_id`),
  ADD KEY `handled_by` (`handled_by`);

--
-- Indexes for table `transactions_archive`
--
ALTER TABLE `transactions_archive`
  ADD PRIMARY KEY (`arc_transaction_id`);

--
-- Indexes for table `user_account`
--
ALTER TABLE `user_account`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `gmail` (`gmail`),
  ADD UNIQUE KEY `gmail_2` (`gmail`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `account_archive`
--
ALTER TABLE `account_archive`
  MODIFY `arc_user_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `categories`
--
ALTER TABLE `categories`
  MODIFY `category_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `inventory_items`
--
ALTER TABLE `inventory_items`
  MODIFY `item_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `item_requests`
--
ALTER TABLE `item_requests`
  MODIFY `request_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `notif_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `personal_info`
--
ALTER TABLE `personal_info`
  MODIFY `personal_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `system_logs`
--
ALTER TABLE `system_logs`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `transactions`
--
ALTER TABLE `transactions`
  MODIFY `transaction_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `transactions_archive`
--
ALTER TABLE `transactions_archive`
  MODIFY `arc_transaction_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user_account`
--
ALTER TABLE `user_account`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `inventory_items`
--
ALTER TABLE `inventory_items`
  ADD CONSTRAINT `inventory_items_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`);

--
-- Constraints for table `item_requests`
--
ALTER TABLE `item_requests`
  ADD CONSTRAINT `item_requests_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `inventory_items` (`item_id`),
  ADD CONSTRAINT `item_requests_ibfk_2` FOREIGN KEY (`requester_id`) REFERENCES `user_account` (`user_id`),
  ADD CONSTRAINT `item_requests_ibfk_3` FOREIGN KEY (`processed_by`) REFERENCES `user_account` (`user_id`),
  ADD CONSTRAINT `item_requests_ibfk_4` FOREIGN KEY (`approved_by`) REFERENCES `user_account` (`user_id`),
  ADD CONSTRAINT `item_requests_ibfk_5` FOREIGN KEY (`confirmed_by`) REFERENCES `user_account` (`user_id`);

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_account` (`user_id`);

--
-- Constraints for table `personal_info`
--
ALTER TABLE `personal_info`
  ADD CONSTRAINT `personal_info_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_account` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `transactions`
--
ALTER TABLE `transactions`
  ADD CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`request_id`) REFERENCES `item_requests` (`request_id`),
  ADD CONSTRAINT `transactions_ibfk_2` FOREIGN KEY (`handled_by`) REFERENCES `user_account` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
