import hashlib, mysql.connector as mycon

def hash_string(input_string):
    hasher = hashlib.sha256()
    hasher.update(input_string.encode('utf-8'))
    hashed_string = hasher.hexdigest()[:128]    
    return hashed_string

connection = mycon.connect(host="localhost",user="root",password="admin",database="atm")
cursor = connection.cursor()

acc_no = "12345"
cname = "XYZ"
bname = "State Bank Of India"
pin = hash_string("111")

insert_value = f'''insert into customers 
values('{acc_no}', '{cname}', '{bname}', '{pin}');'''
cursor.execute(insert_value)
connection.commit()

cus_acc = 'cus' + acc_no

create_pb = f'''create table {cus_acc} (
amount varchar(255),
stat varchar(255),
time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);'''
cursor.execute(create_pb)
connection.commit()

amount = '100000'
stat = 'CREDIT'

insert_value = f'''insert into {cus_acc}(amount, stat)
values('{amount}', '{stat}');'''
cursor.execute(insert_value)
connection.commit()

cursor.close()
connection.close()

print("Hello World")