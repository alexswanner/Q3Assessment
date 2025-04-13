import tkinter as tk
from tkinter import messagebox
import sqlite3
import time

# Updated admin password
ADMIN_PASSWORD = "Alex"

# Function to verify password
def verify_password():
    entered_password = password_entry.get()  # Get the password entered by the user
    
    if entered_password == ADMIN_PASSWORD:
        # If correct password, show success message and open admin interface
        messagebox.showinfo("Success", "Login successful!")
        open_admin_interface()
    else:
        # If incorrect password, show error message
        messagebox.showerror("Error", "Incorrect password. Please try again.")

# Function to connect to the database with retry logic and thread safety
def connect_db_with_retry():
    attempts = 3
    while attempts > 0:
        try:
            # Use check_same_thread=False for thread safety
            conn = sqlite3.connect('quiz_bowl.db', check_same_thread=False)
            return conn
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempts > 0:
                print("Database is locked, retrying...")
                time.sleep(1)  # Wait for 1 second before retrying
                attempts -= 1
            else:
                raise
    raise sqlite3.OperationalError("Failed to connect to the database after multiple attempts.")

# Function to add question to the selected course (table) in the database
def add_question_to_db():
    # Get the input from the entry fields
    question_text = question_entry.get()
    option_1 = option_1_entry.get()
    option_2 = option_2_entry.get()
    option_3 = option_3_entry.get()
    option_4 = option_4_entry.get()
    correct_answer = correct_answer_var.get()
    selected_course = course_var.get()

    # Ensure no fields are empty
    if not question_text or not option_1 or not option_2 or not option_3 or not option_4:
        messagebox.showerror("Error", "All fields must be filled out.")
        return

    # Connect to the SQLite database with retry logic
    conn = connect_db_with_retry()
    cursor = conn.cursor()

    try:
        # Insert the new question into the selected course's table
        cursor.execute(f'''
            INSERT INTO {selected_course} (question_text, option_1, option_2, option_3, option_4, correct_answer)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (question_text, option_1, option_2, option_3, option_4, correct_answer))

        # Commit the transaction and close the connection
        conn.commit()
        messagebox.showinfo("Success", "Question added successfully!")

    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        messagebox.showerror("Error", "Failed to add question to the database.")

    finally:
        conn.close()  # Always close the connection

    # Clear the form fields after submission
    clear_form()

# Function to clear the form fields
def clear_form():
    question_entry.delete(0, tk.END)
    option_1_entry.delete(0, tk.END)
    option_2_entry.delete(0, tk.END)
    option_3_entry.delete(0, tk.END)
    option_4_entry.delete(0, tk.END)
    correct_answer_var.set(1)

# Function to open the admin interface after login
def open_admin_interface():
    admin_window = tk.Toplevel(root)
    admin_window.title("Admin Interface")

    # Label and input for the question
    tk.Label(admin_window, text="Enter the Question:").pack(pady=10)
    global question_entry
    question_entry = tk.Entry(admin_window, width=50)
    question_entry.pack(pady=10)

    # Labels and inputs for the options
    tk.Label(admin_window, text="Option 1:").pack(pady=5)
    global option_1_entry
    option_1_entry = tk.Entry(admin_window, width=50)
    option_1_entry.pack(pady=5)

    tk.Label(admin_window, text="Option 2:").pack(pady=5)
    global option_2_entry
    option_2_entry = tk.Entry(admin_window, width=50)
    option_2_entry.pack(pady=5)

    tk.Label(admin_window, text="Option 3:").pack(pady=5)
    global option_3_entry
    option_3_entry = tk.Entry(admin_window, width=50)
    option_3_entry.pack(pady=5)

    tk.Label(admin_window, text="Option 4:").pack(pady=5)
    global option_4_entry
    option_4_entry = tk.Entry(admin_window, width=50)
    option_4_entry.pack(pady=5)

    # Combobox for selecting the correct answer
    tk.Label(admin_window, text="Select Correct Answer (1-4):").pack(pady=10)
    global correct_answer_var
    correct_answer_var = tk.IntVar(value=1)
    correct_answer_combobox = tk.Spinbox(admin_window, from_=1, to=4, textvariable=correct_answer_var)
    correct_answer_combobox.pack(pady=10)

    # Dropdown to select which course/table to add the question to (no default selection)
    tk.Label(admin_window, text="Select Course:").pack(pady=10)
    global course_var
    course_var = tk.StringVar()
    course_dropdown = tk.OptionMenu(admin_window, course_var, 
                                    "ethics_questions", "philosophy_questions", 
                                    "business_apps_questions", "database_management_questions", "finance_questions")
    course_dropdown.pack(pady=10)

    # Submit button to add the question
    add_button = tk.Button(admin_window, text="Add Question", command=add_question_to_db)
    add_button.pack(pady=20)

    # Cancel/Close button
    close_button = tk.Button(admin_window, text="Close", command=admin_window.destroy)
    close_button.pack(pady=5)

# Create the main window for the login screen
root = tk.Tk()
root.title("Admin Login")

# Create the username and password labels and entry fields
tk.Label(root, text="Enter Admin Password:").pack(pady=10)
password_entry = tk.Entry(root, width=30)
password_entry.pack(pady=10)

# Create a login button
login_button = tk.Button(root, text="Login", command=verify_password)
login_button.pack(pady=20)

# Run the application
root.mainloop()
