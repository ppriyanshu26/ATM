"""
ATM GUI Application

This module provides a graphical user interface for an ATM (Automated Teller Machine) system
built with Tkinter. The application allows customers to perform basic banking operations
such as withdrawing money and setting up new PINs with OTP verification.

Features:
    - Account number validation against a MySQL database
    - Secure PIN handling with SHA-256 hashing
    - Money withdrawal with balance tracking
    - PIN setup/change functionality with OTP verification
    - Dark theme GUI with modern interface design
    - Real-time transaction logging to customer-specific tables

Dependencies:
    - tkinter: GUI framework
    - mysql.connector: MySQL database connectivity
    - sqlalchemy: SQL toolkit and ORM
    - pandas: Data manipulation and analysis
    - hashlib: Secure hash and message digest algorithms
    - random: Generate random numbers for OTP

Database Requirements:
    - MySQL server running on localhost
    - Database named 'atm'
    - Tables: 'customers' and individual customer transaction tables (cus{account_number})

Author: ATM Project Team
Date: 2025
"""

import tkinter as tk
from tkinter import font, messagebox
import random
import mysql.connector as mycon
from sqlalchemy import create_engine
import pandas as pd
import hashlib
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================

# Database Configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'admin'),
    'database': os.getenv('DB_NAME', 'atm')
}

# UI Color Theme (Dark Mode)
UI_COLORS = {
    'bg_color': "#2c2c2c",          # Background color
    'fg_color': "#ffffff",          # Foreground color (text)
    'entry_bg_color': "white",      # Entry background color
    'entry_fg_color': "black",      # Entry foreground color (text)
    'display_bg_color': "#3c3c3c",  # Display text background color
    'display_fg_color': "#ffffff",  # Display text foreground color
    'button_bg_color': "#4c4c4c",   # Button background color
    'button_fg_color': "#ffffff"    # Button foreground color (text)
}

# Application State Variables
NEWPIN = 0
OTP = ''
cust_list = []
acc_no = 0
amount = 0

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def hash_string(input_string):
    """
    Hash a password string using SHA-256 algorithm.
    
    Args:
        input_string (str): The input string to be hashed
        
    Returns:
        str: The first 128 characters of the hexadecimal hash digest
        
    Note:
        Uses SHA-256 hashing algorithm for secure password storage.
        Only returns first 128 characters to match database field size.
    """
    hasher = hashlib.sha256()
    hasher.update(input_string.encode('utf-8'))
    hashed_string = hasher.hexdigest()[:128]    
    return hashed_string

# =============================================================================
# DATABASE CONNECTION CLASS
# =============================================================================

class DatabaseManager:
    """
    Manages database connections and operations for the ATM system.
    
    This class encapsulates all database-related functionality including
    connection management, customer data retrieval, and transaction logging.
    """
    
    def __init__(self, config):
        """
        Initialize database connection with provided configuration.
        
        Args:
            config (dict): Database configuration containing host, user, password, database
        """
        self.config = config
        self.connection = None
        self.cursor = None
        self.engine = None
        self.connect()
    
    def connect(self):
        """
        Establish connections to MySQL database.
        
        Creates both mysql.connector connection for direct SQL operations
        and SQLAlchemy engine for pandas operations.
        """
        try:
            self.connection = mycon.connect(**self.config)
            self.cursor = self.connection.cursor()
            conn_str = f'mysql+mysqlconnector://{self.config["user"]}:{self.config["password"]}@{self.config["host"]}/{self.config["database"]}'
            self.engine = create_engine(conn_str)
        except Exception as e:
            print(f"Database connection error: {e}")
            raise
    
    def get_customer_list(self):
        """
        Retrieve list of all customer account numbers.
        
        Returns:
            list: List of customer account numbers
        """
        try:
            query = "SELECT * FROM customers;"
            df_customers = pd.read_sql(query, self.engine)
            return df_customers['acc_no'].to_list()
        except Exception as e:
            print(f"Error loading customer list: {e}")
            return []
    
    def get_customer_details(self, acc_no):
        """
        Retrieve customer details by account number.
        
        Args:
            acc_no (str): Customer account number
            
        Returns:
            list: Customer details as a list [acc_no, name, bank, pin, ...]
        """
        try:
            query = f"SELECT * FROM customers WHERE acc_no = '{acc_no}';"
            df_details = pd.read_sql(query, self.engine)
            return df_details.iloc[0].to_list()
        except Exception as e:
            print(f"Error getting customer details: {e}")
            return []
    
    def record_transaction(self, acc_no, amount, transaction_type):
        """
        Record a transaction in the customer's transaction table.
        
        Args:
            acc_no (str): Customer account number
            amount (str): Transaction amount
            transaction_type (str): Type of transaction (DEBIT/CREDIT)
        """
        try:
            table_name = f'cus{acc_no}'
            query = f"INSERT INTO {table_name}(amount, stat) VALUES('{amount}', '{transaction_type}');"
            self.cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            print(f"Error recording transaction: {e}")
    
    def update_customer_pin(self, acc_no, new_pin):
        """
        Update customer PIN in the database.
        
        Args:
            acc_no (str): Customer account number
            new_pin (str): New hashed PIN
        """
        try:
            query = f"UPDATE customers SET pin = '{new_pin}' WHERE acc_no = '{acc_no}';"
            self.cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            print(f"Error updating PIN: {e}")
    
    def close(self):
        """Close database connections."""
        if self.connection:
            self.connection.close()
        if self.cursor:
            self.cursor.close()

# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

# Initialize database manager and customer list
db_manager = DatabaseManager(DB_CONFIG)
cust_list = db_manager.get_customer_list()

# =============================================================================
# ATM GUI APPLICATION CLASS
# =============================================================================

class ATMApplication:
    """
    Main ATM GUI Application class.
    
    This class encapsulates the entire ATM user interface and handles
    all user interactions, form validation, and database operations.
    """
    
    def __init__(self):
        """Initialize the ATM application with GUI components and state variables."""
        self.setup_window()
        self.setup_variables()
        self.setup_widgets()
        self.display_welcome_message()
        
    def setup_window(self):
        """Create and configure the main application window."""
        self.root = tk.Tk()
        self.root.title("Bank Transaction System")
        self.root.configure(bg=UI_COLORS['bg_color'])
        
        # Create main frame
        self.frame = tk.Frame(self.root, bg=UI_COLORS['bg_color'])
        self.frame.pack(pady=20, padx=20)
        
    def setup_variables(self):
        """Initialize StringVar variables for form inputs."""
        self.acc_no_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.pin_var = tk.StringVar()
        self.otp_var = tk.StringVar()
        
    def setup_widgets(self):
        """Create and configure all GUI widgets."""
        # Create bold font for buttons
        self.bold_font = font.Font(weight='bold')
        
        # Account Number Entry
        tk.Label(self.frame, text="Acc No:", bg=UI_COLORS['bg_color'], fg=UI_COLORS['fg_color']).grid(row=0, column=0, pady=5, sticky='w')
        self.acc_no_entry = tk.Entry(self.frame, textvariable=self.acc_no_var, bg=UI_COLORS['entry_bg_color'], fg=UI_COLORS['entry_fg_color'])
        self.acc_no_entry.grid(row=0, column=1, pady=5, sticky='w')
        
        # Account Number Submit Button
        tk.Button(self.frame, text="Submit", bg=UI_COLORS['button_bg_color'], fg=UI_COLORS['button_fg_color'], command=self.validate_acc_no).grid(row=0, column=2, pady=5, padx=10)
        
        # Display Window (Text widget)
        self.display_text = tk.Text(self.frame, height=10, width=40, bg=UI_COLORS['display_bg_color'], fg=UI_COLORS['display_fg_color'])
        self.display_text.grid(row=1, column=0, rowspan=3, columnspan=3, pady=10)
        self.display_text.config(state=tk.DISABLED)
        
        # Amount Entry
        tk.Label(self.frame, text="Amount:", bg=UI_COLORS['bg_color'], fg=UI_COLORS['fg_color']).grid(row=5, column=0, pady=5, sticky='w')
        self.amount_entry = tk.Entry(self.frame, textvariable=self.amount_var, bg=UI_COLORS['entry_bg_color'], fg=UI_COLORS['entry_fg_color'])
        self.amount_entry.grid(row=5, column=1, pady=5, sticky='w')
        
        # Amount Submit Button
        tk.Button(self.frame, text="Submit", bg=UI_COLORS['button_bg_color'], fg=UI_COLORS['button_fg_color'], command=self.validate_amount).grid(row=5, column=2, pady=5, padx=10)
        
        # PIN Entry
        tk.Label(self.frame, text="PIN:", bg=UI_COLORS['bg_color'], fg=UI_COLORS['fg_color']).grid(row=6, column=0, pady=5, sticky='w')
        self.pin_entry = tk.Entry(self.frame, textvariable=self.pin_var, show='*', bg=UI_COLORS['entry_bg_color'], fg=UI_COLORS['entry_fg_color'])
        self.pin_entry.grid(row=6, column=1, pady=5, sticky='w')
        
        # PIN Submit Button
        tk.Button(self.frame, text="Submit", bg=UI_COLORS['button_bg_color'], fg=UI_COLORS['button_fg_color'], command=self.validate_pin).grid(row=6, column=2, pady=5, padx=10)
        
        # OTP Entry
        tk.Label(self.frame, text="OTP:", bg=UI_COLORS['bg_color'], fg=UI_COLORS['fg_color']).grid(row=7, column=0, pady=5, sticky='w')
        self.otp_entry = tk.Entry(self.frame, textvariable=self.otp_var, bg=UI_COLORS['entry_bg_color'], fg=UI_COLORS['entry_fg_color'])
        self.otp_entry.grid(row=7, column=1, pady=5, sticky='w')
        
        # OTP Submit Button
        tk.Button(self.frame, text="Submit", bg=UI_COLORS['button_bg_color'], fg=UI_COLORS['button_fg_color'], command=self.validate_otp).grid(row=7, column=2, pady=5, padx=10)
        
        # Action Buttons
        button_width = 12
        self.withdraw_button = tk.Button(self.frame, text="Withdraw", bg="green", fg="black", width=button_width, font=self.bold_font, command=self.withdraw)
        self.withdraw_button.grid(row=1, column=3, pady=5, padx=10)
        
        self.set_up_button = tk.Button(self.frame, text="Set Up PIN", bg="yellow", fg="black", width=button_width, font=self.bold_font, command=self.set_up)
        self.set_up_button.grid(row=2, column=3, pady=5, padx=10)
        
        self.cancel_button = tk.Button(self.frame, text="Cancel", bg="red", fg="black", width=button_width, font=self.bold_font, command=self.cancel_transaction)
        self.cancel_button.grid(row=3, column=3, pady=5, padx=10)
        
        # Initially disable action buttons
        self.update_button_states()
        
    def display_message(self, message):
        """Display a message in the GUI display window."""
        self.display_text.config(state=tk.NORMAL)
        self.display_text.delete(1.0, tk.END)
        self.display_text.insert(tk.END, message)
        self.display_text.config(state=tk.DISABLED)
        
    def display_welcome_message(self):
        """Display the initial welcome message."""
        self.display_message("\tDatabase Management Systems\nPROJECT\n\nWelcome to ATM")
        
    def update_button_states(self):
        """Enable or disable action buttons based on account number validity."""
        acc_no = self.acc_no_var.get()
        if acc_no in cust_list:
            self.withdraw_button.config(state=tk.NORMAL)
            self.set_up_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.NORMAL)
        else:
            self.withdraw_button.config(state=tk.DISABLED)
            self.set_up_button.config(state=tk.DISABLED)
            self.cancel_button.config(state=tk.DISABLED)
            
    def enable_all(self):
        """Enable all entry fields and update button states."""
        self.acc_no_entry.config(state=tk.NORMAL)
        self.amount_entry.config(state=tk.NORMAL)
        self.pin_entry.config(state=tk.NORMAL)
        self.otp_entry.config(state=tk.NORMAL)
        self.update_button_states()
        
    def validate_acc_no(self):
        """Validate account number and display customer details."""
        acc_no = self.acc_no_var.get()
        if acc_no in cust_list:
            try:
                cust_details = db_manager.get_customer_details(acc_no)
                self.display_message(f"Bank Name: {cust_details[2]}\nAccount Number: {cust_details[0]}\nAccount Holder Name: {cust_details[1]}")
                self.acc_no_entry.config(state=tk.DISABLED)
                self.update_button_states()
            except Exception as e:
                self.display_message(f"Error retrieving customer details: {e}")
        else:
            self.display_message("Invalid Account Number.")
            
    def validate_amount(self):
        """Validate entered amount for withdrawal."""
        amount = self.amount_var.get()
        if amount.isdigit() and int(amount) > 0:
            self.display_message(f"Amount entered: {amount}\nEnter PIN")
            self.amount_entry.config(state=tk.DISABLED)
        else:
            self.display_message("Invalid Amount. Please enter a positive number.")
            
    def validate_pin(self):
        """Validate PIN and process transaction or PIN setup."""
        global NEWPIN
        
        pin = self.pin_var.get()
        if not pin:
            self.display_message("Please enter a PIN.")
            return
            
        acc_no = self.acc_no_var.get()
        amount = self.amount_var.get()
        hashed_pin = hash_string(pin)
        
        try:
            cust_details = db_manager.get_customer_details(acc_no)
            
            if NEWPIN == 0:  # Regular withdrawal transaction
                if hashed_pin == cust_details[3]:
                    db_manager.record_transaction(acc_no, amount, "DEBIT")
                    print(f"Amount {amount} debited from account number {acc_no}")
                    self.display_message("Money Debited Successfully")
                    self.pin_entry.config(state=tk.DISABLED)
                else:
                    self.display_message("Invalid PIN.")
            else:  # PIN setup/change
                db_manager.update_customer_pin(acc_no, hashed_pin)
                messagebox.showinfo("Success", "New PIN Successfully Set Up")
                self.display_welcome_message()
                self.reset_form()
        except Exception as e:
            self.display_message(f"Error processing PIN: {e}")
            
    def validate_otp(self):
        """Validate OTP for PIN setup process."""
        global NEWPIN, OTP
        
        otp = str(self.otp_var.get())
        if otp == OTP:
            NEWPIN = 1
            self.otp_entry.config(state=tk.DISABLED)
            self.display_message("OTP Verified. Enter New PIN")
            self.pin_entry.config(state=tk.NORMAL)
        else:
            self.display_message("Invalid OTP. Please try again.")
            
    def withdraw(self):
        """Handle withdraw button action."""
        self.acc_no_entry.config(state=tk.DISABLED)
        self.amount_entry.config(state=tk.NORMAL)
        self.pin_entry.config(state=tk.NORMAL)
        self.otp_entry.config(state=tk.DISABLED)
        self.display_message("Enter withdrawal amount")
        
    def set_up(self):
        """Handle setup button action for PIN change."""
        global OTP
        OTP = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        self.otp_entry.config(state=tk.NORMAL)
        self.acc_no_entry.config(state=tk.DISABLED)
        self.amount_entry.config(state=tk.DISABLED)
        self.pin_entry.config(state=tk.DISABLED)
        
        print(f"Your OTP is: {OTP}")  # In production, send via SMS/email
        self.display_message("OTP sent. Enter OTP to set up new PIN")
        
    def cancel_transaction(self):
        """Handle cancel button action."""
        response = messagebox.askyesno("Cancel Transaction", "Do you want to cancel the transaction?")
        if response:
            self.display_welcome_message()
            self.reset_form()
            
    def reset_form(self):
        """Reset all form fields and enable all inputs."""
        global NEWPIN
        NEWPIN = 0  # Reset PIN setup flag
        self.acc_no_var.set('')
        self.amount_var.set('')
        self.pin_var.set('')
        self.otp_var.set('')
        self.enable_all()
        
    def run(self):
        """Start the application main loop."""
        self.root.mainloop()
        
    def cleanup(self):
        """Clean up resources before closing."""
        db_manager.close()

# =============================================================================
# MAIN FUNCTION AND ENTRY POINT
# =============================================================================

def main():
    """
    Main function to run the ATM application.
    
    Creates and runs the ATM GUI application, handling any initialization
    errors and ensuring proper cleanup on exit.
    """
    try:
        app = ATMApplication()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        messagebox.showerror("Error", f"Failed to start ATM application: {e}")
    finally:
        # Ensure database connections are closed
        try:
            db_manager.close()
        except:
            pass

if __name__ == "__main__":
    main()