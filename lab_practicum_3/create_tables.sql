CREATE TABLE Student (
    Id INTEGER PRIMARY KEY,
    Name VARCHAR(50) NOT NULL,
    Year INTEGER NOT NULL
);

CREATE TABLE Work (
    Number INTEGER PRIMARY KEY,
    Name VARCHAR(50) NOT NULL
);

CREATE TABLE Laboratory (
    Number INTEGER PRIMARY KEY,
    Name VARCHAR(50) NOT NULL,
    Capacity INTEGER NOT NULL,
    Disposition VARCHAR(50) NOT NULL
);

CREATE TABLE Plan (
    StudentId INTEGER NOT NULL,
    WorkNum INTEGER NOT NULL,
    LabNum INTEGER NOT NULL,
    PRIMARY KEY (StudentId, WorkNum, LabNum),
    FOREIGN KEY (StudentId) REFERENCES Student(Id),
    FOREIGN KEY (WorkNum) REFERENCES Work(Number),
    FOREIGN KEY (LabNum) REFERENCES Laboratory(Number)
);

CREATE TABLE Report (
    StudentId INTEGER NOT NULL,
    WorkNum INTEGER NOT NULL,
    File VARCHAR(50) NOT NULL,
    PRIMARY KEY (StudentId, WorkNum),
    FOREIGN KEY (StudentId) REFERENCES Student(Id),
    FOREIGN KEY (WorkNum) REFERENCES Work(Number)
);