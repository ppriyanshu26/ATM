from sqlalchemy import create_engine
import pandas as pd, webbrowser, os
import mysql.connector as mycon

connection = mycon.connect(host="localhost",user="root",password="admin",database="atm")
cursor = connection.cursor()

engine = create_engine('mysql+mysqlconnector://root:admin@localhost/atm')

acc_no = "123"
acc = 'cus' + acc_no

acc_pas = "cus"+acc_no
delete_empty = f'''delete from {acc_pas} where amount = '0';'''
cursor.execute(delete_empty)
connection.commit()

select_customer = f'SELECT * FROM {acc};'

df = pd.read_sql(select_customer, engine)

script_dir = os.path.dirname(os.path.abspath(__file__))

directory = os.path.join(os.path.dirname(script_dir), "Passbooks")

file_name = "Passbook" + acc_no + ".html"
file_path = os.path.join(directory, file_name)

df.to_html(file_path)

webbrowser.open(f'file://{file_path}')

cursor.close()
connection.close()

print("Hello World")