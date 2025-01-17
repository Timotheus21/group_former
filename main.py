import tkinter as tk
from tkinter.filedialog import askopenfilename
import sys
from dataprocessor import DataProcessor
from teamforming import TeamForming
from visualization import Visualization
from tooltip import Tooltip
from config import Config
from gui import GUI
from selector import select_file


def on_closing(root):
    print("Exiting...")
    root.quit()
    root.destroy()

if __name__ == "__main__":
    try:
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
    except Exception as e:
        print(f"Error initializing: {e}")
        sys.exit(1)