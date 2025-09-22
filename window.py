import tkinter as tk
from tkinter import font, messagebox
import random
import mysql.connector as mycon
from sqlalchemy import create_engine
import pandas as pd
import hashlib

# Function to hash the password string
def hash_string(input_string):
    hasher = hashlib.sha256()
    hasher.update(input_string.encode('utf-8'))
    hashed_string = hasher.hexdigest()[:128]    
    return hashed_string

# MySQL Connections
connection = mycon.connect(host="localhost",user="root",password="admin", database="atm")
cursor = connection.cursor()
engine = create_engine('mysql+mysqlconnector://root:admin@localhost/atm')

# Miscellaneous variables
NEWPIN = 0
OTP = ''
cust_list=[]
acc_no = 0
amount = 0

# Using the registered customers list 
select_customer = f'''SELECT * FROM customers;;'''
dfCus = pd.read_sql(select_customer, engine)
cust_list = dfCus['acc_no'].to_list()

# Define the color theme variables for dark mode
bg_color = "#2c2c2c"      # Background color
fg_color = "#ffffff"      # Foreground color (text)
entry_bg_color = "white" # Entry background color
entry_fg_color = "black" # Entry foreground color (text)
display_bg_color = "#3c3c3c" # Display text background color
display_fg_color = "#ffffff" # Display text foreground color
button_bg_color = "#4c4c4c" # Button background color
button_fg_color = "#ffffff" # Button foreground color (text)

# Function to display message in the display window
def display_message(message):
    display_text.config(state=tk.NORMAL)  # Allow editing of the Text widget
    display_text.delete(1.0, tk.END)  # Clear the previous content
    display_text.insert(tk.END, message)  # Insert new message
    display_text.config(state=tk.DISABLED)  # Disable editing

# Function to enable or disable the main action buttons based on account number validity
def update_button_states():
    global cust_list
    global acc_no

    acc_no = acc_no_var.get()
    if acc_no in cust_list:  # Valid account number
        withdraw_button.config(state=tk.NORMAL)
        set_up_button.config(state=tk.NORMAL)
        cancel_button.config(state=tk.NORMAL)
    else:
        withdraw_button.config(state=tk.DISABLED)
        set_up_button.config(state=tk.DISABLED)
        cancel_button.config(state=tk.DISABLED)

# Function to handle Account Number validation and display
def validate_acc_no():
    global cust_list
    global acc_no

    acc_no = acc_no_var.get()
    if acc_no in cust_list:  # Assuming Acc No is numeric and at least 8 digits
        select_customer = f'''SELECT * FROM customers where acc_no = '{acc_no}';'''
        dfDet = pd.read_sql(select_customer, engine)
        cust_details = dfDet.iloc[0].tolist()
        display_message(f"Bank Name: {cust_details[2]}\nAccount Number: {cust_details[0]}\nAccount Holder Name: {cust_details[1]}")
        acc_no_entry.config(state=tk.DISABLED)
        update_button_states()  # Update button states based on validity
    else:
        display_message("Invalid Account Number.")

# Function to handle Amount validation and display
def validate_amount():
    global amount

    amount = amount_var.get()
    if amount.isdigit():  # Assuming Amount is numeric
        display_message(f"Amount entered: {amount}\nEnter PIN")
        amount_entry.config(state=tk.DISABLED)
    else:
        display_message("Invalid Amount.")

# Function to handle PIN validation and display
def validate_pin():
    global NEWPIN
    global acc_no
    global amount

    pin = pin_var.get()
    PIN = hash_string(pin)
    select_customer = f'''SELECT * FROM customers where acc_no = '{acc_no}';'''
    dfDet = pd.read_sql(select_customer, engine)
    cust_details = dfDet.iloc[0].tolist()
    if NEWPIN == 0:
        if PIN == cust_details[3]:
            cus_acc = 'cus' + str(acc_no)
            stat = "DEBIT"
            insert_amount = f'''insert into {cus_acc}(amount, stat) values('{amount}', '{stat}');'''
            cursor.execute(insert_amount)
            connection.commit()

            print(f'''Amount {amount} debited from account number {acc_no}''')
            display_message("Money Debited")
            pin_entry.config(state=tk.DISABLED)
        else:
            display_message("Invalid PIN.")
    else:
        update_pin = f'''update customers set pin = '{PIN}' where acc_no = '{acc_no}';'''
        cursor.execute(update_pin)
        connection.commit()
        messagebox.showinfo("Success", "New PIN Successfully Set Up")
        
        
        display_message("\tDatabase Management Systems\nPROJECT\n\nWelcome to ATM")
        acc_no_var.set('')
        amount_var.set('')
        pin_var.set('')
        otp_var.set('')
        enable_all()

# Function to handle OTP validation and display
def validate_otp():
    global NEWPIN
    global OTP

    otp = str(otp_var.get())
    if otp == OTP:  
        NEWPIN = 1
        otp_entry.config(state=tk.DISABLED)
        display_message("Enter PIN")
        pin_entry.config(state=tk.NORMAL)
    else:
        display_message("Invalid OTP.")

# Function to enable all entry fields
def enable_all():
    acc_no_entry.config(state=tk.NORMAL)
    amount_entry.config(state=tk.NORMAL)
    pin_entry.config(state=tk.NORMAL)
    otp_entry.config(state=tk.NORMAL)
    update_button_states()  # Update button states when enabling fields

# Function to handle Withdraw button action
def withdraw():
    acc_no_entry.config(state=tk.DISABLED)
    amount_entry.config(state=tk.NORMAL)
    pin_entry.config(state=tk.NORMAL)
    otp_entry.config(state=tk.DISABLED)

    display_message("Enter amount")

# Function to handle SetUp button action
def set_up():
    global OTP
    OTP = ''

    # Customer Details
    select_customer = f'''SELECT * FROM customers where acc_no = '{acc_no}';'''
    dfDet = pd.read_sql(select_customer, engine)
    cust_details = dfDet.iloc[0].tolist()

    # Generate OTP
    random_number = random.randint(0, 9)
    for i in range(0,6):
        OTP += str(random.randint(0, 9))
    otp_entry.config(state=tk.NORMAL)
    acc_no_entry.config(state=tk.DISABLED)
    amount_entry.config(state=tk.DISABLED)
    pin_entry.config(state=tk.DISABLED)
    
    print("Your OTP is ", OTP)
    display_message("Enter OTP to set up ATM")

# Function to handle Cancel button action
def cancel_transaction():
    response = messagebox.askyesno("Cancel Transaction", "Do you want to cancel the transaction?")
    if response:
        display_message("\tDatabase Management Systems\nPROJECT\n\nWelcome to ATM")
        acc_no_var.set('')
        amount_var.set('')
        pin_var.set('')
        otp_var.set('')
        enable_all()

# Create the main window
root = tk.Tk()
root.title("Bank Transaction")
root.configure(bg=bg_color)  # Set the background color of the main window

# Create a frame to hold the widgets
frame = tk.Frame(root, bg=bg_color)
frame.pack(pady=20, padx=20)

# StringVars to hold the input values
acc_no_var = tk.StringVar()
amount_var = tk.StringVar()
pin_var = tk.StringVar()
otp_var = tk.StringVar()

# Create a bold font for button labels
bold_font = font.Font(weight='bold')

# Acc No Entry
tk.Label(frame, text="Acc No:", bg=bg_color, fg=fg_color).grid(row=0, column=0, pady=5, sticky='w')
acc_no_entry = tk.Entry(frame, textvariable=acc_no_var, bg=entry_bg_color, fg=entry_fg_color)
acc_no_entry.grid(row=0, column=1, pady=5, sticky='w')

# Acc No Submit Button
acc_no_submit = tk.Button(frame, text="Submit", bg=button_bg_color, fg=button_fg_color, command=validate_acc_no)
acc_no_submit.grid(row=0, column=2, pady=5, padx=10)

# Display Window (Text widget)
display_text = tk.Text(frame, height=10, width=40, bg=display_bg_color, fg=display_fg_color)
display_text.grid(row=1, column=0, rowspan=3, columnspan=3, pady=10)
display_text.config(state=tk.DISABLED)  

# Amount and PIN Entry
tk.Label(frame, text="Amount:", bg=bg_color, fg=fg_color).grid(row=5, column=0, pady=5, sticky='w')
amount_entry = tk.Entry(frame, textvariable=amount_var, bg=entry_bg_color, fg=entry_fg_color)
amount_entry.grid(row=5, column=1, pady=5, sticky='w')

# Amount Submit Button
amount_submit = tk.Button(frame, text="Submit", bg=button_bg_color, fg=button_fg_color, command=validate_amount)
amount_submit.grid(row=5, column=2, pady=5, padx=10)

tk.Label(frame, text="PIN:", bg=bg_color, fg=fg_color).grid(row=6, column=0, pady=5, sticky='w')
pin_entry = tk.Entry(frame, textvariable=pin_var, show='*', bg=entry_bg_color, fg=entry_fg_color)
pin_entry.grid(row=6, column=1, pady=5, sticky='w')

# PIN Submit Button
pin_submit = tk.Button(frame, text="Submit", bg=button_bg_color, fg=button_fg_color, command=validate_pin)
pin_submit.grid(row=6, column=2, pady=5, padx=10)

# OTP Entry
tk.Label(frame, text="OTP:", bg=bg_color, fg=fg_color).grid(row=7, column=0, pady=5, sticky='w')
otp_entry = tk.Entry(frame, textvariable=otp_var, bg=entry_bg_color, fg=entry_fg_color)
otp_entry.grid(row=7, column=1, pady=5, sticky='w')

# OTP Submit Button
otp_submit = tk.Button(frame, text="Submit", bg=button_bg_color, fg=button_fg_color, command=validate_otp)
otp_submit.grid(row=7, column=2, pady=5, padx=10)

# Create Buttons 
button_width = 12 

withdraw_button = tk.Button(frame, text="Withdraw", bg="green", fg="black", width=button_width, font=bold_font, command=withdraw)
withdraw_button.grid(row=1, column=3, pady=5, padx=10)

set_up_button = tk.Button(frame, text="Set Up", bg="yellow", fg="black", width=button_width, font=bold_font, command=set_up)
set_up_button.grid(row=2, column=3, pady=5, padx=10)

cancel_button = tk.Button(frame, text="Cancel", bg="red", fg="black", width=button_width, font=bold_font, command=cancel_transaction)
cancel_button.grid(row=3, column=3, pady=5, padx=10)

# Display an initial message
display_message("\tDatabase Management Systems\nPROJECT\n\nWelcome to ATM")

# Disable action buttons initially
withdraw_button.config(state=tk.DISABLED)
set_up_button.config(state=tk.DISABLED)
cancel_button.config(state=tk.DISABLED)

# Start the Tkinter main loop
root.mainloop()

# Close MySQL Connections
connection.close()
cursor.close()

print("Hello World")