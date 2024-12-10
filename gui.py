import tkinter as tk
from tkinter import ttk
from pygame import mixer

class GUI:
    def __init__(self, root, data_processor, teamforming, visualization, tooltip):
        self.root = root
        self.root.configure(bg='#5d33bd')
        self.root.geometry("650x650")  # Set initial size with max width and specific height
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
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Create the GUI widgets
        self.create_widgets()

        self.resize_id = None  # Add a variable to store the resize event ID

    def create_widgets(self):
        # Configure styles for the widgets
        self.configure_styles()

        # Create a frame for the buttons on the left
        self.create_buttons_frame()

        # Create a frame for adjusting weights in the middle
        self.create_weights_frame()

        self.checkbox_vars = {} # Store the checkbox variables for later updates
        self.checkbuttons = {} # Store the checkbuttons for later updates

        # Add labels and buttons for each weight attribute
        for i, (attribute, weight) in enumerate(self.data_processor.weights.items()):
            label = ttk.Label(self.weights_frame, text=attribute)
            label.grid(row=i, column=0, sticky=tk.W)
    
            label_weight = ttk.Label(self.weights_frame, text=weight)
            label_weight.grid(row=i, column=1, sticky=tk.W)
            self.weight_labels[attribute] = label_weight # Store the label for later updates

            # Button to increase weight
            increase_button = ttk.Button(
                self.weights_frame,
                text="+",
                command=lambda a=attribute: self.adjust_weight(a, 1), style='TButton')
            increase_button.grid(row=i, column=2, padx=5, pady=5)
            self.tooltip(increase_button, "Increase the weight of this attribute.")

            # Button to decrease weight
            decrease_button = ttk.Button(
                self.weights_frame,
                text="-",
                command=lambda a=attribute: self.adjust_weight(a, -1), style='TButton')
            decrease_button.grid(row=i, column=3, padx=5, pady=5)
            self.tooltip(decrease_button, "Decrease the weight of this attribute.")

            self.checkbox_vars[attribute] = tk.BooleanVar(value=True) # Set the default state to True
            print(f"Direct state check for {attribute}: {self.checkbox_vars[attribute].get()}")

            match_differentiate_checkbutton = ttk.Checkbutton(
                self.weights_frame,
                variable=self.checkbox_vars[attribute],
                onvalue=True,
                offvalue=False,
                command=lambda a=attribute: self.handle_checkbox_toggle(a),
                style='TCheckbutton',
                text="Matched"
            )
            match_differentiate_checkbutton.grid(row=i, column=4, padx=5, pady=5)
            self.tooltip(match_differentiate_checkbutton, "Toggle between matching and differentiating this attribute.")

            self.checkbuttons[attribute] = match_differentiate_checkbutton

        # Frame to hold team buttons on the right
        self.team_buttons_frame = ttk.Frame(self.root)
        self.team_buttons_frame.grid(row=0, column=3, padx=10, pady=10, sticky=tk.NW)

    def configure_styles(self):
        style = ttk.Style()
        style.configure("TLabel", background='#5d33bd', foreground='white')  # Ensure text is visible
        style.configure("TButton", background='#7a5dc7', font=("Helvetica", 10, "bold"), padding=5)
        style.map("TButton", 
                  background=[('active', '#45a049'), ('!active', '#4CAF50')],
                  foreground=[('active', 'white'), ('!active', 'black')])

    def create_buttons_frame(self):
        self.buttons_frame = ttk.Frame(self.root)
        self.buttons_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NW)

        # Button to generate teams
        self.generate_button = ttk.Button(
            self.buttons_frame,
            text="Generate Teams",
            command=lambda: [self.generate_teams(), self.play_sound()])
        self.generate_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.tooltip(self.generate_button, "Generate teams based on the current weights.")

        # Button to save current weights
        self.save_weights_button = ttk.Button(
            self.buttons_frame,
            text="Save Current Weights",
            command=lambda: [self.data_processor.save_weights(), self.play_sound()])
        self.save_weights_button.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.tooltip(self.save_weights_button, "Save the current weights to a file.")

        # Button to load custom weights
        self.load_custom_weights_button = ttk.Button(
            self.buttons_frame, 
            text="Load Custom Weights", 
            command=lambda: [self.load_weights("custom"), self.play_sound()]
        )
        self.load_custom_weights_button.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.tooltip(self.load_custom_weights_button, "Load custom weights from a file.")

        # Button to load standard weights
        self.load_std_weights_button = ttk.Button(
            self.buttons_frame, 
            text="Load Standard Weights", 
            command=lambda: [self.load_weights("standard"), self.play_sound()]
        )
        self.load_std_weights_button.grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        self.tooltip(self.load_std_weights_button, "Load standard weights from a file.")

        self.show_configuration_button = ttk.Button(
            self.buttons_frame,
            text="Show Current Configuration",
            command=lambda: self.data_processor.show_configuration()
        )
        self.show_configuration_button.grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
        self.tooltip(self.show_configuration_button, "Show the current configuration of the data processor.")

    def create_weights_frame(self):
        self.weights_canvas = tk.Canvas(self.root, bg='#5d33bd', height=500)  # Set a fixed height for the canvas
        self.weights_frame = ttk.Frame(self.weights_canvas, style='TLabel')
        self.weights_frame.pack()
        self.weights_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.weights_canvas.yview)

        # Configure the scroll region of the canvas
        self.weights_frame.bind("<Configure>", self.on_weights_frame_configure)

        # Create a window in the canvas to hold the weights frame
        self.weights_canvas.create_window((0, 0), window=self.weights_frame, anchor="nw")
        self.weights_canvas.configure(yscrollcommand=self.weights_scrollbar.set)

        # Bind mouse wheel to scroll the canvas
        self.weights_canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        # Place the canvas and scrollbar in the grid
        self.weights_canvas.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.weights_scrollbar.grid(row=0, column=2, padx=(0, 10), pady=10, sticky="ns")

    def on_weights_frame_configure(self, event):
        self.weights_canvas.config(scrollregion=self.weights_canvas.bbox("all"))

    def on_resize(self, event):
        if self.resize_id is not None:
            self.root.after_cancel(self.resize_id)
        self.resize_id = self.root.after(100, self._resize_canvas, event)

    def _resize_canvas(self, event):
        max_width = 305  # Set a maximum width for the canvas
        canvas_width = min(event.width - 50, max_width)
        self.weights_canvas.config(width=canvas_width)
        self.root.update_idletasks()  # Ensure the window updates correctly

    def on_mouse_wheel(self, event):
        self.weights_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def play_sound(self):
        try:
            mixer.music.load('assets/sound/selection.wav')
            mixer.music.play()
        except Exception as e:
            print(f"Error playing sound: {e}")

    def handle_checkbox_toggle(self, attribute):
        is_homogeneous = self.checkbox_vars[attribute].get()
        print(f"Checkbox toggled for {attribute}: {is_homogeneous}")        
        # Update the text of the checkbutton based on the state
        if is_homogeneous:
            self.checkbuttons[attribute].config(text="Matched")
            print(f"Attribute {attribute} added to homogeneous list.")
            self.data_processor.add_homogenous_attribute(attribute)
        else:
            self.checkbuttons[attribute].config(text="Differentiate")
            print(f"Attribute {attribute} added to heterogeneous list.")
            self.data_processor.add_heterogenous_attribute(attribute)

    # Method to adjust weight
    def adjust_weight(self, attribute, delta=0):
        try:
            current_weight = self.weight_vars[attribute].get()
            new_weight = current_weight + delta
            if new_weight < 0:
                new_weight = 0
            self.weight_vars[attribute].set(new_weight)
            self.weight_labels[attribute].config(text=new_weight)
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
                self.weight_labels[attribute].config(text=weight)
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
                button.pack(padx=5, pady=5)
        except Exception as e:
            print(f"Error generating teams: {e}")

    # Method to visualize teams
    def visualize_teams(self, team):
        try:
            self.visualization.visualize(team, self.data_processor.get_data())
        except Exception as e:
            print(f"Error visualizing teams: {e}")