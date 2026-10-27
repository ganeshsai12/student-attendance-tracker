CREATE DATABASE IF NOT EXISTS student_attendance;
USE student_attendance;

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(30) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE,
    course VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('Present', 'Absent') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_student_date (student_id, attendance_date),
    CONSTRAINT fk_attendance_student
        FOREIGN KEY (student_id) REFERENCES students(id)
        ON DELETE CASCADE
);

INSERT INTO students (roll_no, full_name, email, course) VALUES
('STU001', 'Aarav Sharma', 'aarav@example.com', 'Computer Science'),
('STU002', 'Ananya Reddy', 'ananya@example.com', 'Computer Science'),
('STU003', 'Rahul Kumar', 'rahul@example.com', 'Information Technology'),
('STU004', 'Priya Singh', 'priya@example.com', 'Information Technology'),
('STU005', 'Vikram Patel', 'vikram@example.com', 'Computer Science'),
('STU006', 'Meera Nair', 'meera@example.com', 'Data Science'),
('STU007', 'Arjun Rao', 'arjun@example.com', 'Data Science'),
('STU008', 'Kavya Das', 'kavya@example.com', 'Computer Science')
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name);

INSERT INTO attendance (student_id, attendance_date, status)
SELECT id, '2026-09-01',
       CASE roll_no
           WHEN 'STU001' THEN 'Present'
           WHEN 'STU002' THEN 'Present'
           WHEN 'STU003' THEN 'Absent'
           WHEN 'STU004' THEN 'Present'
           WHEN 'STU005' THEN 'Present'
           WHEN 'STU006' THEN 'Absent'
           WHEN 'STU007' THEN 'Present'
           ELSE 'Present'
       END
FROM students
ON DUPLICATE KEY UPDATE status=VALUES(status);

INSERT INTO attendance (student_id, attendance_date, status)
SELECT id, '2026-09-02',
       CASE roll_no
           WHEN 'STU001' THEN 'Present'
           WHEN 'STU002' THEN 'Absent'
           WHEN 'STU003' THEN 'Present'
           WHEN 'STU004' THEN 'Present'
           WHEN 'STU005' THEN 'Absent'
           WHEN 'STU006' THEN 'Present'
           WHEN 'STU007' THEN 'Present'
           ELSE 'Present'
       END
FROM students
ON DUPLICATE KEY UPDATE status=VALUES(status);

INSERT INTO attendance (student_id, attendance_date, status)
SELECT id, '2026-09-03',
       CASE roll_no
           WHEN 'STU001' THEN 'Present'
           WHEN 'STU002' THEN 'Present'
           WHEN 'STU003' THEN 'Present'
           WHEN 'STU004' THEN 'Absent'
           WHEN 'STU005' THEN 'Present'
           WHEN 'STU006' THEN 'Present'
           WHEN 'STU007' THEN 'Absent'
           ELSE 'Present'
       END
FROM students
ON DUPLICATE KEY UPDATE status=VALUES(status);
