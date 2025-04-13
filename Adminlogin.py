import tkinter as tk
from tkinter import messagebox

# Hard-coded admin password
ADMIN_PASSWORD = "Alexisawesome"

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

# Function to open admin interface (this will be the next step after login)
def open_admin_interface():
    # You can set up the next part of the application here (admin functions)
    print("Admin Interface Opened")  # Placeholder for now

# Create the main window for the login screen
root = tk.Tk()
root.title("Admin Login")

# Create the username and password labels and entry fields
tk.Label(root, text="Enter Admin Password:").pack(pady=10)
password_entry = tk.Entry(root, width=30)  # No show="*" argument, so password is visible as you type
password_entry.pack(pady=10)

# Create a login button
login_button = tk.Button(root, text="Login", command=verify_password)
login_button.pack(pady=20)

# Run the application
root.mainloop()
