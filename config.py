import tkinter as tk
from tkinter import ttk
import re

class Config:
    def __init__(self, root, data_processor):
        self.root = root
        self.data_processor = data_processor
        self.create_config_window()

    def format_attribute_for_display(self, attribute):
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', attribute)
    
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def create_config_window(self):
        config_window = tk.Toplevel(self.root)
        config_window.title("Current Configuration")
        config_window.geometry("400x300")

        self.canvas = tk.Canvas(config_window)
        scrollbar = ttk.Scrollbar(config_window, orient="vertical", command=self.canvas.yview)
        scrollable_frame = ttk.Frame(self.canvas, style='Custom.TFrame', padding="3 3 12 12")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        homogenous_attributes = self.data_processor.get_homogenous_attributes()
        heterogenous_attributes = self.data_processor.get_heterogenous_attributes()
        normalized_weights = self.data_processor.get_normalized_current_weights()

        homogenous_label = ttk.Label(scrollable_frame, text="Homogenous Attributes:", foreground='#5d33bd')
        homogenous_label.pack(anchor='w', padx=10, pady=5)
        for attribute in homogenous_attributes:
            display_attribute = self.format_attribute_for_display(attribute)
            attribute_label = ttk.Label(scrollable_frame, text=display_attribute, foreground='#5d33bd')
            attribute_label.pack(anchor='w', padx=20)
        if not homogenous_attributes:
            empty_label = ttk.Label(scrollable_frame, text="No homogenous attributes found", foreground='#5d33bd')
            empty_label.pack(anchor='w', padx=20)

        heterogenous_label = ttk.Label(scrollable_frame, text="Heterogenous Attributes:", foreground='#5d33bd')
        heterogenous_label.pack(anchor='w', padx=10, pady=5)
        for attribute in heterogenous_attributes:
            display_attribute = self.format_attribute_for_display(attribute)
            attribute_label = ttk.Label(scrollable_frame, text=display_attribute, foreground='#5d33bd')
            attribute_label.pack(anchor='w', padx=20)
        if not heterogenous_attributes:
            empty_label = ttk.Label(scrollable_frame, text="No heterogenous attributes found", foreground='#5d33bd')
            empty_label.pack(anchor='w', padx=20)

        weights_label = ttk.Label(scrollable_frame, text="Normalized Weights:", foreground='#5d33bd')
        weights_label.pack(anchor='w', padx=10, pady=5)
        for attribute, weight in normalized_weights.items():
            display_attribute = self.format_attribute_for_display(attribute)
            weight_label = ttk.Label(scrollable_frame, text=f"{display_attribute}: {weight:.2f}", foreground='#5d33bd')
            weight_label.pack(anchor='w', padx=20)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
