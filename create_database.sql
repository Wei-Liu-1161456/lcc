-- Drop the database if it exists
DROP DATABASE IF EXISTS `LCC`;


-- Create the database
CREATE DATABASE LCC;

-- Use the datebase
USE LCC;

-- Drop table if it exists before creating a new one
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`(
    `user_id` INT NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(20) NOT NULL,
    `password_hash` CHAR(60) BINARY NOT NULL COMMENT 'Bcrypt Password Hash and Salt (60 bytes)', 
    `email` VARCHAR(320) NOT NULL,
    `first_name` VARCHAR(50) NOT NULL,
    `last_name` VARCHAR(50) NOT NULL,
    `location` VARCHAR(50) NOT NULL,
    `profile_image` VARCHAR(255),
    `role` ENUM('visitor', 'helper', 'admin') NOT NULL,
	`status` ENUM('active', 'inactive') NOT NULL,
    PRIMARY KEY (`user_id`),
    UNIQUE KEY `username` (`username`)
);

-- Drop table if it exists before creating a new one
DROP TABLE IF EXISTS `issues`;
CREATE TABLE `issues` (
    `issue_id` INT NOT NULL AUTO_INCREMENT,
    `user_id` INT NOT NULL,
    `summary` VARCHAR(255) NOT NULL,
    `description` TEXT NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status` ENUM('new', 'open', 'stalled', 'resolved') NOT NULL DEFAULT 'new',
    PRIMARY KEY (`issue_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
);

-- Drop table if it exits before creating a new one
DROP TABLE IF EXISTS `comments`;
CREATE TABLE `comments` (
  `comment_id` INT NOT NULL AUTO_INCREMENT,
  `issue_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `content` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`comment_id`),
  FOREIGN KEY (`issue_id`) REFERENCES `issues`(`issue_id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE
);