download https://dev.mysql.com/downloads/windows/installer/8.0.html

install mysql workbench and mysql server
start workbench and setup a new connection, the username, database and password you have to put in app.py in:

```
mydb = mysql.connector.connect(
    user='user',
    password='password',
    database='database_name'
)
```

if you didn't change the hostname from 127.0.0.1 and the port from 3306 you can leave them out, otherwise:

```
mydb = mysql.connector.connect(
    user='user',
    password='password',
    port=port,
    database='database_name',
    hostname='hostname',
)
```
to create a database: 

```CREATE DATABASE database_name;```

to create a table in the database: 

```
CREATE TABLE your_table_name (
    row0 INT AUTO_INCREMENT PRIMARY KEY,
    row1 INT,
    row2 VARCHAR(255),
    row3 INT,
    row4 VARCHAR(255)
);
```

to insert values into the table: 
```
insert into your_table_name(`row1`, `row2`, `row3`, `row4`)
values
(1, 'a', 2, 'b''),
(3, 'c', 4, 'd'');
```