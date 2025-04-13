import tkinter as tk
from tkinter import messagebox
import sqlite3
import random

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

# Function to open the quiz interface
def open_quiz_interface(selected_course, category_window):
    quiz_window = tk.Toplevel(root)
    quiz_window.title(f"Quiz - {selected_course}")
    
    # Set a fixed window size (more square-shaped)
    quiz_window.geometry("500x500")
    
    # Debug: print which table is being accessed
    print(f"Accessing quiz data from the {selected_course} table...")

    # Retrieve questions for the selected course
    conn = connect_db_with_retry()
    cursor = conn.cursor()
    cursor.execute(f"SELECT question_id, question_text, option_1, option_2, option_3, option_4, correct_answer FROM {selected_course}")
    questions = cursor.fetchall()
    conn.close()

    # Debug: check if questions were retrieved
    print(f"Questions fetched: {len(questions)} questions found.")
    
    if not questions:
        messagebox.showerror("Error", "No questions found for this quiz.")
        category_window.destroy()  # Close the category window
        return
    
    # Shuffle the questions to randomize order
    random.shuffle(questions)

    # Initialize quiz variables
    current_question = 0
    total_questions = len(questions)
    correct_answers = 0

    # Create a label to display the score
    score_label = tk.Label(quiz_window, text=f"Score: {correct_answers} / {total_questions}", font=('Arial', 12))
    score_label.pack(pady=10)

    # Function to display the next question
    def display_question():
        nonlocal current_question
        if current_question >= total_questions:
            show_results(category_window)
            return
        
        question = questions[current_question]
        
        # Clear the current question display
        for widget in quiz_window.winfo_children():
            widget.destroy()

        # Display the score label at the top
        score_label.config(text=f"Score: {correct_answers} / {total_questions}")
        score_label.pack(pady=10)

        # Display the question
        question_label = tk.Label(quiz_window, text=question[1], font=('Arial', 16))
        question_label.pack(pady=20)
        
        # Feedback label for showing correct/incorrect
        feedback_label = tk.Label(quiz_window, text="", font=('Arial', 12), fg="green")
        feedback_label.pack(pady=5)

        # Display the answer options
        def check_answer(selected_option):
            nonlocal current_question, correct_answers
            # Check if the answer is correct
            if selected_option == question[6]:
                correct_answers += 1
                feedback_label.config(text="Correct!", fg="green")
            else:
                feedback_label.config(text=f"Incorrect! Correct Answer: {question[6]}", fg="red")
            # Update the score label
            score_label.config(text=f"Score: {correct_answers} / {total_questions}")
            current_question += 1
            display_question()

        # Increase the width of the buttons and set a high wraplength, allowing the button to auto-expand vertically
        option_1_button = tk.Button(quiz_window, text=question[2], command=lambda: check_answer(1), width=60, wraplength=450)
        option_1_button.pack(pady=5, fill='both')
        
        option_2_button = tk.Button(quiz_window, text=question[3], command=lambda: check_answer(2), width=60, wraplength=450)
        option_2_button.pack(pady=5, fill='both')
        
        option_3_button = tk.Button(quiz_window, text=question[4], command=lambda: check_answer(3), width=60, wraplength=450)
        option_3_button.pack(pady=5, fill='both')
        
        option_4_button = tk.Button(quiz_window, text=question[5], command=lambda: check_answer(4), width=60, wraplength=450)
        option_4_button.pack(pady=5, fill='both')

    # Function to show results
    def show_results(category_window):
        results_window = tk.Toplevel(quiz_window)
        results_window.title("Quiz Results")
        
        # Set window size for results
        results_window.geometry("300x200")
        
        # Display score
        score_label = tk.Label(results_window, text=f"You scored {correct_answers} out of {total_questions}!", font=('Arial', 14))
        score_label.pack(pady=30)
        
        # Close button for results window
        close_button = tk.Button(results_window, text="Close", command=results_window.destroy)
        close_button.pack(pady=10)

        # Close the quiz window and go back to the category window
        results_window.protocol("WM_DELETE_WINDOW", lambda: category_window.destroy())
        quiz_window.destroy()

    # Start displaying the questions
    display_question()

# Function to open the category selection screen
def open_category_selection():
    category_window = tk.Toplevel(root)
    category_window.title("Select Quiz Category")
    
    # Set window size for category selection
    category_window.geometry("400x300")  # Larger window size to fit all options

    # Categories (these should match the table names in your database)
    categories = ["ethics_questions", "philosophy_questions", "business_apps_questions", "database_management_questions", "finance_questions"]

    # Function to start quiz based on selected category
    def start_quiz(selected_category):
        open_quiz_interface(selected_category, category_window)
        category_window.destroy()
    
    # Create a button for each category
    for category in categories:
        category_button = tk.Button(category_window, text=category.replace("_", " ").title(), 
                                    command=lambda cat=category: start_quiz(cat), width=30)
        category_button.pack(pady=10)

# Function to open the main interface (category selection)
def open_main_interface():
    open_category_selection()

# Create the main window for the quiz selection screen
root = tk.Tk()
root.title("Quiz Bowl Application")

# Set window size
root.geometry("500x500")

# Welcome label
welcome_label = tk.Label(root, text="Hello! Please select a quiz to take!", font=('Arial', 20))
welcome_label.pack(pady=50)

# Button to start quiz
start_button = tk.Button(root, text="Start Quiz", command=open_main_interface, width=30, height=2)
start_button.pack(pady=20)

# Run the application
root.mainloop()
