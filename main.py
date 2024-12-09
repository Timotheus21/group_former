from dataprocessor import DataProcessor
from teamforming import TeamForming
from visualization import Visualization
from tooltip import Tooltip
from gui import GUI
import tkinter as tk

def on_closing(root):
    print("Exiting...")
    root.quit()
    root.destroy()

if __name__ == "__main__":
    data_processor = DataProcessor()
    teamforming = TeamForming(data_processor)
    visualization = Visualization
    tooltip = Tooltip

    root = tk.Tk()

    # Set protocol for closing the window
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
    
    # Initialize and run the GUI
    gui = GUI(root, data_processor, teamforming, visualization, tooltip)
    root.mainloop()