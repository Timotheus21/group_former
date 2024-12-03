from dataprocessor import DataProcessor
from teamforming import TeamFormation
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
    team_formation = TeamFormation(data_processor)
    visualization = Visualization
    tooltip = Tooltip

    root = tk.Tk()

    # Set protocol for closing the window
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
    
    # Initialize and run the GUI
    gui = GUI(root, data_processor, team_formation, visualization, tooltip)
    root.mainloop()