import mysql.connector as mycon

connection = mycon.connect(host="localhost",user="root",password="admin",database="atm")
cursor = connection.cursor()

acc_no = "12345789"

cus_acc = 'cus' + acc_no

amount = '10000'
stat = 'CREDIT'

insert_value = f'''insert into {cus_acc}(amount, stat)
values('{amount}', '{stat}');'''
cursor.execute(insert_value)
connection.commit()

cursor.close()
connection.close()

print("Hello World")