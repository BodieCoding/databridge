-- Create the database
IF DB_ID('pocdb') IS NOT NULL
    DROP DATABASE pocdb;

CREATE DATABASE pocdb;
GO

USE pocdb;
GO

-- Enable Query Store for the database
ALTER DATABASE pocdb
SET QUERY_STORE = ON;

-- Configure Query Store settings (optional, adjust as needed)
ALTER DATABASE pocdb
SET QUERY_STORE (OPERATION_MODE = READ_WRITE, 
                 CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30),
                 DATA_FLUSH_INTERVAL_SECONDS = 900,
                 MAX_STORAGE_SIZE_MB = 100);

-- DDL for lender_customer table
IF OBJECT_ID('lender_customer') IS NOT NULL
    DROP TABLE lender_customer;

CREATE TABLE lender_customer (
    customer_id INT PRIMARY KEY IDENTITY(1,1),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE,
    email VARCHAR(255),
    phone_number VARCHAR(20)
);

-- DDL for loan_data table
IF OBJECT_ID('loan_data') IS NOT NULL
    DROP TABLE loan_data;

CREATE TABLE loan_data (
    loan_id INT PRIMARY KEY IDENTITY(1,1),
    loan_amount DECIMAL(18, 2),
    interest_rate DECIMAL(5, 2),
    loan_term INT,
    loan_type VARCHAR(50),
    origination_date DATE,
    maturity_date DATE
);

-- DDL for loan_borrower_data table
IF OBJECT_ID('loan_borrower_data') IS NOT NULL
    DROP TABLE loan_borrower_data;

CREATE TABLE loan_borrower_data (
    loan_borrower_id INT PRIMARY KEY IDENTITY(1,1),
    loanid INT, -- No FK constraint
    customer_id INT, -- No FK constraint
    borrower_first_name VARCHAR(100),
    borrower_last_name VARCHAR(100),
    borrower_date_of_birth DATE
);

-- DDL for loan_borrower_creditscore_data table
IF OBJECT_ID('loan_borrower_creditscore_data') IS NOT NULL
    DROP TABLE loan_borrower_creditscore_data;

CREATE TABLE loan_borrower_creditscore_data (
    credit_score_id INT PRIMARY KEY IDENTITY(1,1),
    loanborrowerid INT, -- No FK constraint
    credit_score INT,
    credit_score_date DATE
);

-- DDL for loan_comments
IF OBJECT_ID('loan_comments') IS NOT NULL
    DROP TABLE loan_comments;

CREATE TABLE loan_comments (
    comment_id INT PRIMARY KEY IDENTITY(1,1),
    loan_id INT,
    comment_text VARCHAR(MAX),
    comment_date DATETIME
);


-- Add indexes to the tables
-- Index for lender_customer table
CREATE INDEX idx_lender_customer_email ON lender_customer (email);
CREATE INDEX idx_lender_customer_phone_number ON lender_customer (phone_number);

-- Index for loan_data table
CREATE INDEX idx_loan_data_loan_amount ON loan_data (loan_amount);
CREATE INDEX idx_loan_data_origination_date ON loan_data (origination_date);
CREATE INDEX idx_loan_data_maturity_date ON loan_data (maturity_date);

-- Index for loan_borrower_data table
CREATE INDEX idx_loan_borrower_data_loanid ON loan_borrower_data (loanid);
CREATE INDEX idx_loan_borrower_data_customer_id ON loan_borrower_data (customer_id);

-- Index for loan_borrower_creditscore_data table
CREATE INDEX idx_loan_borrower_creditscore_data_loanborrowerid ON loan_borrower_creditscore_data (loanborrowerid);
CREATE INDEX idx_loan_borrower_creditscore_data_credit_score ON loan_borrower_creditscore_data (credit_score);

-- Index for loan_comments table
CREATE INDEX idx_loan_comments_loan_id ON loan_comments (loan_id);
CREATE INDEX idx_loan_comments_comment_date ON loan_comments (comment_date);

-- Seed data for lender_customer
INSERT INTO lender_customer (first_name, last_name, date_of_birth, email, phone_number) VALUES
('John', 'Doe', '1985-03-15', 'john.doe@example.com', '123-456-7890'),
('Jane', 'Smith', '1990-07-22', 'jane.smith@example.com', '987-654-3210'),
('Peter', 'Jones', '1988-11-01', 'peter.jones@example.com', '555-123-4567');

-- Seed data for loan_data
DECLARE @counter INT = 1;
WHILE @counter <= 500
BEGIN
    INSERT INTO loan_data (loan_amount, interest_rate, loan_term, loan_type, origination_date, maturity_date)
    VALUES (
        ROUND(RAND() * 100000, 2),  -- Random loan amount between 0 and 100000
        ROUND(RAND() * 10 + 2, 2),    -- Random interest rate between 2 and 12
        FLOOR(RAND() * 360) + 12,    -- Random loan term between 12 and 372 months (31 years)
        CASE FLOOR(RAND() * 3) 
            WHEN 0 THEN 'Mortgage'
            WHEN 1 THEN 'Auto Loan'
            ELSE 'Personal Loan'
        END,
        DATEADD(day, -FLOOR(RAND() * 365 * 5), GETDATE()), -- Random origination date within the last 5 years
        DATEADD(month, FLOOR(RAND() * 360) + 12, GETDATE())       -- Random maturity date, at least 1 year from now
    );
    SET @counter = @counter + 1;
END;


-- Seed data for loan_borrower_data
INSERT INTO loan_borrower_data (loanid, customer_id, borrower_first_name, borrower_last_name, borrower_date_of_birth)
SELECT
    ld.loan_id,
    lc.customer_id,
    lc.first_name,  -- Or a different first name if needed
    lc.last_name,   -- Or a different last name
    lc.date_of_birth -- Or a different dob
FROM loan_data ld
JOIN lender_customer lc ON
    lc.customer_id = (SELECT TOP 1 customer_id FROM lender_customer ORDER BY NEWID());  --important fix

-- Seed data for loan_borrower_creditscore_data
INSERT INTO loan_borrower_creditscore_data (loanborrowerid, credit_score, credit_score_date)
SELECT
    lbd.loan_borrower_id,
    FLOOR(RAND() * (850 - 300 + 1)) + 300, -- Random credit score between 300 and 850
    DATEADD(month, -FLOOR(RAND() * 24), GETDATE())  -- Random date within the last 2 years
FROM loan_borrower_data lbd;

-- Seed data for loan_comments
DECLARE @commentCounter INT = 1;
WHILE @commentCounter <= 500
BEGIN
    INSERT INTO loan_comments (loan_id, comment_text, comment_date)
    VALUES (
        (SELECT TOP 1 loan_id FROM loan_data ORDER BY NEWID()), -- Random loan_id
        'Comment ' + CAST(@commentCounter AS VARCHAR(10)) + ': ' +
        CASE FLOOR(RAND() * 4)
            WHEN 0 THEN 'Loan application in progress.'
            WHEN 1 THEN 'Funds disbursed to borrower.'
            WHEN 2 THEN 'Payment overdue.  Contact borrower.'
            ELSE 'Loan paid in full.'
        END,
        DATEADD(day, -FLOOR(RAND() * 60), GETDATE()) -- Random date within the last 60 days
    );
    SET @commentCounter = @commentCounter + 1;
END;
