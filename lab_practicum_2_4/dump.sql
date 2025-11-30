
CREATE TABLE finansy (
    idf SERIAL PRIMARY KEY,
    dept VARCHAR(12) NOT NULL,
    summ DECIMAL(8,2) NOT NULL
);

INSERT INTO finansy (dept, summ) VALUES 
('Dept 22', 125.50),
('Dept Цнит', 50.00);