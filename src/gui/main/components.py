import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Any, List

from src import TGTGLogger


class PackagesList:
    """Komponent wyświetlający listę dostępnych paczek"""

    def __init__(self, parent: ttk.Frame):
        self.logger = TGTGLogger("PackagesList").get_logger()
        self.logger.info("=== Inicjalizacja komponentu listy paczek ===")

        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self._create_widgets()
        self._bind_events()

        self.logger.info("=== Inicjalizacja listy paczek zakończona ===")

    def _create_widgets(self):
        """Tworzy widżety listy paczek"""
        self.logger.debug("Tworzenie widżetów listy paczek...")

        # Nagłówek
        ttk.Label(
            self.frame,
            text="Dostępne paczki:",
            style='Header.TLabel'
        ).pack(fill=tk.X)

        # Frame dla listy i scrollbara
        list_frame = ttk.Frame(self.frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Lista paczek
        self.logger.debug("Tworzenie Treeview dla paczek...")
        self.treeview = ttk.Treeview(
            list_frame,
            columns=('name', 'price', 'distance', 'pickup'),
            show='headings',
            selectmode='browse'
        )

        # Konfiguracja kolumn
        self.treeview.heading('name', text='Nazwa')
        self.treeview.heading('price', text='Cena')
        self.treeview.heading('distance', text='Odległość')
        self.treeview.heading('pickup', text='Odbiór')

        # Szerokości kolumn
        self.treeview.column('name', width=200)
        self.treeview.column('price', width=80)
        self.treeview.column('distance', width=80)
        self.treeview.column('pickup', width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=scrollbar.set)

        # Pakowanie
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.logger.debug("Widżety listy paczek zostały utworzone")

    def _bind_events(self):
        """Wiąże eventy dla listy"""
        self.logger.debug("Bindowanie eventów listy...")
        # Na razie puste — eventy będą bindowane z zewnątrz
        pass

    def bind_select(self, callback: Callable):
        """Binduje callback dla wyboru paczki"""
        self.logger.debug(f"Bindowanie callbacku wyboru paczki: {callback}")
        self.treeview.bind('<<TreeviewSelect>>', callback)

    def clear(self):
        """Czyści listę paczek"""
        self.logger.debug("Czyszczenie listy paczek...")
        for item in self.treeview.get_children():
            self.treeview.delete(item)

    def update_packages(self, packages: List[Dict[str, Any]]):
        """Aktualizuje listę paczek"""
        self.logger.debug(f"Aktualizacja listy paczek (liczba paczek: {len(packages)})")

        self.clear()
        for package in packages:
            store = package.get('store', {})
            price = package.get('item', {}).get('price_including_taxes', {})
            price_value = float(price.get('minor_units', 0)) / 100
            pickup = package.get('pickup_interval', {})

            values = (
                store.get('store_name', 'Nieznany sklep'),
                f"{price_value:.2f} PLN",
                f"{store.get('distance', 0):.1f} km",
                f"{pickup.get('start', '')} - {pickup.get('end', '')}"
            )

            self.logger.debug(f"Dodawanie paczki: {values[0]}, {values[1]}")
            self.treeview.insert('', 'end', iid=str(id(package)), values=values)


class MapFrame:
    """Komponent wyświetlający mapę z lokalizacją paczek"""

    def __init__(self, parent: ttk.Frame):
        self.logger = TGTGLogger("MapFrame").get_logger()
        self.logger.info("=== Inicjalizacja komponentu mapy ===")

        # Frame główny
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Label z tytułem
        ttk.Label(
            self.frame,
            text="Lokalizacja:",
            style='Header.TLabel'
        ).pack(fill=tk.X, pady=(0, 5))

        # Frame na mapę
        self.map_container = ttk.Frame(self.frame)
        self.map_container.pack(fill=tk.BOTH, expand=True)

        self._create_widgets()
        self.logger.info("=== Inicjalizacja mapy zakończona ===")

    def _create_widgets(self):
        """Tworzy widżet mapy"""
        self.logger.debug("Tworzenie widżetu mapy...")

        try:
            # Użyj ttk.Label zamiast tkinterweb do wyświetlania prostej mapy
            self.map_label = ttk.Label(
                self.map_container,
                text="Mapa zostanie zaimplementowana w przyszłej wersji",
                style='Normal.TLabel'
            )
            self.map_label.pack(fill=tk.BOTH, expand=True)

            # Dodaj informację o współrzędnych
            self.coords_label = ttk.Label(
                self.map_container,
                text="",
                style='Status.TLabel'
            )
            self.coords_label.pack(fill=tk.X)

            self.logger.debug("Widżet mapy został utworzony")

        except Exception as e:
            self.logger.error(f"Błąd podczas tworzenia widżetu mapy: {e}")
            raise

    def load_location(self, location: str):
        """Aktualizuje wyświetlane współrzędne"""
        self.logger.debug(f"Aktualizacja lokalizacji: {location}")
        self.coords_label.config(text=f"Współrzędne: {location}")


class OptionsFrame:
    """Komponent z opcjami aplikacji"""

    def __init__(self, parent: ttk.Frame, settings: dict):
        self.logger = TGTGLogger("OptionsFrame").get_logger()
        self.logger.info("=== Inicjalizacja komponentu opcji ===")

        self.frame = ttk.LabelFrame(parent, text="Opcje", padding=10)
        self.frame.pack(fill=tk.X, padx=10, pady=5)

        self.settings = settings
        self._create_widgets()

        self.logger.info("=== Inicjalizacja opcji zakończona ===")

    def _create_widgets(self):
        """Tworzy widżety opcji"""
        self.logger.debug("Tworzenie widżetów opcji...")

        # Frame dla pierwszego rzędu opcji
        row1 = ttk.Frame(self.frame)
        row1.pack(fill=tk.X, pady=5)

        # Zakres cenowy
        self.logger.debug("Tworzenie pól zakresu cenowego...")
        ttk.Label(row1, text="Cena od:").pack(side=tk.LEFT, padx=5)
        self.min_price_var = tk.StringVar(value=str(self.settings.get('min_price', 0)))
        ttk.Entry(row1, textvariable=self.min_price_var, width=8).pack(side=tk.LEFT, padx=5)

        ttk.Label(row1, text="do:").pack(side=tk.LEFT, padx=5)
        self.max_price_var = tk.StringVar(value=str(self.settings.get('max_price', 1000)))
        ttk.Entry(row1, textvariable=self.max_price_var, width=8).pack(side=tk.LEFT, padx=5)

        # Interwał odświeżania
        self.logger.debug("Tworzenie pola interwału...")
        ttk.Label(row1, text="Interwał (s):").pack(side=tk.LEFT, padx=(20, 5))
        self.interval_var = tk.StringVar(value=str(self.settings.get('refresh_interval', 30)))
        ttk.Entry(row1, textvariable=self.interval_var, width=8).pack(side=tk.LEFT, padx=5)

        # Przycisk zapisz
        self.save_button = ttk.Button(row1, text="Zapisz ustawienia")
        self.save_button.pack(side=tk.RIGHT, padx=5)

    def bind_save(self, callback: Callable):
        """Binduje callback dla przycisku zapisu"""
        self.logger.debug(f"Bindowanie callbacku zapisu ustawień: {callback}")
        self.save_button.configure(command=callback)

    def get_values(self) -> dict:
        """Zwraca wartości wszystkich opcji"""
        self.logger.debug("Pobieranie wartości opcji...")
        values = {
            'min_price': float(self.min_price_var.get()),
            'max_price': float(self.max_price_var.get()),
            'refresh_interval': int(self.interval_var.get()),
        }
        self.logger.debug(f"Pobrane wartości opcji: {values}")
        return values
