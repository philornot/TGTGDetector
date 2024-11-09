import sys
import tkinter as tk
from tkinter import ttk

import darkdetect
import sv_ttk

from ..utils import TGTGLogger


class TGTGStyles:
    """Style dla aplikacji TGTG Detector z wykorzystaniem Sun Valley theme"""

    logger = TGTGLogger("TGTGStyles").get_logger()

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
    def apply_theme(cls, root: tk.Tk):
        """Aplikuje Sun Valley theme w zależności od motywu systemowego"""
        try:
            cls.logger.debug("=== Rozpoczęcie aplikowania stylu ===")
            cls.logger.debug(f"Python version: {sys.version}")
            cls.logger.debug(f"Tkinter version: {tk.TkVersion}")

            # Wykryj motyw systemowy
            is_dark = darkdetect.isDark()
            cls.logger.debug(f"Wykryty motyw systemowy: {'ciemny' if is_dark else 'jasny'}")

            # Zastosuj Sun Valley theme
            theme = "dark" if is_dark else "light"
            cls.logger.debug(f"Ustawianie motywu Sun Valley: {theme}")
            sv_ttk.set_theme(theme)

            # Podstawowa konfiguracja okna
            cls.logger.debug("Konfiguracja podstawowych parametrów okna...")
            root.configure(padx=cls.PADDING['normal'], pady=cls.PADDING['normal'])

            # Dodatkowe style dla widgetów
            cls.logger.debug("Konfiguracja stylów dla widgetów...")
            style = ttk.Style()

            # Styl dla nagłówków
            cls.logger.debug("Konfiguracja stylu nagłówka...")
            style.configure(
                'Header.TLabel',
                font=cls.FONTS['header'],
                padding=cls.PADDING['normal']
            )

            # Styl dla zwykłego tekstu
            cls.logger.debug("Konfiguracja stylu normalnego tekstu...")
            style.configure(
                'Normal.TLabel',
                font=cls.FONTS['normal'],
                padding=cls.PADDING['small']
            )

            # Styl dla statusów
            cls.logger.debug("Konfiguracja stylu statusu...")
            style.configure(
                'Status.TLabel',
                font=cls.FONTS['small'],
                padding=cls.PADDING['small']
            )

            # Styl dla przycisków
            cls.logger.debug("Konfiguracja stylu przycisków...")
            style.configure(
                'TButton',
                padding=cls.PADDING['normal']
            )

            # Wymuszenie aktualizacji stylów
            cls.logger.debug("Wymuszenie aktualizacji stylów...")
            root.update()

            cls.logger.info("=== Style zostały pomyślnie zastosowane ===")

        except Exception as e:
            cls.logger.error(f"!!! Błąd podczas aplikowania stylów: {e}", exc_info=True)
            cls.logger.error(f"Typ błędu: {type(e).__name__}")
            raise
