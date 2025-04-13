import tkinter as tk
from tkinter import messagebox
import sqlite3
import time

# Hard-coded admin password
ADMIN_PASSWORD = "Alex"

# Global variables for the form entries and buttons
password_entry = None
question_entry = None
option_1_entry = None
option_2_entry = None
option_3_entry = None
option_4_entry = None
correct_answer_var = None
course_var = None
question_listbox = None
save_button = None
root = None  # Define root here so it's accessible globally

# Current quiz for student
current_quiz = None
current_question_idx = 0
questions = []

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

# Function to view questions from the selected course
def view_questions():
    selected_course = course_var.get()

    # Ensure the course name is valid (matches an actual table)
    if selected_course not in ["ethics_questions", "philosophy_questions", "business_apps_questions", "database_management_questions", "finance_questions"]:
        messagebox.showerror("Error", "Invalid course selected.")
        return

    # Connect to the SQLite database
    conn = connect_db_with_retry()
    cursor = conn.cursor()

    try:
        # Fetch all questions from the selected course
        cursor.execute(f'SELECT question_id, question_text FROM {selected_course}')
        questions = cursor.fetchall()

        # Clear the Listbox before displaying new questions
        question_listbox.delete(0, tk.END)

        # Check if any questions were returned
        if not questions:
            messagebox.showinfo("Info", "No questions available in this course.")
            return

        # Add questions to the Listbox vertically
        for question in questions:
            # Displaying question text and ID in a vertical list
            question_listbox.insert(tk.END, f"{question[1]} (ID: {question[0]})")

    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")  # This will print the error to the console for debugging
        messagebox.showerror("Error", f"Failed to retrieve questions from the database.\n\nError: {e}")

    finally:
        conn.close()

# Function to modify the selected question
def modify_question(event=None):
    # Get the selected question's ID
    selected_index = question_listbox.curselection()
    
    if not selected_index:
        messagebox.showerror("Error", "Please select a question to modify.")
        return
    
    # Get the question text and question_id from the Listbox selection
    selected_question_text = question_listbox.get(selected_index)
    question_id = selected_question_text.split(' (ID: ')[1][:-1]  # Extract question_id from the text

    selected_course = course_var.get()

    # Connect to the SQLite database
    conn = connect_db_with_retry()
    cursor = conn.cursor()

    try:
        # Fetch the question details from the database
        cursor.execute(f'SELECT * FROM {selected_course} WHERE question_id = ?', (question_id,))
        question = cursor.fetchone()

        # Populate the form fields with the selected question's details
        question_entry.delete(0, tk.END)
        question_entry.insert(0, question[1])

        option_1_entry.delete(0, tk.END)
        option_1_entry.insert(0, question[2])

        option_2_entry.delete(0, tk.END)
        option_2_entry.insert(0, question[3])

        option_3_entry.delete(0, tk.END)
        option_3_entry.insert(0, question[4])

        option_4_entry.delete(0, tk.END)
        option_4_entry.insert(0, question[5])

        correct_answer_var.set(question[6])

        # Enable the save button and update its command
        save_button.config(state=tk.NORMAL, command=lambda: update_question(question_id))

    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        messagebox.showerror("Error", "Failed to retrieve question details.")

    finally:
        conn.close()

# Function to update the selected question in the database
def update_question(question_id):
    # Get the updated input from the entry fields
    updated_question_text = question_entry.get()
    updated_option_1 = option_1_entry.get()
    updated_option_2 = option_2_entry.get()
    updated_option_3 = option_3_entry.get()
    updated_option_4 = option_4_entry.get()
    updated_correct_answer = correct_answer_var.get()

    # Ensure no fields are empty
    if not updated_question_text or not updated_option_1 or not updated_option_2 or not updated_option_3 or not updated_option_4:
        messagebox.showerror("Error", "All fields must be filled out.")
        return

    # Connect to the SQLite database
    conn = connect_db_with_retry()
    cursor = conn.cursor()

    try:
        # Update the question in the database
        cursor.execute(f'''
            UPDATE {course_var.get()} 
            SET question_text = ?, option_1 = ?, option_2 = ?, option_3 = ?, option_4 = ?, correct_answer = ? 
            WHERE question_id = ?
        ''', (updated_question_text, updated_option_1, updated_option_2, updated_option_3, updated_option_4, updated_correct_answer, question_id))

        # Commit the transaction and close the connection
        conn.commit()
        messagebox.showinfo("Success", "Question updated successfully!")

        # Refresh the Listbox with updated questions
        view_questions()

    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        messagebox.showerror("Error", "Failed to update the question.")

    finally:
        conn.close()

# Function to delete the selected question
def delete_question():
    # Get the selected question's ID
    selected_index = question_listbox.curselection()

    if not selected_index:
        messagebox.showerror("Error", "Please select a question to delete.")
        return

    selected_question_text = question_listbox.get(selected_index)
    question_id = selected_question_text.split(' (ID: ')[1][:-1]  # Extract question_id from the text

    selected_course = course_var.get()

    # Confirm the deletion
    confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this question?")
    if not confirm:
        return

    # Connect to the SQLite database
    conn = connect_db_with_retry()
    cursor = conn.cursor()

    try:
        # Delete the selected question from the database
        cursor.execute(f'DELETE FROM {selected_course} WHERE question_id = ?', (question_id,))
        conn.commit()

        messagebox.showinfo("Success", "Question deleted successfully.")

        # Refresh the Listbox to show the updated questions
        view_questions()

    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        messagebox.showerror("Error", "Failed to delete the question.")

    finally:
        conn.close()

# Function to open the admin interface after login
def open_admin_interface():
    admin_window = tk.Toplevel(root)
    admin_window.title("Admin Interface")

    # Set a fixed window size (more square-shaped)
    admin_window.geometry("500x500")  # Adjusted to make it more square-shaped

    # Create a frame for the form fields
    form_frame = tk.Frame(admin_window)
    form_frame.pack(pady=10)

    # Labels and inputs for the question and options, laid out horizontally
    tk.Label(form_frame, text="Enter the Question:").grid(row=0, column=0, padx=5)
    global question_entry
    question_entry = tk.Entry(form_frame, width=50)
    question_entry.grid(row=0, column=1, padx=5)

    tk.Label(form_frame, text="Option 1:").grid(row=1, column=0, padx=5)
    global option_1_entry
    option_1_entry = tk.Entry(form_frame, width=50)
    option_1_entry.grid(row=1, column=1, padx=5)

    tk.Label(form_frame, text="Option 2:").grid(row=2, column=0, padx=5)
    global option_2_entry
    option_2_entry = tk.Entry(form_frame, width=50)
    option_2_entry.grid(row=2, column=1, padx=5)

    tk.Label(form_frame, text="Option 3:").grid(row=3, column=0, padx=5)
    global option_3_entry
    option_3_entry = tk.Entry(form_frame, width=50)
    option_3_entry.grid(row=3, column=1, padx=5)

    tk.Label(form_frame, text="Option 4:").grid(row=4, column=0, padx=5)
    global option_4_entry
    option_4_entry = tk.Entry(form_frame, width=50)
    option_4_entry.grid(row=4, column=1, padx=5)

    # Combobox for selecting the correct answer
    tk.Label(form_frame, text="Select Correct Answer (1-4):").grid(row=5, column=0, padx=5)
    global correct_answer_var
    correct_answer_var = tk.IntVar(value=1)
    correct_answer_combobox = tk.Spinbox(form_frame, from_=1, to=4, textvariable=correct_answer_var)
    correct_answer_combobox.grid(row=5, column=1, padx=5)

    # Dropdown to select which course/table to add the question to
    tk.Label(form_frame, text="Select Course:").grid(row=6, column=0, padx=5)
    global course_var
    course_var = tk.StringVar()
    course_dropdown = tk.OptionMenu(form_frame, course_var, 
                                    "ethics_questions", "philosophy_questions", 
                                    "business_apps_questions", "database_management_questions", "finance_questions")
    course_dropdown.grid(row=6, column=1, padx=5)

    # Submit button to add the question
    add_button = tk.Button(admin_window, text="Add Question", command=add_question_to_db)
    add_button.pack(pady=20)

    # Button to view questions
    view_button = tk.Button(admin_window, text="View Questions", command=view_questions)
    view_button.pack(pady=10)

    # Frame for the Listbox with vertical scrolling
    listbox_frame = tk.Frame(admin_window)
    listbox_frame.pack(pady=10)

    global question_listbox
    question_listbox = tk.Listbox(listbox_frame, width=80, height=5)
    question_listbox.pack(side=tk.LEFT, padx=10)

    # Add a vertical scrollbar to the listbox
    scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=question_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    question_listbox.config(yscrollcommand=scrollbar.set)

    # Button to modify the selected question
    modify_button = tk.Button(admin_window, text="Modify Question", command=modify_question)
    modify_button.pack(pady=5)

    # Button to save modifications
    global save_button
    save_button = tk.Button(admin_window, text="Save Changes", state=tk.DISABLED)
    save_button.pack(pady=5)

    # Button to delete the selected question
    delete_button = tk.Button(admin_window, text="Delete Question", command=delete_question)
    delete_button.pack(pady=5)

    # Cancel/Close button
    close_button = tk.Button(admin_window, text="Close", command=admin_window.destroy)
    close_button.pack(pady=5)

# Function to display available quizzes for student
def open_student_interface():
    root.withdraw()  # Hide the initial window

    # Create the student quiz window
    student_window = tk.Toplevel(root)
    student_window.title("Select a Quiz")

    # Set window size
    student_window.geometry("400x300")

    # Create a label and button for each available quiz (course)
    tk.Label(student_window, text="Choose a Quiz", font=("Arial", 16)).pack(pady=20)

    course_list = ["ethics_questions", "philosophy_questions", "business_apps_questions", "database_management_questions", "finance_questions"]

    for course in course_list:
        button = tk.Button(student_window, text=course, width=20, command=lambda c=course: start_quiz(c, student_window))
        button.pack(pady=5)

# Function to start the quiz by loading questions
def start_quiz(course_name, student_window):
    global current_quiz, current_question_idx, questions
    current_quiz = course_name
    current_question_idx = 0

    # Fetch questions for the selected quiz
    conn = connect_db_with_retry()
    cursor = conn.cursor()
    cursor.execute(f'SELECT question_id, question_text, option_1, option_2, option_3, option_4, correct_answer FROM {course_name}')
    questions = cursor.fetchall()
    conn.close()

    if not questions:
        messagebox.showinfo("No Questions", "No questions found for this quiz.")
        student_window.destroy()
        return

    # Start displaying questions
    show_question(student_window)

# Function to display the current question
def show_question(student_window):
    global current_question_idx, questions
    if current_question_idx >= len(questions):
        messagebox.showinfo("Quiz Completed", "Congratulations! You have completed the quiz.")
        student_window.destroy()
        return

    question = questions[current_question_idx]
    
    # Create the question display
    question_text = question[1]
    options = question[2:6]  # The 4 options

    tk.Label(student_window, text=question_text).pack(pady=10)

    for i, option in enumerate(options, 1):
        tk.Radiobutton(student_window, text=option, value=i, variable=correct_answer_var).pack(pady=5)

    # Submit button for the question
    submit_button = tk.Button(student_window, text="Submit Answer", command=lambda: check_answer(student_window))
    submit_button.pack(pady=20)

# Function to check the student's answer
def check_answer(student_window):
    global current_question_idx, questions
    selected_answer = correct_answer_var.get()
    correct_answer = questions[current_question_idx][6]  # The correct answer

    if selected_answer == correct_answer:
        messagebox.showinfo("Correct", "You got it right!")
    else:
        messagebox.showerror("Incorrect", f"The correct answer was: {correct_answer}")

    # Move to the next question
    current_question_idx += 1
    student_window.destroy()  # Close current window
    open_student_interface()  # Open a new window for the next question


# Function to open the admin login window
def open_admin_login():
    root.withdraw()  # Hide the initial window when moving to the login screen
    
    # Create the admin login window
    admin_window = tk.Toplevel(root)
    admin_window.title("Admin Login")
    
    # Set the window size
    admin_window.geometry("400x200")
    
    # Label for the password prompt
    tk.Label(admin_window, text="Enter Admin Password:", font=("Arial", 14)).pack(pady=10)
    
    # Password entry field (masked input for security)
    password_entry = tk.Entry(admin_window, width=30, show="*")
    password_entry.pack(pady=10)
    
    # Function to verify the entered password
    def verify_password():
        entered_password = password_entry.get()
        
        if entered_password == ADMIN_PASSWORD:  # Check if the entered password is correct
            messagebox.showinfo("Success", "Login successful!")
            open_admin_interface()  # If password is correct, open the admin interface
            admin_window.destroy()  # Close the login window
        else:
            messagebox.showerror("Error", "Incorrect password. Please try again.")  # Show error message if password is wrong

    # Button to submit the password
    login_button = tk.Button(admin_window, text="Login", command=verify_password)
    login_button.pack(pady=20)


# Function to open the initial window where the user chooses their role (Admin or Student)
def open_initial_window():
    global root
    root = tk.Tk()  # Define root here
    root.title("Quiz Bowl Application")

    root.geometry("400x300")

    # Add a label to indicate the role selection
    tk.Label(root, text="Choose your role", font=("Arial", 16)).pack(pady=20)

    # Add the button for Admin
    admin_button = tk.Button(root, text="Admin", width=20, command=open_admin_login)
    admin_button.pack(pady=10)

    # Add the button for Student
    student_button = tk.Button(root, text="Student", width=20, command=open_student_interface)
    student_button.pack(pady=10)

    root.mainloop()


# Run the initial window
open_initial_window()  # This will run the initial selection window first
