import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

from ...utils import TGTGLogger


class EmailFrame:
    """Komponent formularza z polem email"""

    def __init__(self, parent: ttk.Frame):
        self.logger = TGTGLogger("EmailFrame").get_logger()
        self.logger.debug("Inicjalizacja komponentu EmailFrame")

        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.X, pady=5)

        self.email_var = tk.StringVar()
        self._create_widgets()

        self.logger.debug("Komponent EmailFrame został zainicjalizowany")

    def _create_widgets(self):
        """Tworzy widgety dla komponentu email"""
        self.logger.debug("Tworzenie widgetów EmailFrame")

        ttk.Label(
            self.frame,
            text="Email TGTG:",
            style='Normal.TLabel'
        ).pack(side=tk.LEFT)

        email_entry = ttk.Entry(self.frame, textvariable=self.email_var)
        email_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        self.logger.debug("Widgety EmailFrame zostały utworzone")

    def get_email(self) -> str:
        """Zwraca wprowadzony email"""
        return self.email_var.get().strip()


class CodeFrame:
    """Komponent formularza z polem do wprowadzenia kodu weryfikacyjnego"""

    def __init__(self, parent: ttk.Frame):
        self.logger = TGTGLogger("CodeFrame").get_logger()
        self.logger.debug("Inicjalizacja komponentu CodeFrame")

        self.frame = ttk.Frame(parent)
        self.code_var = tk.StringVar()
        self._create_widgets()

        # Na początku ukrywamy komponent
        self.hide()
        self.logger.debug("Komponent CodeFrame został zainicjalizowany")

    def _create_widgets(self):
        """Tworzy widgety dla komponentu kodu weryfikacyjnego"""
        self.logger.debug("Tworzenie widgetów CodeFrame")

        ttk.Label(
            self.frame,
            text="Kod weryfikacyjny:",
            style='Normal.TLabel'
        ).pack(side=tk.LEFT)

        self.code_entry = ttk.Entry(self.frame, textvariable=self.code_var)
        self.code_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        self.logger.debug("Widgety CodeFrame zostały utworzone")

    def show(self, after_widget: Optional[ttk.Widget] = None):
        """Pokazuje pole na kod weryfikacyjny"""
        self.logger.debug("Pokazywanie pola na kod weryfikacyjny")
        if after_widget:
            self.frame.pack(after=after_widget, fill=tk.X, pady=5)
        else:
            self.frame.pack(fill=tk.X, pady=5)
        self.code_entry.focus()

    def hide(self):
        """Ukrywa pole na kod weryfikacyjny"""
        self.logger.debug("Ukrywanie pola na kod weryfikacyjny")
        self.frame.pack_forget()

    def get_code(self) -> str:
        """Zwraca wprowadzony kod"""
        return self.code_var.get().strip()


class ButtonFrame:
    """Komponent z przyciskami akcji"""

    def __init__(self, parent: ttk.Frame):
        self.logger = TGTGLogger("ButtonFrame").get_logger()
        self.logger.debug("Inicjalizacja komponentu ButtonFrame")

        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.X, pady=20)

        self._create_widgets()
        self.logger.debug("Komponent ButtonFrame został zainicjalizowany")

    def _create_widgets(self):
        """Tworzy przyciski"""
        self.logger.debug("Tworzenie przycisków")

        self.auth_button = ttk.Button(
            self.frame,
            text="Wyślij kod weryfikacyjny"
        )
        self.auth_button.pack(side=tk.LEFT, padx=5)

        self.close_button = ttk.Button(
            self.frame,
            text="Zamknij"
        )
        self.close_button.pack(side=tk.RIGHT, padx=5)

        self.logger.debug("Przyciski zostały utworzone")

    def bind_auth_action(self, command: Callable):
        """Przypisuje akcję do przycisku autentykacji"""
        self.auth_button.configure(command=command)

    def bind_close_action(self, command: Callable):
        """Przypisuje akcję do przycisku zamknięcia"""
        self.close_button.configure(command=command)

    def set_auth_button_text(self, text: str):
        """Zmienia tekst na przycisku autentykacji"""
        self.logger.debug(f"Zmiana tekstu przycisku autentykacji na: {text}")
        self.auth_button.configure(text=text)