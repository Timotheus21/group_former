import tkinter as tk
import re
from tkinter import ttk, PhotoImage
from tkextrafont import Font
from PIL import Image, ImageTk
from config import Config
from teamforming import TeamForming
from visualization import Visualization
from selector import select_file

"""
    The GUI class is responsible for creating and managing the graphical user interface of the Group Former application.
    It uses the tkinter library to build the interface and provides various functionalities to interact with the user.

    Key Responsibilities:
    - Initialize the main window and configure its appearance.
    - Set up fonts, colors, and styles for the GUI elements.
    - Create and manage widgets such as labels, buttons, checkboxes, and entry fields.
    - Handle user interactions and update the GUI accordingly.
    - Load and display images.
    - Provide tooltips for various elements to guide the user.
    - Validate user inputs and provide feedback.
    - Manage the weights and attributes used for team formation.
    - Generate and visualize teams based on the current configuration.
    - Load and save weights from/to CSV files.
    - Load different surveys and update the GUI accordingly.

    The class is designed to be modular and extensible, allowing for easy addition of new features and customization.
    It interacts with other components such as the DataProcessor, TeamForming, and Visualization classes to perform its tasks.
"""

class GUI:
    def __init__(self, root, data_processor, teamforming, visualization, tooltip):
        self.root = root
        self.main_color = '#6f12c0'
        self.secondary_color = '#d4c9ef'
        self.scrollable_frame_color = '#f5f2fb'
        self.root.configure(bg=self.main_color)
        self.data_processor = data_processor
        self.teamforming = teamforming
        self.visualization = visualization
        self.tooltip = tooltip

        # Set the font for the GUI
        self.pixeltype = Font(file= "fonts/Pixeltype.ttf", family="Pixeltype", size=22)
        self.helvetica = Font(file= "fonts/Helvetica.ttf", family="Helvetica")

        # Set the maximum number of emphasized attributes
        self.max_emphasis = 4

        # Initialize the program explanation label
        self.program_explanation = None

        # Set the title of the main window
        self.root.title("Group Former")

        # Initialize weight variables from data processor
        self.weight_vars = {attribute: tk.DoubleVar(value=weight) for attribute, weight in self.data_processor.get_weights().items()}

        # Configure grid weights for the root window
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create the GUI widgets
        self.create_widgets()

    def create_widgets(self):
        self.checkbox_vars = {} # Store the checkbox variables for later updates
        self.checkbuttons = {} # Store the checkbuttons for later updates
        self.emphasis_buttons = {} # Store the emphasis buttons for later updates
        self.emphasis_attributes = {} # Store the emphasized attributes for later updates
        self.remove_checkbuttons = {} # Store the remove checkbuttons for later updates
        self.remove_checkbox_vars = {} # Store the remove checkbox variables for later updates
        self.attribute_labels = {} # Store the attribute labels for later updates
        self.increase_buttons = {} # Store the increase buttons for later updates
        self.decrease_buttons = {} # Store the decrease buttons for later updates
        self.weight_labels = {} # Store the labels for later updates
        self.feedback_labels = {} # Store the feedback labels for later updates

        # Define styles for the GUI
        self.define_styles()

        # Add explanatory texts to the GUI
        self.create_top_frame()

        # Create a scrollable area for the weights and checkboxes
        self.create_scrollable_area()

        # Create a frame for the team buttons
        self.create_button_frame()

    def define_styles(self):
        style = ttk.Style()
        style.configure('Emphasized.TButton',
                        foreground='red',
                        padding=(6, 6),
                        relief="raised",
                        anchor="center",
                        font=(self.helvetica, 10)
                        )
        style.configure('Toggle.TButton',
                        foreground='black',
                        background=self.main_color,
                        padding=(6, 6),
                        relief="raised",
                        anchor="center",
                        font=(self.helvetica, 10)
                        )
        style.configure('Diverse.TButton',
                        foreground=self.main_color,
                        padding=(6, 6),
                        relief="raised",
                        anchor="center",
                        font=(self.helvetica, 10)
                        )
        style.configure('Custom.TButton',
                        foreground='black',
                        padding=(6, 6),
                        relief="raised",
                        anchor="center",
                        font=(self.helvetica, 10)
                        )
        style.configure('Adjust.TButton',
                        foreground='black',
                        padding=(6, 6),
                        relief="raised",
                        anchor="center",
                        width=3,
                        font=(self.helvetica, 10)
                        )
        style.configure('Removed.TButton',
                        foreground='gray',
                        padding=(6, 6),
                        relief="raised",
                        anchor="center",
                        font=(self.helvetica, 10, 'overstrike')
                        )
        style.configure('Buttonframe.TButton',
                        foreground='black',
                        background=self.secondary_color,
                        padding=(6, 6),
                        relief="raised",
                        anchor="center",
                        font= self.pixeltype
                        )
        style.configure('Top.TFrame',
                        background=self.main_color,
                        )
        style.configure('Scrollable.TFrame',
                        background=self.scrollable_frame_color,
                        )
        style.configure('Button.TFrame',
                        background=self.secondary_color,
                        )

    def create_top_frame(self):
        # Create a frame to hold the top widgets
        self.top_frame = ttk.Frame(self.root, style='Top.TFrame')
        self.top_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

        # Configure grid weights for the top frame
        self.top_frame.grid_rowconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(0, weight=1)

        # Load the questionmark image, first integer is width, second is height
        self.questionmark = self.load_image("images/questionmark.png", 20, 25)

        self.toogle_button = tk.Button(
            self.root,
            image=self.questionmark,
            borderwidth=0,
            background=self.main_color,
            width=20,
            height=25,
            command= self.toogle_top_frame
        )
        self.toogle_button.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
        self.tooltip(self.toogle_button, "Toggle the program explanation.", self.helvetica)

    def create_scrollable_area(self):
        # Create a frame to hold the weights and checkboxes
        self.scrollable_frame = ttk.Frame(self.root, style='Scrollable.TFrame')
        self.scrollable_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Create a canvas to hold the weights and checkboxes
        self.canvas = tk.Canvas(self.scrollable_frame, bg=self.scrollable_frame_color)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Create a scrollbar for the canvas
        scrollbar = ttk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Create a parent frame inside the canvas to hold both weights_frame and teamsizing_frame
        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="n")

        self.weights_frame = ttk.LabelFrame(self.inner_frame, text="Adjust Weights and Attributes")
        self.weights_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Bind the canvas to the scrollbar
        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Add labels and buttons for each weight attribute
        for index, (attribute, weight) in enumerate(self.data_processor.weights.items()):
            display_attribute = self.format_attribute_for_display(attribute)

            label = ttk.Label(self.weights_frame, text=display_attribute, font=(self.helvetica, 11))
            label.grid(row=index, column=1, padx=5, pady=5, sticky=tk.W)
            self.attribute_labels[attribute] = label # Store the label for later updates

            label_weight = ttk.Label(self.weights_frame, text=int(weight), font=(self.helvetica, 11))
            label_weight.grid(row=index, column=2, padx=6, pady=6, sticky=tk.E)
            self.weight_labels[attribute] = label_weight # Store the label for later updates

            # Button to increase weight
            increase_button = ttk.Button(
                self.weights_frame,
                text="+",
                style='Adjust.TButton',
                command=lambda a=attribute: self.adjust_weight(a, 1))
            increase_button.grid(row=index, column=3, padx=5, pady=5)
            self.tooltip(increase_button, "Increase the weight of this attribute.", self.helvetica)

            self.increase_buttons[attribute] = increase_button

            # Button to decrease weight
            decrease_button = ttk.Button(
                self.weights_frame,
                text="-",
                style='Adjust.TButton',
                command=lambda a=attribute: self.adjust_weight(a, -1))
            decrease_button.grid(row=index, column=4, padx=5, pady=5)
            self.tooltip(decrease_button, "Decrease the weight of this attribute.", self.helvetica)

            self.decrease_buttons[attribute] = decrease_button

            self.create_checkbutton(index, attribute)

            self.create_emphasis_button(self.weights_frame, index, 6, attribute)

        start_row = len(self.data_processor.weights.items())

        # Add labels and buttons for other attributes
        for index, attribute in enumerate(self.data_processor.get_other_attributes()):
            row = start_row + index
            display_attribute = self.format_attribute_for_display(attribute)

            row_frame = ttk.Frame(self.weights_frame)
            row_frame.grid(row=row, column=3, columnspan=4, padx=5, pady=5, sticky=tk.W)

            label = ttk.Label(self.weights_frame, text=display_attribute, font=(self.helvetica, 11))
            label.grid(row=row, column=1, padx=5, pady=5, sticky=tk.W)

            self.attribute_labels[attribute] = label

            # Create BooleanVars for the homogenous and heterogenous attributes
            is_homogeneous = attribute in self.data_processor.get_homogenous_attributes()
            checkbox_var = tk.BooleanVar(value=is_homogeneous)

            self.checkbox_vars[attribute] = checkbox_var

            # Create Checkbuttons for the homogenous and heterogenous attributes
            self.checkbutton = ttk.Button(
                row_frame,
                style='Custom.TButton' if self.checkbox_vars[attribute].get() else 'Diverse.TButton',
                text="Matched" if self.checkbox_vars[attribute].get() else "Diverse",
                command=lambda a=attribute: self.handle_checkbox_toggle(a))
            self.checkbutton.grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
            self.tooltip(self.checkbutton, "Toggle between matching and differentiating this attribute.", self.helvetica)

            self.remove_checkbox_vars[attribute] = tk.BooleanVar(value=True)

            self.remove_checkbutton = ttk.Checkbutton(
                self.weights_frame,
                variable=self.remove_checkbox_vars[attribute],
                onvalue=True,
                offvalue=False,
                command=lambda a=attribute: self.handle_remove_toggle(a))
            self.remove_checkbutton.grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
            self.tooltip(self.remove_checkbutton, "Toggle between removing and adding this attribute.", self.helvetica)

            self.checkbuttons[attribute] = self.checkbutton
            self.remove_checkbuttons[attribute] = self.remove_checkbutton

            self.create_emphasis_button(row_frame, row, 1, attribute)

        # Create a frame for the team sizing
        self.teamsizing_frame = ttk.LabelFrame(self.inner_frame, text="Team Sizing")
        self.teamsizing_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        total_members = f"Total Members: {len(self.data_processor.get_data())}"

        self.member_descriptive_label = ttk.Label(self.teamsizing_frame, text=total_members, font=(self.helvetica, 11))
        self.member_descriptive_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)

        # Label for the team size
        team_size_label = ttk.Label(self.teamsizing_frame, text="Desired Team Size:", font=(self.helvetica, 11))
        team_size_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        # Entry for the desired team size
        self.team_size_var = tk.StringVar(value=4)
        self.team_size_var.trace_add("write", self.validate_entries)
        validate_team_size = (self.root.register(self.validate_size),'%P', '%d', '%W')
        self.team_size_entry = ttk.Entry(
            self.teamsizing_frame,
            textvariable=self.team_size_var,
            justify=tk.CENTER,
            font=(self.helvetica, 11),
            width=5,
            validate='key',
            validatecommand=validate_team_size)
        self.team_size_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.tooltip(self.team_size_entry, "The first teams will be generated with this size.", self.helvetica)

        # Label for the maximum number of team members
        max_teams_label = ttk.Label(self.teamsizing_frame, text="Maximum Team Size:", font=(self.helvetica, 11))
        max_teams_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        # Entry for the maximum number of team members
        self.max_team_size_var = tk.StringVar(value=5)
        self.max_team_size_var.trace_add("write", self.validate_entries)
        validate_max_team_size = (self.root.register(self.validate_size),'%P', '%d', '%W')
        self.max_teams_entry = ttk.Entry(
            self.teamsizing_frame,
            textvariable=self.max_team_size_var,
            justify=tk.CENTER,
            font=(self.helvetica, 11),
            width=5,
            validate='key',
            validatecommand=validate_max_team_size)
        self.max_teams_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.tooltip(self.max_teams_entry, "Teams will not exceed this size. Adding remaining members to teams below this size.\n"+
                     "If the desired team size is greater than this, the maximum team size will be adjusted.", self.helvetica)

        # Label for the minimum number of team members
        min_teams_label = ttk.Label(self.teamsizing_frame, text="Minimum Team Size:", font=(self.helvetica, 11))
        min_teams_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

        # Entry for the minimum number of team members
        self.min_team_size_var = tk.StringVar(value=3)
        self.min_team_size_var.trace_add("write", self.validate_entries)
        validate_min_team_size = (self.root.register(self.validate_size),'%P', '%d', '%W')
        self.min_teams_entry = ttk.Entry(
            self.teamsizing_frame,
            textvariable=self.min_team_size_var,
            justify=tk.CENTER,
            font=(self.helvetica, 11),
            width=5,
            validate='key',
            validatecommand=validate_min_team_size)
        self.min_teams_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.tooltip(self.min_teams_entry, "Teams will not be smaller than this size.\n"+
                     "If the desired team size is smaller than this, the minimum team size will be adjusted.", self.helvetica)
        
        # Label for the remaining members
        remaining_members = f"Remaining Members: "
        self.remaining_members_label = ttk.Label(self.teamsizing_frame, text=remaining_members, font=(self.helvetica, 11))
        self.remaining_members_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        # Frame to hold team buttons on the right
        self.team_buttons_frame = ttk.Frame(self.root, style='Top.TFrame')
        self.team_buttons_frame.grid(row=1, column=5, padx=10, pady=10, sticky=tk.NW)

    def create_button_frame(self):
        self.bottom_frame = ttk.Frame(self.root, style='Button.TFrame')
        self.bottom_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

        self.bottom_frame.columnconfigure(1, weight=1, minsize=110)
        self.bottom_frame.columnconfigure(2, weight=1, minsize=110)
        self.bottom_frame.columnconfigure(3, weight=1, minsize=110)
        self.bottom_frame.columnconfigure(4, weight=1, minsize=110)
        self.bottom_frame.columnconfigure(5, weight=1, minsize=110)

        # Load the images for the buttons, first integer is width, second is height
        self.start_button = self.load_image("images/generate.png", 110, 40)

        # Button to generate teams
        self.generate_button = tk.Button(
            self.bottom_frame,
            image=self.start_button,
            borderwidth=0,
            background=self.secondary_color,
            width=110,
            height=40,
            command=lambda: self.generate_teams()
            )
        self.generate_button.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
        self.tooltip(self.generate_button, "Generate teams based on the current configuration.", self.helvetica)

        # Button to save current weights
        save_weights_button = ttk.Button(
            self.bottom_frame,
            text="Save Weights",
            style='Buttonframe.TButton',
            command=lambda: self.data_processor.save_weights()
            )
        save_weights_button.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        self.tooltip(save_weights_button, "Save the current weights to a CSV file.", self.helvetica)

        # Button to load custom weights
        load_custom_weights_button = ttk.Button(
            self.bottom_frame,
            text="Load Custom Weights",
            style='Buttonframe.TButton',
            command=lambda: self.load_weights("custom")
            )
        load_custom_weights_button.grid(row=0, column=2, padx=10, pady=10, sticky='ew')
        self.tooltip(load_custom_weights_button, "Load custom weights from a CSV file.", self.helvetica)

        # Button to load standard weights
        load_std_weights_button = ttk.Button(
            self.bottom_frame,
            text="Load Standard Weights",
            style='Buttonframe.TButton',
            command=lambda: self.load_weights("standard")
            )
        load_std_weights_button.grid(row=0, column=3, padx=10, pady=10, sticky='ew')
        self.tooltip(load_std_weights_button, "Load standard weights from a CSV file.", self.helvetica)

        # Button to show the current configuration
        show_config_button = ttk.Button(
            self.bottom_frame,
            text="Settings",
            style='Buttonframe.TButton',
            command=lambda: Config(self.root, self.data_processor, self, self.helvetica)
            )
        show_config_button.grid(row=0, column=4, padx=10, pady=10, sticky='ew')
        self.tooltip(show_config_button, "Show the current configuration of the data processor.", self.helvetica)

        # Button to load a different survey
        load_survey_button = ttk.Button(
            self.bottom_frame,
            text="Load Survey",
            style='Buttonframe.TButton',
            command=lambda: self.load_different_survey()
            )
        load_survey_button.grid(row=0, column=5, padx=10, pady=10, sticky='ew')
        self.tooltip(load_survey_button, "Load a different survey to form teams.", self.helvetica)

    def create_checkbutton(self, row, attribute):
        # Create BooleanVar for the Checkbutton
        self.checkbox_vars[attribute] = tk.BooleanVar(value=True)

        # Create and configure the Checkbutton
        checkbutton = ttk.Button(
            self.weights_frame,
            style='Custom.TButton' if self.checkbox_vars[attribute].get() else 'Diverse.TButton',
            text="Matched" if self.checkbox_vars[attribute].get() else "Diverse",
            command=lambda: self.handle_checkbox_toggle(attribute))
        checkbutton.grid(row=row, column=5, padx=5, pady=5)
        self.tooltip(checkbutton, "Toggle between matching and differentiating this attribute.", self.helvetica)

        self.remove_checkbox_vars[attribute] = tk.BooleanVar(value=True)

        remove_checkbutton = ttk.Checkbutton(
            self.weights_frame,
            variable=self.remove_checkbox_vars[attribute],
            onvalue=True,
            offvalue=False,
            command=lambda a=attribute: self.handle_remove_toggle(a))
        remove_checkbutton.grid(row=row, column=0, padx=5, pady=5)
        self.tooltip(remove_checkbutton, "Toggle between removing and adding this attribute.", self.helvetica)

        # Store Checkbutton for reference
        self.checkbuttons[attribute] = checkbutton
        self.remove_checkbuttons[attribute] = remove_checkbutton

    # Method to create emphasis button
    def create_emphasis_button(self, frame, row, column, attribute):
        self.emphasis_button = ttk.Button(
            frame,
            text="Emphasize",
            style='Custom.TButton',
            command=lambda: self.handle_emphasis_toggle(attribute))
        self.emphasis_button.grid(row=row, column=column, padx=5, pady=5)
        self.tooltip(self.emphasis_button, "Emphasize this attribute in team formation.", self.helvetica)

        self.emphasis_buttons[attribute] = self.emphasis_button

    # Method to handle mousewheel scrolling
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    # Method to format attribute for display by inserting spaces before capital letters
    def format_attribute_for_display(self, attribute):
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', attribute)

    # Method to load an image and resize it
    def load_image(self, filepath, width, height):
        og_img = Image.open(filepath)
        resized_img = og_img.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(resized_img)

    # Method to show feedback when validating entries
    def show_feedback(self, widget, message, color):
        self.feedback_label = ttk.Label(self.teamsizing_frame, text=message, foreground=color, font=(self.helvetica, 10))
        self.feedback_label.grid(row=widget.grid_info()['row'], column=widget.grid_info()['column'] + 2, padx=5, pady=5, sticky=tk.W)
        self.feedback_labels[widget] = self.feedback_label

    # Method to validate entries by checking if they are positive integers and enabling the generate button
    def validate_entries(self, *args):
        try:
            min_size = int(self.min_team_size_var.get())
            max_size = int(self.max_team_size_var.get())
            desired_size = int(self.team_size_var.get())

            if not min_size or not max_size or not desired_size:
                self.generate_button.config(state=tk.DISABLED)
                return

            if min_size > 0 and max_size > 0 and desired_size > 0:
                self.generate_button.config(state=tk.NORMAL)
            else:
                self.generate_button.config(state=tk.DISABLED)

        except:
            self.generate_button.config(state=tk.DISABLED)

    # Method to validate the size entries by checking if they are positive integers
    def validate_size(self, size, action, entry_name):
        entry_widget = self.root.nametowidget(entry_name)
        if action == '1': # Insert
            if size.isdigit() and int(size) > 0 and not size.startswith("0"):
                if entry_widget in self.feedback_labels:
                    self.feedback_labels[entry_widget].grid_forget()
                    del self.feedback_labels[entry_widget]
                return True
            else:
                self.show_feedback(entry_widget, "Please enter a positive integer.", 'red')
                return False

        if entry_widget in self.feedback_labels:
            self.feedback_labels[entry_widget].grid_forget()
            del self.feedback_labels[entry_widget]

        return True

    def handle_checkbox_toggle(self, attribute):
        is_homogeneous = self.checkbox_vars[attribute].get()
        self.checkbox_vars[attribute].set(not is_homogeneous)

        # Update the text of the checkbutton based on the state
        if self.checkbox_vars[attribute].get():
            self.checkbuttons[attribute].config(text="Matched")
            self.checkbuttons[attribute].config(style='Custom.TButton')
            self.data_processor.add_homogenous_attribute(attribute)
        else:
            self.checkbuttons[attribute].config(text="Diverse")
            self.checkbuttons[attribute].config(style='Diverse.TButton')
            self.data_processor.add_heterogenous_attribute(attribute)

    def handle_emphasis_toggle(self, attribute):
        emphasized_attributes = self.data_processor.get_emphasized_attributes()
        if attribute not in emphasized_attributes:
            if len(emphasized_attributes) >= self.max_emphasis:

                # Remove the first emphasized attribute
                first_attribute = emphasized_attributes[0]
                self.data_processor.remove_emphasized_attribute(first_attribute)
                self.emphasis_buttons[first_attribute].config(style='Custom.TButton')
                self.emphasis_attributes[first_attribute] = False

            self.data_processor.add_emphasized_attribute(attribute)
            self.emphasis_buttons[attribute].config(style='Emphasized.TButton')
            self.emphasis_attributes[attribute] = True
        else:
            self.data_processor.remove_emphasized_attribute(attribute)
            self.emphasis_buttons[attribute].config(style='Custom.TButton')
            self.emphasis_attributes[attribute] = False

    def handle_remove_toggle(self, attribute):
            if not self.remove_checkbox_vars[attribute].get():
                self.data_processor.remove_attribute(attribute)

                # Apply strike-through to the label
                self.attribute_labels[attribute].config(foreground='gray', font=(self.helvetica, 11,'overstrike'))
                self.checkbuttons[attribute].config(style='Removed.TButton')
                self.emphasis_buttons[attribute].config(style='Removed.TButton')

                if attribute in self.weight_labels:
                    self.weight_labels[attribute].config(foreground='gray', font=(self.helvetica, 11,'overstrike'))
                self.set_attribute_button_state(attribute, state=tk.DISABLED)
            else:
                if self.checkbox_vars[attribute].get():
                    self.data_processor.add_homogenous_attribute(attribute)
                else:
                    self.data_processor.add_heterogenous_attribute(attribute)

                # Remove strike-through from the label
                self.attribute_labels[attribute].config(foreground='black', font=(self.helvetica, 11))
                if attribute in self.weight_labels:
                    self.weight_labels[attribute].config(foreground='black', font=(self.helvetica, 11))
                self.set_attribute_button_state(attribute, state=tk.NORMAL)
                if self.checkbox_vars[attribute].get():
                    self.checkbuttons[attribute].config(style='Custom.TButton')
                else:
                    self.checkbuttons[attribute].config(style='Diverse.TButton')
                if attribute in self.emphasis_buttons:
                    if attribute not in self.emphasis_attributes:
                        self.emphasis_buttons[attribute].config(style='Custom.TButton')
                        self.emphasis_attributes[attribute] = False
                    if self.emphasis_attributes[attribute]:
                        self.emphasis_buttons[attribute].config(style='Emphasized.TButton')
                        self.data_processor.add_emphasized_attribute(attribute)
                    else:
                        self.emphasis_buttons[attribute].config(style='Custom.TButton')
                        self.data_processor.remove_emphasized_attribute(attribute)

    # Method to set the state of the attribute buttons based on the state
    def set_attribute_button_state(self, attribute, state):
        self.checkbuttons[attribute].config(state=state)
        self.emphasis_buttons[attribute].config(state=state)
        if attribute in self.increase_buttons:
            self.increase_buttons[attribute].config(state=state)
        if attribute in self.decrease_buttons:
            self.decrease_buttons[attribute].config(state=state)

    # Method to toogle the program explanation
    def toogle_top_frame(self):
        if self.program_explanation and self.program_explanation.winfo_ismapped():
            self.program_explanation.config(text="")
            self.program_explanation = None
        elif not self.program_explanation:
            # Add a label for the overall program explanation
            self.program_explanation = ttk.Label(
                self.top_frame,
                text=(f"Welcome to the Group Former! This program helps you form teams based on various attributes.\n"
                    f"Adjust the weights of the skill attributes below. Higher weights indicate more importance. "
                    f"Select whether the following attributes should be homogenous or heterogenous within teams. "
                    f"You can remove attributes by unchecking the remove box. Or you can emphasize up to {self.max_emphasis} of them, all with the corresponding buttons.\n"
                    f"You can also adjust the desired teamsizes. Click 'Generate Teams' to create teams based on the current configuration."),
                background=self.main_color,
                foreground='white',
                wraplength=900,
                font=(self.helvetica, 12, "bold")
                )
            self.program_explanation.grid(row=0, column=0)

    # Method to adjust weight of an skill attribute
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

    # Method to update the current weights in the DataProcessor based on the GUI
    def update_current_weights(self):
        self.data_processor.current_weights = {attribute: var.get() for attribute, var in self.weight_vars.items()}

    # Method to update the remaining members label in the GUI based on the number of remaining members in the TeamForming
    def update_remaining_members_label(self, remaining_members):
        self.remaining_members_label.config(text=f"Remaining Members: {remaining_members}")

    # Method to load a different survey and update the GUI
    def load_different_survey(self):
        try:
            filepath = select_file()
            if filepath:
                self.data_processor.reload_survey(filepath)
                self.teamforming = TeamForming(self.data_processor)
                self.visualization = Visualization(self.data_processor)
                self.update_gui()
        except Exception as e:
            print(f"Error loading different survey: {e}")

    # Method to update the GUI by removing and recreating the widgets
    def update_gui(self):
        for widget in self.team_buttons_frame.winfo_children():
                widget.destroy()
        self.create_widgets()

    # Method to generate teams
    def generate_teams(self):
        try:
            for label in self.feedback_labels.values():
                label.grid_forget()
                del label
            self.feedback_labels.clear()

            feedback_shown = False

            # Clear the team buttons frame
            for widget in self.team_buttons_frame.winfo_children():
                widget.destroy()

            # Get the desired team size, minimum team size, and maximum team size
            min_size = int(self.min_team_size_var.get())
            max_size = int(self.max_team_size_var.get())
            desired_size = int(self.team_size_var.get())

            # Check if the team sizes are as expected and adjust if necessary
            total_members = len(self.data_processor.get_data())
            if desired_size > total_members:
                desired_size = total_members
                self.team_size_var.set(desired_size)
                self.show_feedback(self.team_size_entry, "Value decreased to accommodate total number of members.", self.main_color)
                feedback_shown = True

            if max_size < desired_size:
                max_size = desired_size + 1
                self.max_team_size_var.set(max_size)
                self.show_feedback(self.max_teams_entry, "Value increased to accommodate desired team size.", self.main_color)
                feedback_shown = True

            if min_size > desired_size:
                min_size = desired_size - 1
                if min_size <= 1:
                    min_size = desired_size
                self.min_team_size_var.set(min_size)
                self.show_feedback(self.min_teams_entry, "Value decreased to accommodate desired team size.", self.main_color)
                feedback_shown = True

            if not feedback_shown:
                # Remove feedback label if no feedback is shown
                if hasattr(self, 'feedback_label'):
                    for label in self.feedback_labels.values():
                        label.grid_forget()
                        del label
                    self.feedback_labels.clear()

            # Generate teams based on the desired team size, minimum team size, and maximum team size
            self.teams, remaining_members = self.teamforming.generate_teams(desired_size, min_size, max_size)
            self.teamforming.set_teams(self.teams)  # Set teams attribute
            self.update_remaining_members_label(len(remaining_members))

            # Create buttons to visualize the teams
            for idx, team in enumerate(self.teams):
                button = ttk.Button(
                    self.team_buttons_frame,
                    style='Toggle.TButton',
                    text=f"Visualize Team {idx + 1}",
                    command=lambda t=team: self.visualize_teams(t)
                    )
                button.pack(fill="x", padx=5, pady=5)
        except Exception as e:
            print(f"Error generating teams: {e}")

    # Method to visualize teams in the Visualization class
    def visualize_teams(self, team):
        try:
            self.visualization.visualize([team])
        except Exception as e:
            print(f"Error visualizing teams: {e}")