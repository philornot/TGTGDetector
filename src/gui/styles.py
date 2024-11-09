from tkinter import ttk
import tkinter as tk


class TGTGStyles:
    """Style dla aplikacji TGTG Detector"""

    # Kolory
    COLORS = {
        'bg_dark': '#2b2b2b',
        'bg_light': '#3c3f41',
        'fg': '#ffffff',
        'accent': '#4CAF50',  # Zielony - nawiązanie do TGTG
        'error': '#ff5252',
        'warning': '#ffd740',
        'success': '#69f0ae'
    }

    # Czcionki
    FONTS = {
        'header': ('Helvetica', 12, 'bold'),
        'normal': ('Helvetica', 10),
        'small': ('Helvetica', 9)
    }

    # Wymiary
    PADDING = {
        'small': 5,
        'normal': 10,
        'large': 20
    }

    @classmethod
    def apply_dark_theme(cls, root: tk.Tk):
        """Aplikuje ciemny motyw do całej aplikacji"""
        style = ttk.Style()

        # Konfiguracja głównego okna
        root.configure(bg=cls.COLORS['bg_dark'])

        # Style dla TTK widgets
        style.configure('TFrame', background=cls.COLORS['bg_dark'])

        style.configure('TLabel',
                        background=cls.COLORS['bg_dark'],
                        foreground=cls.COLORS['fg'],
                        font=cls.FONTS['normal'],
                        padding=cls.PADDING['normal']
                        )

        style.configure('Header.TLabel',
                        font=cls.FONTS['header'],
                        foreground=cls.COLORS['accent']
                        )

        style.configure('TButton',
                        background=cls.COLORS['accent'],
                        foreground=cls.COLORS['fg'],
                        font=cls.FONTS['normal'],
                        padding=cls.PADDING['normal']
                        )

        style.map('TButton',
                  background=[('active', cls.COLORS['accent'])],
                  foreground=[('active', cls.COLORS['fg'])]
                  )

        style.configure('TEntry',
                        fieldbackground=cls.COLORS['bg_light'],
                        foreground=cls.COLORS['fg'],
                        padding=cls.PADDING['small']
                        )

        # Status style
        style.configure('Status.TLabel',
                        font=cls.FONTS['small'],
                        foreground=cls.COLORS['fg']
                        )

        style.configure('Success.TLabel',
                        foreground=cls.COLORS['success']
                        )

        style.configure('Error.TLabel',
                        foreground=cls.COLORS['error']
                        )

        style.configure('Warning.TLabel',
                        foreground=cls.COLORS['warning']
                        )

    @staticmethod
    def create_tooltip(widget, text):
        """Tworzy tooltip dla widgetu"""

        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

            label = ttk.Label(tooltip, text=text, background="#ffffe0", relief='solid')
            label.pack()

            def hide_tooltip():
                tooltip.destroy()

            widget.tooltip = tooltip
            widget.bind('<Leave>', lambda e: hide_tooltip())

        widget.bind('<Enter>', show_tooltip)