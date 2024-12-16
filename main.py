import tkinter as tk
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

if __name__ == "__main__":
    root = tk.Tk()

    data_processor = DataProcessor()
    teamforming = TeamForming(data_processor)
    visualization = Visualization(data_processor.get_data())
    tooltip = Tooltip
    config = Config

    # Set protocol for closing the window
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
    
    # Initialize and run the GUI
    gui = GUI(root, data_processor, teamforming, visualization, tooltip)
    root.mainloop()