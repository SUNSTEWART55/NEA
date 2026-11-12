"""
responsive.py
 
Small helper that rescales a view's fonts (and button sizes) as the
app window is resized so the UI doesn't feel locked to one window
size
"""
 
BASE_WIDTH = 460  # matches WINDOW_WIDTH in main.py
 
 
def make_responsive(frame, widgets, base_width=BASE_WIDTH, min_scale=0.8, max_scale=1.8):
    """
    Registers a <Configure> handler on the app's root window that
    rescales the given widgets whenever the window is resized.
 
    widgets: a list of (widget, base_font_size, base_width_px, base_height_px)
             tuples. For labels or widgets with no fixed size, pass
             None for base_width_px and base_height_px.
    """
    root = frame.winfo_toplevel()
 
    def on_resize(event):
        if event.widget is not root:
            return
 
        scale = event.width / base_width
        scale = max(min_scale, min(max_scale, scale))
 
        for widget, font_size, width, height in widgets:
            try:
                widget.configure(font=("Arial", max(10, int(font_size * scale))))
            except Exception:
                pass
            if width is not None and height is not None:
                try:
                    widget.configure(width=int(width * scale), height=int(height * scale))
                except Exception:
                    pass
 
    root.bind("<Configure>", on_resize, add="+")
