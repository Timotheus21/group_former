import tkinter as tk
from tkinter import ttk
import re

"""
    The Config class is responsible for displaying the current configuration of the Group Former application.
    It creates a new window using the tkinter library to show the configuration details.

    Key Responsibilities:
    - Initialize the configuration window and configure its appearance.
    - Display the current configuration settings in a scrollable frame.
    - Handle user interactions such as scrolling and closing the window.
    - Format attribute names for display.
    - Ensure smooth scrolling experience by binding mouse wheel events.

    The class interacts with the DataProcessor to retrieve the current configuration settings and displays them in a user-friendly manner.
    It also ensures that the main GUI's scrolling functionality is restored when the configuration window is closed.
"""

class Config:
    def __init__(self, root, data_processor, root_canvas, font_settings):
        self.root = root
        self.data_processor = data_processor
        self.root_canvas = root_canvas
        self.font_settings = font_settings
        self.create_config_window()

    # Format attribute names for display by adding spaces between words
    def format_attribute_for_display(self, attribute):
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', attribute)
    
    # Handle mouse wheel scrolling in the configuration window
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    # Create the configuration window and display the current configuration settings from the DataProcessor
    def create_config_window(self):
        config_window = tk.Toplevel(self.root)
        config_window.title("Current Configuration")
        config_window.geometry("400x300")

        self.canvas = tk.Canvas(config_window)
        scrollbar = ttk.Scrollbar(config_window, orient = "vertical", command = self.canvas.yview)
        scrollable_frame = ttk.Frame(self.canvas, style = 'Custom.TFrame', padding = "3 3 12 12")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window = scrollable_frame, anchor = "nw")
        self.canvas.configure(yscrollcommand = scrollbar.set)

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        # Restore the main GUI's scrolling functionality when the configuration window is closed
        def on_close():
            self.canvas.unbind_all("<MouseWheel>")
            self.root_canvas.canvas.bind_all("<MouseWheel>", self.root_canvas.on_mousewheel)
            config_window.destroy()

        config_window.protocol("WM_DELETE_WINDOW", on_close)

        homogenous_attributes = sorted(self.data_processor.get_homogenous_attributes())
        heterogenous_attributes = sorted(self.data_processor.get_heterogenous_attributes())
        removed_attributes = sorted(self.data_processor.get_removed_attributes())
        normalized_weights = self.data_processor.get_normalized_current_weights()
        emphasized_attributes = sorted(self.data_processor.get_emphasized_attributes())

        font_settings = (self.font_settings, 11)
        main_color = '#6f12c0'

        # Display the current homogeneous attributes
        homogenous_label = ttk.Label(scrollable_frame, text = "Homogenous Attributes:", foreground = main_color, font = font_settings)
        homogenous_label.pack(anchor = 'w', padx = 10, pady = 5)

        for attribute in homogenous_attributes:
            display_attribute = self.format_attribute_for_display(attribute)
            attribute_label = ttk.Label(scrollable_frame, text = display_attribute, foreground = main_color, font = font_settings)
            attribute_label.pack(anchor = 'w', padx = 20)

        if not homogenous_attributes:
            empty_label = ttk.Label(scrollable_frame, text = "No homogenous attributes found", foreground = main_color, font = font_settings)
            empty_label.pack(anchor = 'w', padx = 20)

        # Display the current heterogenous attributes
        heterogenous_label = ttk.Label(scrollable_frame, text = "Heterogenous Attributes:", foreground = main_color, font = font_settings)
        heterogenous_label.pack(anchor = 'w', padx = 10, pady = 5)

        for attribute in heterogenous_attributes:
            display_attribute = self.format_attribute_for_display(attribute)
            attribute_label = ttk.Label(scrollable_frame, text = display_attribute, foreground = main_color, font = font_settings)
            attribute_label.pack(anchor = 'w', padx = 20)

        if not heterogenous_attributes:
            empty_label = ttk.Label(scrollable_frame, text = "No heterogenous attributes found", foreground=main_color, font=font_settings)
            empty_label.pack(anchor = 'w', padx = 20)

        # Display the current emphasized attributes
        emphasized_label = ttk.Label(scrollable_frame, text = "Emphasized Attributes:", foreground = main_color, font = font_settings)
        emphasized_label.pack(anchor = 'w', padx = 10, pady = 5)

        for attribute in emphasized_attributes:
            display_attribute = self.format_attribute_for_display(attribute)
            attribute_label = ttk.Label(scrollable_frame, text=display_attribute, foreground = main_color, font = font_settings)
            attribute_label.pack(anchor = 'w', padx = 20)

        if not emphasized_attributes:
            empty_label = ttk.Label(scrollable_frame, text = "No emphasized attributes found", foreground = main_color, font = font_settings)
            empty_label.pack(anchor = 'w', padx = 20)

        # Display the current removed attributes
        removed_label = ttk.Label(scrollable_frame, text = "Removed Attributes:", foreground = main_color, font = font_settings)
        removed_label.pack(anchor = 'w', padx = 10, pady = 5)

        for attribute in removed_attributes:
            display_attribute = self.format_attribute_for_display(attribute)
            attribute_label = ttk.Label(scrollable_frame, text = display_attribute, foreground = main_color, font = font_settings)
            attribute_label.pack(anchor = 'w', padx = 20)

        if not removed_attributes:
            empty_label = ttk.Label(scrollable_frame, text = "No removed attributes found", foreground = main_color, font = font_settings)
            empty_label.pack(anchor = 'w', padx = 20)

        # Display the current normalized weights
        weights_label = ttk.Label(scrollable_frame, text = "Normalized Weights:", foreground = main_color, font = font_settings)
        weights_label.pack(anchor = 'w', padx = 10, pady = 5)

        for attribute, weight in normalized_weights.items():
            display_attribute = self.format_attribute_for_display(attribute)
            weight_label = ttk.Label(scrollable_frame, text = f"{display_attribute}: {weight:.4f}", foreground = main_color, font=font_settings)
            weight_label.pack(anchor = 'w', padx = 20)

        self.canvas.pack(side = "left", fill = "both", expand = True)
        scrollbar.pack(side = "right", fill = "y")
