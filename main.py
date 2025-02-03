import tkinter as tk
from tkinterdnd2 import TkinterDnD
import sys
from src.dataprocessor import DataProcessor
from src.teamforming import TeamForming
from src.visualization import Visualization
from src.tooltip import Tooltip
from src.config import Config
from src.gui import GUI
from src.selector import select_file

def on_closing(root):
    root.quit()
    root.destroy()

if __name__ == "__main__":
    try:
        filepath = select_file()
        if not filepath:
            sys.exit()

        root = TkinterDnD.Tk()

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