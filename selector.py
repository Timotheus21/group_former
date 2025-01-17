import tkinter as tk
from tkinter.filedialog import askopenfilename
import sys

def select_file():
    # Create a temporary file dialog to select a file
    try:
        temp_root = tk.Tk()
        temp_root.withdraw()
        file_path = askopenfilename(title="Select a Questionnaire CSV file", filetypes=[("CSV files", "*.csv")])
        temp_root.destroy()
        return file_path
    except Exception as e:
        print(f"Error selecting file: {e}")
        sys.exit(1)