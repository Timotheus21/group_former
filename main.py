import tkinter as tk
from tkinter.filedialog import askopenfilename
import sys
from dataprocessor import DataProcessor
from teamforming import TeamForming
from visualization import Visualization
from tooltip import Tooltip
from config import Config
from gui import GUI


def on_closing(root):
    print("Exiting...")
    root.quit()
    root.destroy()

def select_file():
    # Create a temporary file dialog to select a file
    temp_root = tk.Tk()
    temp_root.withdraw()
    file_path = askopenfilename(title="Select a Questionnaire CSV file", filetypes=[("CSV files", "*.csv")])
    temp_root.destroy()
    return file_path

if __name__ == "__main__":
    filepath = select_file()
    if not filepath:
        print("No file selected. Exiting...")
        sys.exit()

    root = tk.Tk()

    data_processor = DataProcessor(filepath)
    teamforming = TeamForming(data_processor)
    visualization = Visualization(data_processor)
    tooltip = Tooltip
    config = Config

    # Set protocol for closing the window
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
    
    # Initialize and run the GUI
    gui = GUI(root, data_processor, teamforming, visualization, tooltip)
    root.mainloop()