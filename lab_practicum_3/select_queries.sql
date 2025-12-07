

SELECT * FROM Student WHERE Year = 4;

SELECT LabNum FROM Student, Plan, Work WHERE
Plan.WorkNum = Work.Number AND
Plan.StudentId = Student.Id AND
Student.Name = 'Иванов И. И.' AND
Work.Name = 'Изучение плазмы в открытом поле';

SELECT * FROM Student WHERE Year = 1;

SELECT Student.Name FROM Student, Plan WHERE WorkNum = 1 AND LabNum = 1 AND Plan.StudentId = Student.Id;

SELECT Student.Name FROM Student, Plan, Work WHERE LabNum = 1 AND
Plan.WorkNum = Work.Number AND
Plan.StudentId = Student.Id AND
Work.Name = 'Изучение плазмы в магнитном поле';