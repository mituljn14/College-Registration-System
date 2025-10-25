Enter password: \*\*\*\*

Welcome to the MySQL monitor.  Commands end with ; or \\g.

Your MySQL connection id is 115

Server version: 9.4.0 MySQL Community Server - GPL



Copyright (c) 2000, 2025, Oracle and/or its affiliates.



Oracle is a registered trademark of Oracle Corporation and/or its

affiliates. Other names may be trademarks of their respective

owners.



Type 'help;' or '\\h' for help. Type '\\c' to clear the current input statement.



mysql> use lab6;

Database changed

mysql> CREATE TABLE Employees (

    ->     emp\_id INT PRIMARY KEY,

    ->     emp\_name VARCHAR(100) NOT NULL,

    ->     salary DECIMAL(10,2) NOT NULL

    -> );

Query OK, 0 rows affected (0.467 sec)

v

mysql> CREATE TABLE EmployeeSalaryLog (

    ->     log\_id INT AUTO\_INCREMENT PRIMARY KEY,

    ->     emp\_id INT,

    ->     old\_salary DECIMAL(10,2),

    ->     new\_salary DECIMAL(10,2),

    ->     update\_time TIMESTAMP DEFAULT CURRENT\_TIMESTAMP

    -> );

Query OK, 0 rows affected (0.455 sec)



mysql> INSERT INTO Employees (emp\_id, emp\_name, salary) VALUES

    -> (101, 'Alice', 50000.00),

    -> (102, 'Bob', 60000.00),

    -> (103, 'Charlie', 55000.00);

Query OK, 3 rows affected (0.088 sec)

Records: 3  Duplicates: 0  Warnings: 0



mysql> create procedure  UpdateEmployeeSalary(

    ->     IN p\_employee\_id INT,

    ->     IN p\_new\_salary DECIMAL(10,2)

    -> );

ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '' at line 4

mysql> DELIMITER $$

mysql>

mysql> CREATE PROCEDURE UpdateEmployeeSalary(

    ->     IN p\_employee\_id INT,

    ->     IN p\_new\_salary DECIMAL(10,2)

    -> )

    -> BEGIN

    ->     DECLARE v\_old\_salary DECIMAL(10,2);

    ->

    ->     -- Step 1: Check if employee exists

    ->     SELECT salary INTO v\_old\_salary

    ->     FROM Employees

    ->     WHERE employee\_id = p\_employee\_id

    ->     LIMIT 1;

    ->

    ->     -- Step 2: If employee exists, update salary

    ->     IF v\_old\_salary IS NOT NULL THEN

    ->         UPDATE Employees

    ->         SET salary = p\_new\_salary

    ->         WHERE employee\_id = p\_employee\_id;

    ->

    ->         -- Step 3: Insert into log

    ->         INSERT INTO EmployeeSalaryLog (employee\_id, old\_salary, new\_salary)

                VALUES (p\_employee\_id, v\_old\_salary, p\_new\_salary);

    ->

    ->     END IF;

    ->

    -> END$$

Query OK, 0 rows affected (0.160 sec)



mysql>

mysql> DELIMITER ;

mysql> CALL UpdateEmployeeSalary(101, 75000.00);

ERROR 1054 (42S22): Unknown column 'employee\_id' in 'where clause'

mysql> CALL UpdateEmployeeSalary(101, 75000.00);

ERROR 1054 (42S22): Unknown column 'employee\_id' in 'where clause'

mysql> drop table employees;

Query OK, 0 rows affected (0.277 sec)



mysql> drop table employeesalarylog;

Query OK, 0 rows affected (0.453 sec)



mysql> CREATE TABLE Employees (

    ->     employee\_id INT PRIMARY KEY,

    ->     emp\_name VARCHAR(100) NOT NULL,

    ->     salary DECIMAL(10,2) NOT NULL );

Query OK, 0 rows affected (0.284 sec)



mysql> INSERT INTO Employees (employee\_id, emp\_name, salary) VALUES

    -> (101, 'Alice', 50000.00),

    -> (102, 'Bob', 60000.00),

    -> (103, 'Charlie', 55000.00);

Query OK, 3 rows affected (0.069 sec)

Records: 3  Duplicates: 0  Warnings: 0



mysql> CREATE TABLE EmployeeSalaryLog (

    ->     log\_id INT AUTO\_INCREMENT PRIMARY KEY,

    ->     employee\_id INT NOT NULL,

    ->     old\_salary DECIMAL(10,2),

    ->     new\_salary DECIMAL(10,2),

    ->     update\_time TIMESTAMP DEFAULT CURRENT\_TIMESTAMP,

    ->     FOREIGN KEY (employee\_id) REFERENCES Employees(employee\_id)

    -> );

Query OK, 0 rows affected (0.845 sec)



mysql> CALL UpdateEmployeeSalary(101, 75000.00);

Query OK, 1 row affected (0.131 sec)



mysql> select \* from employee;

+--------+--------+

| emp\_id | salary |

+--------+--------+

|    101 |  20000 |

|    102 |  30000 |

|    103 |  40000 |

|    104 |  50000 |

|    105 |  60000 |

+--------+--------+

5 rows in set (0.018 sec)



mysql> select \* from employeelogsalary;

ERROR 1146 (42S02): Table 'lab6.employeelogsalary' doesn't exist

mysql> select \* from employeesalarylog;

+--------+-------------+------------+------------+---------------------+

| log\_id | employee\_id | old\_salary | new\_salary | update\_time         |

+--------+-------------+------------+------------+---------------------+

|      1 |         101 |   50000.00 |   75000.00 | 2025-10-05 15:15:28 |

+--------+-------------+------------+------------+---------------------+

1 row in set (0.010 sec)



mysql> CREATE TABLE Employees (

    ->     emp\_id INT PRIMARY KEY AUTO\_INCREMENT,

    ->     emp\_name VARCHAR(100),

    ->     salary DECIMAL(10,2),

    ->     hire\_date DATE

    -> );

ERROR 1050 (42S01): Table 'employees' already exists

mysql> alter table emplyees add column hire\_date date;

ERROR 1146 (42S02): Table 'lab6.emplyees' doesn't exist

mysql> drop table employees;

ERROR 3730 (HY000): Cannot drop table 'employees' referenced by a foreign key constraint 'employeesalarylog\_ibfk\_1' on table 'employeesalarylog'.

mysql> select \* from employees;

+-------------+----------+----------+

| employee\_id | emp\_name | salary   |

+-------------+----------+----------+

|         101 | Alice    | 75000.00 |

|         102 | Bob      | 60000.00 |

|         103 | Charlie  | 55000.00 |

+-------------+----------+----------+

3 rows in set (0.014 sec)



mysql> drop table employee;

Query OK, 0 rows affected (0.181 sec)



mysql> alter table emplyees add column hire\_date date;

ERROR 1146 (42S02): Table 'lab6.emplyees' doesn't exist

mysql> alter table employees add column hire\_date date;

Query OK, 0 rows affected (0.292 sec)

Records: 0  Duplicates: 0  Warnings: 0



mysql> update employees set hire\_date = 2025-12-05 where employee\_id = 101;

ERROR 1292 (22007): Incorrect date value: '2008' for column 'hire\_date' at row 1

mysql> update employees set hire\_date = '2025-12-05' where employee\_id = 101;

Query OK, 1 row affected (0.043 sec)

Rows matched: 1  Changed: 1  Warnings: 0



mysql> update employees set hire\_date = '2025-11-05' where employee\_id = 102;

Query OK, 1 row affected (0.049 sec)

Rows matched: 1  Changed: 1  Warnings: 0



mysql> update employees set hire\_date = '2025-10-05' where employee\_id = 103;

Query OK, 1 row affected (0.075 sec)

Rows matched: 1  Changed: 1  Warnings: 0



mysql> select \* from employees;

+-------------+----------+----------+------------+

| employee\_id | emp\_name | salary   | hire\_date  |

+-------------+----------+----------+------------+

|         101 | Alice    | 75000.00 | 2025-12-05 |

|         102 | Bob      | 60000.00 | 2025-11-05 |

|         103 | Charlie  | 55000.00 | 2025-10-05 |

+-------------+----------+----------+------------+

3 rows in set (0.013 sec)



mysql> DELIMITER $$

mysql>

mysql> CREATE FUNCTION CalculateAnnualBonus(emp\_id INT)

    -> RETURNS DECIMAL(10,2)

    -> DETERMINISTIC

    -> BEGIN

    ->     DECLARE emp\_salary DECIMAL(10,2);

    ->     DECLARE years\_of\_service INT;

    ->     DECLARE bonus DECIMAL(10,2);

######  

    ->     -- Get employee's salary and years of service

    ->     SELECT salary, TIMESTAMPDIFF(YEAR, hire\_date, CURDATE())

    ->     INTO emp\_salary, years\_of\_service

    ->     FROM Employees

    -> WHERE employee\_id = emp\_id

    -> LIMIT 1;

    ->

    ->     -- If employee not found, return NULL

    ->     IF emp\_salary IS NULL THEN

    ->         RETURN NULL;

    ->     END IF;

    ->

    ->     -- Bonus calculation

    ->     IF years\_of\_service < 5 THEN

    ->         SET bonus = emp\_salary \* 0.10;

    ->     ELSEIF years\_of\_service >= 5 AND years\_of\_service < 10 THEN

    ->         SET bonus = emp\_salary \* 0.15;

    ->     ELSE

    ->         SET bonus = emp\_salary \* 0.20;

    ->     END IF;

    ->

    ->     RETURN bonus;

    -> END$$

Query OK, 0 rows affected (0.093 sec)



mysql>

mysql> DELIMITER ;

mysql> SELECT CalculateAnnualBonus(1) AS Bonus;

+-------+

| Bonus |

+-------+

|  NULL |

+-------+

1 row in set (0.033 sec)



mysql> update employees set hire\_date = '2020-11-05' where employee\_id = 103;

Query OK, 1 row affected (0.059 sec)

Rows matched: 1  Changed: 1  Warnings: 0



mysql> update employees set hire\_date = '2015-11-05' where employee\_id = 101;

Query OK, 1 row affected (0.046 sec)

Rows matched: 1  Changed: 1  Warnings: 0



mysql> update employees set hire\_date = '2010-11-05' where employee\_id = 102;

Query OK, 1 row affected (0.067 sec)

Rows matched: 1  Changed: 1  Warnings: 0



mysql> SELECT CalculateAnnualBonus(1) AS Bonus;

+-------+

| Bonus |

+-------+

|  NULL |

+-------+

1 row in set (0.015 sec)



mysql> SELECT CalculateAnnualBonus(101) AS Bonus;

+----------+

| Bonus    |

+----------+

| 11250.00 |

+----------+

1 row in set (0.016 sec)



mysql>

mysql> desc users;
+----------+--------------+------+-----+---------+----------------+
| Field    | Type         | Null | Key | Default | Extra          |
+----------+--------------+------+-----+---------+----------------+
| id       | int          | NO   | PRI | NULL    | auto_increment |
| username | varchar(50)  | NO   |     | NULL    |                |
| password | varchar(100) | NO   |     | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
3 rows in set (0.062 sec)

mysql>