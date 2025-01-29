import tkinter as tk

"""
    The Tooltip class is responsible for creating and displaying tooltips for widgets in the Group Former application.
    It uses the tkinter library to create a small pop-up window that shows additional information when the user hovers
    over a widget.

    Key Responsibilities:
    - Initialize the tooltip with the target widget, text, and font settings.
    - Show the tooltip after a delay when the user hovers over the widget.
    - Hide the tooltip when the user moves the cursor away from the widget.
    - Calculate the position for the tooltip window based on the widget's position.
    - Create and configure the tooltip window and its label.

    The class ensures that the tooltip is displayed at the correct position and with the specified text and appearance.
    It handles the events for showing and hiding the tooltip, providing a smooth user experience.
"""

class Tooltip:
    def __init__(self, widget, text, font_settings):
        self.widget = widget
        self.text = text
        self.font_settings = font_settings

        self.tooltip_window = None
        self.showing = False
        self.delay_id = None

        # Bind mouse events to the widget for showing and hiding the tooltip
        self.widget.bind("<Enter>", self.delay_show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    # Delay showing the tooltip after 1 second
    def delay_show_tooltip(self, event):
        self.showing = True
        self.delay_id = self.widget.after(1000, self.show_tooltip, event)

    # Show the tooltip window with the specified text at the calculated position above the widget
    def show_tooltip(self, event):
        if not self.showing:
            return
        
        # Calculate position for the tooltip
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() - 10
        y += self.widget.winfo_rooty() - 20
        
        # Create tooltip window
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        # Create and pack the label in the tooltip window
        label = tk.Label(tw, text=self.text, background="#d4c9ef", relief="solid", borderwidth=0.5, font=(self.font_settings, 9, "normal"))
        label.pack(ipadx=1)

    # Hide the tooltip window when the user moves the cursor away from the widget and cancel the delay
    def hide_tooltip(self, event):
        self.showing = False
        if self.delay_id:
            self.widget.after_cancel(self.delay_id)
            self.delay_id = None

        # Destroy the tooltip window
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None