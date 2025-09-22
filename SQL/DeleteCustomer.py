import mysql.connector as mycon

connection = mycon.connect(host="localhost",user="root",password="admin", database="atm")
cursor = connection.cursor()

acc = "123"

delete_customer = f'''delete from customers where acc_no = '{acc}';'''
cursor.execute(delete_customer)
connection.commit()

cus_acc = 'cus' + acc

delete_pb = f'''drop table {cus_acc};'''
cursor.execute(delete_pb)
connection.commit()

cursor.close()
connection.close()

print("Hello World")