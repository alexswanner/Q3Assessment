import tkinter as tk
from tkinter import messagebox
import sqlite3
import time


# Hard-coded admin password
ADMIN_PASSWORD = "Alex"

# Global variables
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
root = None
quiz_window = None
current_question_idx = 0
user_score = 0
user_answer_var = None
selected_course = None
questions = []  # List to store the quiz questions for the student
header_frame = None
content_frame = None
nav_frame = None
score_label = None  # New global variable for score tracking


# Database connection function
def connect_db():
    try:
        conn = sqlite3.connect('quiz_bowl.db', check_same_thread=False)
        return conn
    except sqlite3.OperationalError as e:
        messagebox.showerror("Database Error", f"Failed to connect to the database.\n\nError: {e}")
        raise e


# Function to execute queries
def execute_query(query, params=(), fetch=False):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        conn.commit()
    except sqlite3.OperationalError as e:
        messagebox.showerror("Database Error", f"Database operation failed.\nError: {e}")
        return None
    finally:
        conn.close()


# Question class for OOP approach
class Question:
    def __init__(self, question_id, question_text, options, correct_answer):
        self.question_id = question_id
        self.question_text = question_text
        self.options = options  # List of 4 options
        self.correct_answer = correct_answer
    
    def check_answer(self, selected_answer):
        return selected_answer == self.correct_answer
    
    @staticmethod
    def from_db_row(row):
        return Question(
            question_id=row[0],
            question_text=row[1],
            options=[row[2], row[3], row[4], row[5]],
            correct_answer=row[6]
        )


# Function to initialize the database and create tables
def initialize_database():
    conn = connect_db()
    cursor = conn.cursor()
    
    courses = ["ethics_questions", "philosophy_questions", 
               "business_apps_questions", "database_management_questions", 
               "finance_questions"]
    
    for course in courses:
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {course} (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL,
            option_1 TEXT NOT NULL,
            option_2 TEXT NOT NULL,
            option_3 TEXT NOT NULL,
            option_4 TEXT NOT NULL,
            correct_answer INTEGER NOT NULL
        )
        ''')
    
    conn.commit()
    conn.close()


# Function to verify password
def verify_password():
    entered_password = password_entry.get()  # Get the password entered by the user
    
    if entered_password == ADMIN_PASSWORD:
        messagebox.showinfo("Success", "Login successful!")
        open_admin_interface()
    else:
        messagebox.showerror("Error", "Incorrect password. Please try again.")


# Function to open the admin interface
def open_admin_interface():
    global question_entry, option_1_entry, option_2_entry, option_3_entry, option_4_entry, correct_answer_var
    global course_var, question_listbox, save_button

    admin_window = tk.Toplevel(root)
    admin_window.title("Admin Interface - Quiz Bowl")
    admin_window.geometry("800x600")

    # Course selection
    course_frame = tk.Frame(admin_window)
    course_frame.pack(pady=10)
    
    tk.Label(course_frame, text="Select Course:").pack(side=tk.LEFT, padx=5)
    
    course_var = tk.StringVar()
    course_options = [
        ("Ethics", "ethics_questions"),
        ("Philosophy", "philosophy_questions"),
        ("Business Applications", "business_apps_questions"),
        ("Database Management", "database_management_questions"),
        ("Finance", "finance_questions")
    ]
    
    course_dropdown = tk.OptionMenu(course_frame, course_var, *[option[1] for option in course_options])
    course_dropdown.pack(side=tk.LEFT, padx=5)
    
    # Form for adding/editing questions
    form_frame = tk.Frame(admin_window)
    form_frame.pack(pady=10)
    
    tk.Label(form_frame, text="Question:").grid(row=0, column=0, sticky=tk.W, pady=5)
    question_entry = tk.Entry(form_frame, width=50)
    question_entry.grid(row=0, column=1, pady=5)
    
    tk.Label(form_frame, text="Option 1:").grid(row=1, column=0, sticky=tk.W, pady=5)
    option_1_entry = tk.Entry(form_frame, width=50)
    option_1_entry.grid(row=1, column=1, pady=5)
    
    tk.Label(form_frame, text="Option 2:").grid(row=2, column=0, sticky=tk.W, pady=5)
    option_2_entry = tk.Entry(form_frame, width=50)
    option_2_entry.grid(row=2, column=1, pady=5)
    
    tk.Label(form_frame, text="Option 3:").grid(row=3, column=0, sticky=tk.W, pady=5)
    option_3_entry = tk.Entry(form_frame, width=50)
    option_3_entry.grid(row=3, column=1, pady=5)
    
    tk.Label(form_frame, text="Option 4:").grid(row=4, column=0, sticky=tk.W, pady=5)
    option_4_entry = tk.Entry(form_frame, width=50)
    option_4_entry.grid(row=4, column=1, pady=5)
    
    tk.Label(form_frame, text="Correct Answer:").grid(row=5, column=0, sticky=tk.W, pady=5)
    correct_answer_var = tk.IntVar(value=1)
    
    # Radio buttons for selecting the correct answer
    radio_frame = tk.Frame(form_frame)
    radio_frame.grid(row=5, column=1, sticky=tk.W)
    
    for i in range(1, 5):
        tk.Radiobutton(radio_frame, text=f"Option {i}", variable=correct_answer_var, value=i).pack(side=tk.LEFT, padx=10)
    
    # Buttons for CRUD operations
    button_frame = tk.Frame(admin_window)
    button_frame.pack(pady=10)
    
    add_button = tk.Button(button_frame, text="Add Question", command=add_question_to_db)
    add_button.pack(side=tk.LEFT, padx=10)
    
    view_button = tk.Button(button_frame, text="View Questions", command=view_questions)
    view_button.pack(side=tk.LEFT, padx=10)
    
    delete_button = tk.Button(button_frame, text="Delete Question", command=delete_question)
    delete_button.pack(side=tk.LEFT, padx=10)
    
    # Modified save button (the save button is now properly connected to update_question)
    save_button = tk.Button(button_frame, text="Save Changes", state=tk.DISABLED)
    save_button.pack(side=tk.LEFT, padx=10)
    
    clear_button = tk.Button(button_frame, text="Clear Form", command=clear_form)
    clear_button.pack(side=tk.LEFT, padx=10)
    
    back_button = tk.Button(
        admin_window,
        text="Back to Main Menu",
        command=lambda: [admin_window.destroy(), root.deiconify()]
    )
    back_button.pack(pady=10)
    
    # Listbox to display questions
    listbox_frame = tk.Frame(admin_window)
    listbox_frame.pack(pady=10, fill=tk.BOTH, expand=True)
    
    tk.Label(listbox_frame, text="Questions:").pack(anchor=tk.W)
    
    question_listbox = tk.Listbox(listbox_frame, width=80, height=10)
    question_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    question_listbox.bind("<Double-1>", modify_question)
    
    scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=question_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    question_listbox.config(yscrollcommand=scrollbar.set)


# Function to clear the form fields
def clear_form():
    question_entry.delete(0, tk.END)
    option_1_entry.delete(0, tk.END)
    option_2_entry.delete(0, tk.END)
    option_3_entry.delete(0, tk.END)
    option_4_entry.delete(0, tk.END)
    correct_answer_var.set(1)
    
    # Reset save button state
    save_button.config(state=tk.DISABLED, command=None)


# Function to add a question to the selected course
def add_question_to_db():
    question_text = question_entry.get()
    option_1 = option_1_entry.get()
    option_2 = option_2_entry.get()
    option_3 = option_3_entry.get()
    option_4 = option_4_entry.get()
    correct_answer = correct_answer_var.get()
    selected_course = course_var.get()

    if not question_text or not option_1 or not option_2 or not option_3 or not option_4:
        messagebox.showerror("Error", "All fields must be filled out.")
        return
    
    if not selected_course:
        messagebox.showerror("Error", "Please select a course.")
        return

    execute_query(f'''
        INSERT INTO {selected_course} (question_text, option_1, option_2, option_3, option_4, correct_answer)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (question_text, option_1, option_2, option_3, option_4, correct_answer))

    messagebox.showinfo("Success", "Question added successfully!")
    clear_form()


# Function to view questions
def view_questions():
    selected_course = course_var.get()

    valid_courses = ["ethics_questions", "philosophy_questions", "business_apps_questions", 
                     "database_management_questions", "finance_questions"]
    
    if selected_course not in valid_courses:
        messagebox.showerror("Error", "Invalid course selected.")
        return

    questions = execute_query(f'SELECT question_id, question_text FROM {selected_course}', fetch=True)

    if not questions:
        messagebox.showinfo("Info", "No questions available in this course.")
        return

    question_listbox.delete(0, tk.END)
    for question in questions:
        question_listbox.insert(tk.END, f"{question[1]} (ID: {question[0]})")


# Function to modify a question
def modify_question(event=None):
    selected_index = question_listbox.curselection()
    
    if not selected_index:
        messagebox.showerror("Error", "Please select a question to modify.")
        return
    
    selected_question_text = question_listbox.get(selected_index)
    question_id = selected_question_text.split(' (ID: ')[1][:-1]  

    selected_course = course_var.get()

    question = execute_query(f'SELECT * FROM {selected_course} WHERE question_id = ?', (question_id,), fetch=True)[0]

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

    # Configure the save button to call update_question with the current question_id
    save_button.config(state=tk.NORMAL, command=lambda: update_question(question_id))


# Function to update the selected question
def update_question(question_id):
    updated_question_text = question_entry.get()
    updated_option_1 = option_1_entry.get()
    updated_option_2 = option_2_entry.get()
    updated_option_3 = option_3_entry.get()
    updated_option_4 = option_4_entry.get()
    updated_correct_answer = correct_answer_var.get()

    if not updated_question_text or not updated_option_1 or not updated_option_2 or not updated_option_3 or not updated_option_4:
        messagebox.showerror("Error", "All fields must be filled out.")
        return

    selected_course = course_var.get()
    
    execute_query(f'''
        UPDATE {selected_course} 
        SET question_text = ?, option_1 = ?, option_2 = ?, option_3 = ?, option_4 = ?, correct_answer = ? 
        WHERE question_id = ?
    ''', (updated_question_text, updated_option_1, updated_option_2, updated_option_3, updated_option_4, updated_correct_answer, question_id))

    messagebox.showinfo("Success", "Question updated successfully!")
    clear_form()
    view_questions()


# Function to delete a question
def delete_question():
    selected_index = question_listbox.curselection()

    if not selected_index:
        messagebox.showerror("Error", "Please select a question to delete.")
        return

    selected_question_text = question_listbox.get(selected_index)
    question_id = selected_question_text.split(' (ID: ')[1][:-1]

    selected_course = course_var.get()

    confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this question?")
    if not confirm:
        return

    execute_query(f'DELETE FROM {selected_course} WHERE question_id = ?', (question_id,))
    messagebox.showinfo("Success", "Question deleted successfully.")
    view_questions()


# Function to open the admin login window
def open_admin_login():
    global password_entry
    
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
    def verify_admin_password():
        entered_password = password_entry.get()
        
        if entered_password == ADMIN_PASSWORD:  # Check if the entered password is correct
            messagebox.showinfo("Success", "Login successful!")
            admin_window.destroy()  # Close the login window
            open_admin_interface()  # If password is correct, open the admin interface
        else:
            messagebox.showerror("Error", "Incorrect password. Please try again.")  # Show error message if password is wrong
    
    # Button to submit the password
    login_button = tk.Button(admin_window, text="Login", command=verify_admin_password)
    login_button.pack(pady=20)
    
    # Button to go back to the main menu
    back_button = tk.Button(
        admin_window,
        text="Back",
        command=lambda: [admin_window.destroy(), root.deiconify()]
    )
    back_button.pack(pady=5)


# Function to open the student interface
def open_student_interface():
    root.withdraw()  # Hide the initial window

    student_window = tk.Toplevel(root)
    student_window.title("Select a Quiz")

    student_window.geometry("400x400")

    tk.Label(student_window, text="Quiz Bowl", font=("Arial", 20, "bold")).pack(pady=10)
    tk.Label(student_window, text="Choose a Subject for Your Quiz", font=("Arial", 12)).pack(pady=10)

    course_frame = tk.Frame(student_window)
    course_frame.pack(pady=20)

    course_display_names = {
        "ethics_questions": "Ethics",
        "philosophy_questions": "Philosophy",
        "business_apps_questions": "Business Applications",
        "database_management_questions": "Database Management",
        "finance_questions": "Finance"
    }

    for db_name, display_name in course_display_names.items():
        button = tk.Button(
            course_frame, 
            text=display_name, 
            width=25, 
            height=2,
            command=lambda c=db_name: start_quiz(c, student_window),
            font=("Arial", 10)
        )
        button.pack(pady=8)

    back_button = tk.Button(
        student_window,
        text="Back to Main Menu",
        command=lambda: [student_window.destroy(), root.deiconify()]
    )
    back_button.pack(pady=15)


# Function to start the quiz for the selected course
def start_quiz(course_name, selection_window):
    global current_question_idx, user_score, selected_course, questions
    
    # Initialize quiz state
    current_question_idx = 0
    user_score = 0
    selected_course = course_name
    
    # Fetch questions for the selected course
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f'''
            SELECT question_id, question_text, option_1, option_2, option_3, option_4, correct_answer 
            FROM {course_name}
        ''')
        
        db_questions = cursor.fetchall()
        
        if not db_questions:
            messagebox.showinfo("No Questions", f"No questions found for this subject. Please try another one.")
            return
        
        # Convert database rows to Question objects
        questions = [Question.from_db_row(row) for row in db_questions]
        
        # Close the course selection window
        selection_window.destroy()
        
        # Create and show the quiz window
        create_quiz_window()
        
    except sqlite3.OperationalError as e:
        messagebox.showerror("Database Error", f"Could not load quiz questions: {e}")
        print(f"Database error: {e}")
    finally:
        conn.close()


# Function to create the quiz window (fixed to avoid stacking questions)
def create_quiz_window():
    global quiz_window, user_answer_var, header_frame, content_frame, nav_frame, score_label
    
    quiz_window = tk.Toplevel(root)
    quiz_window.title("Quiz Bowl - Test Your Knowledge")
    quiz_window.geometry("700x500")
    
    # Header frame
    header_frame = tk.Frame(quiz_window)
    header_frame.pack(pady=10, fill=tk.X)
    
    # Add title and score tracker in the header
    title_frame = tk.Frame(header_frame)
    title_frame.pack(side=tk.LEFT, padx=20)
    
    tk.Label(title_frame, text="Quiz Bowl", font=("Arial", 24, "bold")).pack(anchor=tk.W)
    
    # Add score tracker to the right side of header
    score_frame = tk.Frame(header_frame)
    score_frame.pack(side=tk.RIGHT, padx=20)
    
    score_label = tk.Label(
        score_frame, 
        text=f"Score: {user_score}/{len(questions)}", 
        font=("Arial", 14, "bold"),
        fg="green"
    )
    score_label.pack(anchor=tk.E)
    
    # Create content frame for question and options
    content_frame = tk.Frame(quiz_window)
    content_frame.pack(pady=20, fill=tk.BOTH, expand=True)
    
    # User answer variable
    user_answer_var = tk.IntVar()
    
    # Navigation buttons frame
    nav_frame = tk.Frame(quiz_window)
    nav_frame.pack(side=tk.BOTTOM, pady=20)
    
    submit_button = tk.Button(nav_frame, text="Submit Answer", command=check_answer)
    submit_button.pack(side=tk.LEFT, padx=10)
    
    quit_button = tk.Button(nav_frame, text="Quit Quiz", command=end_quiz)
    quit_button.pack(side=tk.LEFT, padx=10)
    
    # Load the first question
    display_question()


# Function to display the current question (fixed to avoid stacking questions)
def display_question():
    global content_frame, user_answer_var, current_question_idx, score_label
    
    # Clear the content frame first
    for widget in content_frame.winfo_children():
        widget.destroy()
    
    # Get current question
    question = questions[current_question_idx]
    
    # Display question number and text
    tk.Label(
        content_frame, 
        text=f"Question {current_question_idx + 1} of {len(questions)}", 
        font=("Arial", 12, "bold")
    ).pack(anchor=tk.W, padx=20)
    
    tk.Label(
        content_frame, 
        text=question.question_text, 
        font=("Arial", 14),
        wraplength=600,
        justify=tk.LEFT
    ).pack(anchor=tk.W, padx=20, pady=10)
    
    # Display options
    options_frame = tk.Frame(content_frame)
    options_frame.pack(anchor=tk.W, padx=20, pady=10)
    
    # Reset the user answer variable
    user_answer_var.set(0)
    
    # Display radio buttons for each option
    for i, option_text in enumerate(question.options, 1):
        tk.Radiobutton(
            options_frame,
            text=option_text,
            variable=user_answer_var,
            value=i,
            font=("Arial", 12)
        ).pack(anchor=tk.W, pady=5)
    
    # Update score display
    score_label.config(text=f"Score: {user_score}/{len(questions)}")


# Function to check the current answer
def check_answer():
    global user_score, current_question_idx, score_label
    
    # Check if an answer is selected
    if user_answer_var.get() == 0:
        messagebox.showwarning("No Selection", "Please select an answer before submitting.")
        return
    
    current_question = questions[current_question_idx]
    selected_answer = user_answer_var.get()
    
    # Check if the answer is correct
    is_correct = current_question.check_answer(selected_answer)
    
    if is_correct:
        user_score += 1
        messagebox.showinfo("Correct!", "Your answer is correct!")
        # Update the score label immediately
        score_label.config(text=f"Score: {user_score}/{len(questions)}")
    else:
        correct_option = current_question.options[current_question.correct_answer - 1]
        messagebox.showinfo("Incorrect", f"Sorry, the correct answer was: {correct_option}")
    
    # Move to the next question or end the quiz
    current_question_idx += 1
    
    if current_question_idx < len(questions):
        display_question()
    else:
        show_final_score()


# Function to show the final score
def show_final_score():
    # Clear the window
    for widget in quiz_window.winfo_children():
        widget.destroy()
    
    # Create results frame
    results_frame = tk.Frame(quiz_window)
    results_frame.pack(pady=50)
    
    # Display final score
    tk.Label(
        results_frame,
        text="Quiz Completed!",
        font=("Arial", 24, "bold")
    ).pack(pady=20)
    
    tk.Label(
        results_frame,
        text=f"Your Score: {user_score} out of {len(questions)}",
        font=("Arial", 18)
    ).pack(pady=10)
    
    percentage = (user_score / len(questions)) * 100
    
    tk.Label(
        results_frame,
        text=f"Percentage: {percentage:.1f}%",
        font=("Arial", 16)
    ).pack(pady=10)
    
    # Add buttons to restart or return to main menu
    button_frame = tk.Frame(quiz_window)
    button_frame.pack(pady=30)
    
    restart_button = tk.Button(
        button_frame,
        text="Take Another Quiz",
        command=lambda: [quiz_window.destroy(), open_student_interface()]
    )
    restart_button.pack(side=tk.LEFT, padx=10)
    
    main_menu_button = tk.Button(
        button_frame,
        text="Return to Main Menu",
        command=lambda: [quiz_window.destroy(), root.deiconify()]
    )
    main_menu_button.pack(side=tk.LEFT, padx=10)


# Function to end the quiz early
def end_quiz():
    if messagebox.askyesno("Quit Quiz", "Are you sure you want to quit this quiz? Your progress will be lost."):
        quiz_window.destroy()
        root.deiconify()


# Main entry point for the application
def open_initial_window():
    global root
    initialize_database()

    root = tk.Tk()
    root.title("Quiz Bowl Application")
    root.geometry("500x400")

    header_label = tk.Label(
        root,
        text="Quiz Bowl Application",
        font=("Arial", 24, "bold")
    )
    header_label.pack(pady=30)

    subheader_label = tk.Label(
        root,
        text="Choose your role to continue",
        font=("Arial", 14)
    )
    subheader_label.pack(pady=20)

    button_frame = tk.Frame(root)
    button_frame.pack(pady=40)

    admin_button = tk.Button(
        button_frame,
        text="Administrator",
        width=15,
        height=2,
        command=open_admin_login,
        font=("Arial", 12)
    )
    admin_button.pack(side=tk.LEFT, padx=20)

    student_button = tk.Button(
        button_frame,
        text="Student",
        width=15,
        height=2,
        command=open_student_interface,
        font=("Arial", 12)
    )
    student_button.pack(side=tk.RIGHT, padx=20)

    exit_button = tk.Button(
        root,
        text="Exit",
        width=10,
        command=root.destroy,
        font=("Arial", 10)
    )
    exit_button.pack(pady=10)

    root.mainloop()


# Run the initial window when the script is executed
if __name__ == "__main__":
    open_initial_window()