import tkinter as tk

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.showing = False
        self.delay_id = None
        self.widget.bind("<Enter>", self.delay_show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)


    def delay_show_tooltip(self, event):
        self.showing = True
        self.delay_id = self.widget.after(1000, self.show_tooltip, event)

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
        label = tk.Label(tw, text=self.text, background="#d4c9ef", relief="solid", borderwidth=0.5, font=("Helvetica", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        self.showing = False
        if self.delay_id:
            self.widget.after_cancel(self.delay_id)
            self.delay_id = None
        # Destroy the tooltip window
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None