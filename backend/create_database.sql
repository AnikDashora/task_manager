-- 1️⃣ Create the database
CREATE DATABASE task_flow;
USE task_flow;

-- 1️⃣ Users table
CREATE TABLE users (
    user_id VARCHAR(20) PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(512) NOT NULL,
    theme ENUM('Light', 'Dark') DEFAULT 'Light',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2️⃣ Daily plan table
CREATE TABLE daily_plan (
    plan_id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    plan_date DATE NOT NULL,
    total_task INT DEFAULT 0,
    completed_task INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, plan_date)
);

-- 3️⃣ Tasks table (no user_id, only plan_id)
CREATE TABLE tasks (
    task_id VARCHAR(20) PRIMARY KEY,
    plan_id VARCHAR(20) NOT NULL,     -- belongs to a daily plan
    title VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'Incomplete',   -- could be ENUM too
    incomplete_reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (plan_id) REFERENCES daily_plan(plan_id) ON DELETE CASCADE,
    CHECK (
        (status = 'Completed' AND incomplete_reason IS NULL) OR
        (status = 'Incomplete' AND incomplete_reason IS NOT NULL)
    )
);