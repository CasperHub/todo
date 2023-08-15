download https://dev.mysql.com/downloads/windows/installer/8.0.html

install mysql workbench and mysql server
start workbench and setup a new connection, the username, database and password you have to put in app.py in:

```
mydb = mysql.connector.connect(
    user='root',
    password='root',
    database='todo'
)
```

if you didn't change the hostname from 127.0.0.1 and the port from 3306 you can leave them out, otherwise:

```
mydb = mysql.connector.connect(
    user='root',
    password='root',
    port=port,
    database='todo',
    hostname='hostname',
)
```

```
insert into tasks(`name`, `desc`, `deadline`, `duration`)
values
('Write a blog post', 'Compose an informative blog post', '2023-07-10', 90),
('Attend a webinar', 'Participate in an educational webinar', '2023-07-11', 120);
```