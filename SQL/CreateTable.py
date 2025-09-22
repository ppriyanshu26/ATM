import mysql.connector as mycon

connection = mycon.connect(host="localhost",user="root",password="admin")
cursor = connection.cursor()

create_db = '''create database if not exists atm;'''
cursor.execute(create_db)
connection.commit()

use_db = '''use atm;'''
cursor.execute(use_db)
connection.commit()

create_table = '''create table if not exists customers (
acc_no varchar(20) primary key,
cname varchar(255) not null,
bank_name varchar(255),
pin varchar(255) not null
);'''
cursor.execute(create_table)
connection.commit()

cursor.close()
connection.close()

print("Hello World")