import tkinter as tk
from tkinter import ttk
from typing import Callable

from ...utils import TGTGLogger


class LocationFrame:
    """Komponent formularza z ustawieniami lokalizacji"""

    def __init__(self, parent: ttk.Frame):
        self.logger = TGTGLogger("LocationFrame").get_logger()
        self.logger.debug("Inicjalizacja komponentu LocationFrame")

        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.X, pady=5)

        # Zmienne do przechowywania wartości
        self.lat_var = tk.StringVar()
        self.lng_var = tk.StringVar()
        self.radius_var = tk.StringVar()

        self._create_widgets()
        self.logger.debug("Komponent LocationFrame został zainicjalizowany")

    def _create_widgets(self):
        """Tworzy widgety dla komponentu lokalizacji"""
        self.logger.debug("Tworzenie widgetów LocationFrame")

        # Nagłówek sekcji
        ttk.Label(
            self.frame,
            text="Lokalizacja:",
            style='Normal.TLabel'
        ).pack(anchor=tk.W, pady=(10, 5))

        # Frame dla pól
        fields_frame = ttk.Frame(self.frame)
        fields_frame.pack(fill=tk.X)

        # Szerokość geograficzna
        ttk.Label(fields_frame, text="Szerokość:").pack(side=tk.LEFT)
        ttk.Entry(
            fields_frame,
            textvariable=self.lat_var,
            width=15
        ).pack(side=tk.LEFT, padx=5)

        # Długość geograficzna
        ttk.Label(fields_frame, text="Długość:").pack(side=tk.LEFT)
        ttk.Entry(
            fields_frame,
            textvariable=self.lng_var,
            width=15
        ).pack(side=tk.LEFT, padx=5)

        # Promień
        ttk.Label(fields_frame, text="Promień (km):").pack(side=tk.LEFT)
        ttk.Entry(
            fields_frame,
            textvariable=self.radius_var,
            width=5
        ).pack(side=tk.LEFT, padx=5)

        self.logger.debug("Widgety LocationFrame zostały utworzone")

    def set_values(self, lat: float, lng: float, radius: int):
        """Ustawia wartości pól lokalizacji"""
        self.logger.debug(f"Ustawianie wartości lokalizacji: lat={lat}, lng={lng}, radius={radius}")
        self.lat_var.set(str(lat))
        self.lng_var.set(str(lng))
        self.radius_var.set(str(radius))

    def get_values(self) -> tuple:
        """Zwraca wartości pól lokalizacji"""
        lat = float(self.lat_var.get())
        lng = float(self.lng_var.get())
        radius = int(self.radius_var.get())
        self.logger.debug(f"Pobrano wartości lokalizacji: lat={lat}, lng={lng}, radius={radius}")
        return lat, lng, radius


class RefreshIntervalFrame:
    """Komponent formularza z ustawieniem interwału odświeżania"""

    def __init__(self, parent: ttk.Frame):
        self.logger = TGTGLogger("RefreshIntervalFrame").get_logger()
        self.logger.debug("Inicjalizacja komponentu RefreshIntervalFrame")

        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.X, pady=5)

        self.interval_var = tk.StringVar()

        self._create_widgets()
        self.logger.debug("Komponent RefreshIntervalFrame został zainicjalizowany")

    def _create_widgets(self):
        """Tworzy widgety dla komponentu interwału"""
        self.logger.debug("Tworzenie widgetów RefreshIntervalFrame")

        ttk.Label(
            self.frame,
            text="Interwał odświeżania (sekundy):",
            style='Normal.TLabel'
        ).pack(anchor=tk.W)

        ttk.Entry(
            self.frame,
            textvariable=self.interval_var
        ).pack(fill=tk.X)

        self.logger.debug("Widgety RefreshIntervalFrame zostały utworzone")

    def set_value(self, interval: int):
        """Ustawia wartość interwału"""
        self.logger.debug(f"Ustawianie interwału: {interval}")
        self.interval_var.set(str(interval))

    def get_value(self) -> int:
        """Zwraca wartość interwału"""
        interval = int(self.interval_var.get())
        self.logger.debug(f"Pobrano wartość interwału: {interval}")
        return interval


class ButtonFrame:
    """Komponent z przyciskami akcji"""

    def __init__(self, parent: ttk.Frame):
        self.logger = TGTGLogger("SettingsButtonFrame").get_logger()
        self.logger.debug("Inicjalizacja komponentu ButtonFrame")

        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.X, pady=10)

        self._create_widgets()
        self.logger.debug("Komponent ButtonFrame został zainicjalizowany")

    def _create_widgets(self):
        """Tworzy przyciski"""
        self.logger.debug("Tworzenie przycisków")

        self.save_button = ttk.Button(self.frame, text="Zapisz")
        self.save_button.pack(side=tk.RIGHT)

        self.cancel_button = ttk.Button(self.frame, text="Anuluj")
        self.cancel_button.pack(side=tk.RIGHT, padx=5)

        self.logger.debug("Przyciski zostały utworzone")

    def bind_save_action(self, command: Callable):
        """Przypisuje akcję do przycisku zapisu"""
        self.logger.debug("Bindowanie akcji zapisu")
        self.save_button.configure(command=command)

    def bind_cancel_action(self, command: Callable):
        """Przypisuje akcję do przycisku anulowania"""
        self.logger.debug("Bindowanie akcji anulowania")
        self.cancel_button.configure(command=command)