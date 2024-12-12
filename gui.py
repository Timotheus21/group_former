import tkinter as tk
import re
from tkinter import ttk
from pygame import mixer
from config import Config

class GUI:
    def __init__(self, root, data_processor, teamforming, visualization, tooltip):
        self.root = root
        self.root.configure(bg='#5d33bd')
        self.data_processor = data_processor
        self.teamforming = teamforming
        self.visualization = visualization
        self.tooltip = tooltip
        mixer.init()

        # Set the title of the main window
        self.root.title("Hackathon Group Former")

        # Initialize weight variables from data processor
        self.weight_vars = {attribute: tk.DoubleVar(value=weight) for attribute, weight in self.data_processor.get_weights().items()}
        self.weight_labels = {} # Store the labels for later updates

        # Configure grid weights for the root window
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create the GUI widgets
        self.create_widgets()

    def create_widgets(self):
        self.checkbox_vars = {} # Store the checkbox variables for later updates
        self.checkbuttons = {} # Store the checkbuttons for later updates

        # Add explanatory texts to the GUI
        self.create_top_frame()
        # Create a frame for the buttons on the left
        self.create_scrollable_area()

        # Create a frame for adjusting weights in the middle
        self.create_button_frame()

    def create_top_frame(self):
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Add a label for the overall program explanation
        program_explanation = ttk.Label(
            self.top_frame,
            text=("Welcome to the Hackathon Group Former! This program helps you form teams based on various attributes. "
                 "Adjust the weights of the skill attributes below. Higher weights indicate more importance. "
                 "Select whether the following attributes should be homogenous or heterogenous within teams by checking or unchecking the boxes."),
            background='#5d33bd',
            foreground='white',
            wraplength=800,
            font=('Helvetica', 12, "bold")
        )
        program_explanation.pack(fill="x")

    def create_scrollable_area(self):
        # Create a frame to hold the weights and checkboxes
        self.scrollable_frame = ttk.Frame(self.root, style='Custom.TFrame')
        self.scrollable_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.canvas = tk.Canvas(self.scrollable_frame, bg='#f0f0f0')
        scrollbar = ttk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.canvas.yview)
        self.weights_frame = ttk.Frame(self.canvas)

        # Create a window in the canvas to hold the weights frame
        self.canvas.create_window((0, 0), window=self.weights_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Bind the mousewheel to the canvas
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        # Add labels and buttons for each weight attribute
        for index, (attribute, weight) in enumerate(self.data_processor.weights.items()):
            display_attribute = self.format_attribute_for_display(attribute)

            label = ttk.Label(self.weights_frame, text=display_attribute)
            label.grid(row=index, column=0, padx=5, pady=5, sticky=tk.W)

            label_weight = ttk.Label(self.weights_frame, text=int(weight))
            label_weight.grid(row=index, column=1, sticky=tk.W)
            self.weight_labels[attribute] = label_weight # Store the label for later updates

            # Button to increase weight
            increase_button = ttk.Button(
                self.weights_frame,
                text="+",
                command=lambda a=attribute: self.adjust_weight(a, 1))
            increase_button.grid(row=index, column=2, padx=5, pady=5)
            self.tooltip(increase_button, "Increase the weight of this attribute.")

            # Button to decrease weight
            decrease_button = ttk.Button(
                self.weights_frame,
                text="-",
                command=lambda a=attribute: self.adjust_weight(a, -1))
            decrease_button.grid(row=index, column=3, padx=5, pady=5)
            self.tooltip(decrease_button, "Decrease the weight of this attribute.")

            self.create_checkbutton(index, attribute)

        start_row = len(self.data_processor.weights.items())

        for index, attribute in enumerate(self.data_processor.get_other_attributes()):
            row = start_row + index
            display_attribute = self.format_attribute_for_display(attribute)
            label = ttk.Label(self.weights_frame, text=display_attribute)
            label.grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)

            # Create BooleanVars for the homogenous and heterogenous attributes
            is_homogeneous = attribute in self.data_processor.get_homogenous_attributes()
            checkbox_var = tk.BooleanVar(value=is_homogeneous)

            self.checkbox_vars[attribute] = checkbox_var

            # Create Checkbuttons for the homogenous and heterogenous attributes
            checkbutton = ttk.Checkbutton(
                self.weights_frame,
                variable=checkbox_var,
                onvalue=True,
                offvalue=False,
                command=lambda a=attribute: self.handle_checkbox_toggle(a))
            checkbutton.grid(row=row, column=1, padx=5, pady=5, sticky=tk.W)
            self.tooltip(checkbutton, "Toggle between matching and differentiating this attribute.")

            self.checkbuttons[attribute] = checkbutton

        # Bind the canvas to the scrollbar
        self.weights_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Frame to hold team buttons on the right
        self.team_buttons_frame = ttk.Frame(self.root)
        self.team_buttons_frame.grid(row=1, column=4, padx=10, pady=10, sticky=tk.NW)

    def create_button_frame(self):
        self.bottom_frame = ttk.Frame(self.root)
        self.bottom_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

        self.bottom_frame.columnconfigure(0, weight=1)

        buttons_frame = ttk.Frame(self.bottom_frame)
        buttons_frame.grid(row=0, column=0)

        # Button to generate teams
        generate_button = ttk.Button(
            buttons_frame,
            text="Generate Teams",
            command=lambda: [self.generate_teams(), self.play_sound()])
        generate_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.tooltip(generate_button, "Generate teams based on the current weights.")

        # Button to save current weights
        save_weights_button = ttk.Button(
            buttons_frame,
            text="Save Current Weights",
            command=lambda: [self.data_processor.save_weights(), self.play_sound()])
        save_weights_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        self.tooltip(save_weights_button, "Save the current weights to a file.")

        # Button to load custom weights
        load_custom_weights_button = ttk.Button(
            buttons_frame, 
            text="Load Custom Weights", 
            command=lambda: [self.load_weights("custom"), self.play_sound()])
        load_custom_weights_button.grid(row=0, column=2, padx=10, pady=10, sticky=tk.W)
        self.tooltip(load_custom_weights_button, "Load custom weights from a file.")

        # Button to load standard weights
        load_std_weights_button = ttk.Button(
            buttons_frame, 
            text="Load Standard Weights", 
            command=lambda: [self.load_weights("standard"), self.play_sound()])
        load_std_weights_button.grid(row=0, column=3, padx=10, pady=10, sticky=tk.W)
        self.tooltip(load_std_weights_button, "Load standard weights from a file.")

        show_config_button = ttk.Button(
            buttons_frame,
            text="Show Current Configuration",
            command=lambda: Config(self.root, self.data_processor))
        show_config_button.grid(row=0, column=4, padx=10, pady=10, sticky=tk.W)
        self.tooltip(show_config_button, "Show the current configuration of the data processor.")

    def create_checkbutton(self, row, attribute):
        # Create BooleanVar for the Checkbutton
        self.checkbox_vars[attribute] = tk.BooleanVar(value=False)

        # Create and configure the Checkbutton
        checkbutton = ttk.Checkbutton(
            self.weights_frame,
            variable=self.checkbox_vars[attribute],
            onvalue=True,
            offvalue=False,
            command=lambda: self.handle_checkbox_toggle(attribute))
        checkbutton.grid(row=row, column=4, padx=5, pady=5)
        self.tooltip(checkbutton, "Toggle between matching and differentiating this attribute.")

        # Store Checkbutton for reference
        self.checkbuttons[attribute] = checkbutton

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def play_sound(self):
        try:
            mixer.music.load('assets/sound/selection.wav')
            mixer.music.play()
        except Exception as e:
            print(f"Error playing sound: {e}")

    def format_attribute_for_display(self, attribute):
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', attribute)

    def handle_checkbox_toggle(self, attribute):
        is_homogeneous = self.checkbox_vars[attribute].get()
        # Update the text of the checkbutton based on the state
        if is_homogeneous:
            self.data_processor.add_homogenous_attribute(attribute)
        else:
            self.data_processor.add_heterogenous_attribute(attribute)

    # Method to adjust weight
    def adjust_weight(self, attribute, delta=0):
        try:
            current_weight = self.weight_vars[attribute].get()
            new_weight = current_weight + delta
            if new_weight < 0:
                new_weight = 0
            self.weight_vars[attribute].set(new_weight)
            self.weight_labels[attribute].config(text=int(new_weight))
            self.data_processor.custom_weights[attribute] = new_weight
            self.update_current_weights()
        except Exception as e:
            print(f"Error adjusting weight for {attribute}: {e}")

    def load_weights(self, weight_type):
        try:
            if weight_type == 'standard':
                # Load standard weights from the DataProcessor
                self.data_processor.weights = self.data_processor.load_weights(self.data_processor.STD_WEIGHT_FILE)
                # Update the custom weights to match the standard weights
                self.data_processor.custom_weights = self.data_processor.weights.copy()
            elif weight_type == 'custom':
                # Load custom weights from the DataProcessor
                self.data_processor.custom_weights = self.data_processor.load_weights(self.data_processor.CUSTOM_WEIGHT_FILE)
        
            # Update the weight variables and labels in the GUI
            for attribute, weight in self.data_processor.custom_weights.items():
                self.weight_vars[attribute].set(weight)
                self.weight_labels[attribute].config(text=int(weight))
            self.update_current_weights()
        except Exception as e:
            print(f"Error loading {weight_type} weights: {e}")

    def update_current_weights(self):
        self.data_processor.current_weights = {attribute: var.get() for attribute, var in self.weight_vars.items()}
        print(f"Current weights: {self.data_processor.current_weights}")

    # Method to generate teams
    def generate_teams(self):
        try:
            for widget in self.team_buttons_frame.winfo_children():
                widget.destroy()

            self.teams = self.teamforming.generate_teams()
            self.teamforming.set_teams(self.teams)  # Set teams attribute
            self.teamforming.print_teams()  # Print teams with names
            for idx, (team, score) in enumerate(self.teams):
                button = ttk.Button(
                    self.team_buttons_frame,
                    text=f"Visualize Team {idx + 1}",
                    command=lambda t=team: self.visualize_teams(t))
                button.pack(fill="x", padx=5, pady=5)
        except Exception as e:
            print(f"Error generating teams: {e}")

    # Method to visualize teams
    def visualize_teams(self, team):
        try:
            self.visualization.visualize(team, self.data_processor.get_data())
        except Exception as e:
            print(f"Error visualizing teams: {e}")