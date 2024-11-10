import asyncio
import json
import ssl
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import ttk
from typing import Callable
from typing import Dict, Any, Optional, Tuple, List

import aiohttp

from src.utils import NiceLogger


class PackagesList:
    """Komponent wyświetlający listę dostępnych paczek"""

    def __init__(self, parent: ttk.Frame):
        self.logger = NiceLogger("PackagesList").get_logger()
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
        self.logger = NiceLogger("MapFrame").get_logger()
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
        self.logger = NiceLogger("OptionsFrame").get_logger()
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


class LocationAndFiltersFrame:
    """Komponent zarządzający lokalizacją i filtrami"""

    def __init__(self, parent: ttk.Frame):
        self.logger = NiceLogger("LocationComponent").get_logger()
        self.logger.info("=== Inicjalizacja komponentu lokalizacji ===")

        # Główny kontener na dwie kolumny
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Zapisz referencję do głównego okna
        self.root = self.frame.winfo_toplevel()

        # Inicjalizacja zmiennych
        self.street_var = tk.StringVar()
        self.city_var = tk.StringVar()
        self.radius_var = tk.StringVar(value="5")
        self.keywords_var = tk.StringVar()
        self.company_var = tk.StringVar(value="Wszystkie")

        # Status geokodowania
        self.current_coords = None

        self._create_location_panel()
        self._create_filters_panel()

        self.logger.debug("Komponenty zostały utworzone")

    def _create_location_panel(self):
        """Tworzy panel ustawień lokalizacji"""
        self.logger.debug("Tworzenie panelu lokalizacji...")

        # Panel lokalizacji
        location_frame = ttk.LabelFrame(self.frame, text="Lokalizacja", padding=10)
        location_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        # Ulica
        street_frame = ttk.Frame(location_frame)
        street_frame.pack(fill=tk.X, pady=2)
        ttk.Label(street_frame, text="Ulica i numer:", width=15).pack(side=tk.LEFT)
        ttk.Entry(street_frame, textvariable=self.street_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # Miasto
        city_frame = ttk.Frame(location_frame)
        city_frame.pack(fill=tk.X, pady=2)
        ttk.Label(city_frame, text="Miasto:", width=15).pack(side=tk.LEFT)
        ttk.Entry(city_frame, textvariable=self.city_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # Promień
        radius_frame = ttk.Frame(location_frame)
        radius_frame.pack(fill=tk.X, pady=2)
        ttk.Label(radius_frame, text="Promień:", width=15).pack(side=tk.LEFT)
        ttk.Entry(radius_frame, textvariable=self.radius_var, width=10).pack(side=tk.LEFT, padx=(5, 5))
        ttk.Label(radius_frame, text="km").pack(side=tk.LEFT)

        # Przycisk geokodowania
        self.geocode_button = ttk.Button(location_frame, text="Ustaw lokalizację", command=self._geocode_callback)
        self.geocode_button.pack(pady=(5, 0))

        # Status
        self.status_label = ttk.Label(location_frame, text="Status: Nie ustawiono lokalizacji", style='Status.TLabel')
        self.status_label.pack(pady=(5, 0))

    def _create_filters_panel(self):
        """Tworzy panel filtrów"""
        self.logger.debug("Tworzenie panelu filtrów...")

        # Panel filtrów
        filters_frame = ttk.LabelFrame(self.frame, text="Filtry", padding=10)
        filters_frame.pack(fill=tk.X, padx=5, pady=5)

        # Słowa kluczowe
        keywords_frame = ttk.Frame(filters_frame)
        keywords_frame.pack(fill=tk.X, pady=2)
        ttk.Label(keywords_frame, text="Zawiera słowa:", width=15).pack(side=tk.LEFT)
        ttk.Entry(keywords_frame, textvariable=self.keywords_var).pack(side=tk.LEFT, fill=tk.X, expand=True,
                                                                       padx=(5, 0))

        # Lista firm
        company_frame = ttk.Frame(filters_frame)
        company_frame.pack(fill=tk.X, pady=2)
        ttk.Label(company_frame, text="Od firmy:", width=15).pack(side=tk.LEFT)

        self.company_combobox = ttk.Combobox(
            company_frame,
            textvariable=self.company_var,
            state='readonly',
            values=['Wszystkie']
        )
        self.company_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.company_combobox.set('Wszystkie')

    def _geocode_callback(self):
        """Callback dla przycisku geokodowania"""
        self.logger.debug("Wywołano callback geokodowania")

        # Pobierz aktualną pętlę zdarzeń
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            # Utwórz i uruchom task geokodowania
            task = loop.create_task(self._geocode_address())

            # Dodaj callback do obsługi błędów
            def handle_task_result(future):
                try:
                    future.result()  # To wywoła wyjątek, jeśli wystąpił błąd
                except Exception as ex:
                    self.logger.error(f"Błąd w tasku geokodowania: {ex}", exc_info=True)

            task.add_done_callback(handle_task_result)

        except Exception as e:
            self.logger.error(f"Błąd podczas tworzenia tasku geokodowania: {e}", exc_info=True)
            self.status_label.config(text=f"Status: Błąd - {str(e)}")

    async def _geocode_address(self):
        """Geokoduje wprowadzony adres"""
        self.logger.debug("=== Rozpoczęcie geokodowania adresu ===")

        street = self.street_var.get().strip()
        city = self.city_var.get().strip()

        self.logger.debug(f"Pobrane dane: ulica='{street}', miasto='{city}'")

        if not (street and city):
            self.logger.warning("Brak kompletnego adresu")
            self.status_label.config(text="Status: Wprowadź kompletny adres")
            return

        try:
            self.geocode_button.configure(state='disabled')
            self.status_label.config(text="Status: Trwa geokodowanie...")

            address = f"{street}, {city}, Poland"
            self.logger.debug(f"Przygotowany adres do geokodowania: {address}")

            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED

            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                url = "https://nominatim.openstreetmap.org/search"
                params = {
                    'q': address,
                    'format': 'json',
                    'limit': 1,
                    'countrycodes': 'pl'
                }
                headers = {
                    'User-Agent': 'TGTG_Detector/1.0 (https://github.com/philornot/TGTGDetector)'
                }
                self.logger.debug(f"Wysyłanie zapytania do: {url}")

                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 429:
                        raise Exception("Przekroczono limit zapytań. Spróbuj ponownie za kilka minut.")

                    if response.status != 200:
                        error_msg = await response.text()
                        self.logger.error(f"Błąd serwera {response.status}: {error_msg}")
                        raise Exception(f"Błąd serwera: {response.status}")

                    data = await response.json()
                    self.logger.debug(f"Otrzymana odpowiedź: {data}")

                    if not data:
                        self.status_label.config(text="Status: Nie znaleziono lokalizacji")
                        return

                    try:
                        lat = float(data[0]['lat'])
                        lon = float(data[0]['lon'])
                        self.current_coords = (lat, lon)

                        self.logger.info(f"Znaleziono współrzędne: ({lat}, {lon})")
                        self.status_label.config(
                            text=f"Status: Lokalizacja ustawiona ({lat:.6f}, {lon:.6f})"
                        )

                        # Wywołaj event aktualizacji lokalizacji
                        self.root.event_generate('<<LocationUpdated>>')

                    except (KeyError, ValueError) as e:
                        self.logger.error(f"Błąd parsowania danych: {e}")
                        raise Exception("Nieprawidłowy format danych z serwera")

        except aiohttp.ClientError as e:
            self.status_label.config(text="Status: Błąd połączenia z serwisem geokodowania")
            self.logger.error(f"Błąd połączenia: {e}")
        except Exception as e:
            self.status_label.config(text=f"Status: Błąd - {str(e)}")
            self.logger.error(f"Błąd geokodowania: {e}")
        finally:
            self.geocode_button.configure(state='normal')

    def get_status(self) -> Optional[Tuple[float, float]]:
        """Zwraca aktualne współrzędne"""
        return self.current_coords

    def update_companies(self, companies: List[str]):
        """Aktualizuje listę firm"""
        self.logger.debug(f"Aktualizacja listy firm: {len(companies)} pozycji")
        sorted_companies = sorted(set(companies))
        self.company_combobox['values'] = ['Wszystkie'] + sorted_companies

    def get_filters(self) -> dict:
        """Zwraca aktualne filtry"""
        return {
            'keywords': self.keywords_var.get().strip(),
            'company': None if self.company_var.get() == 'Wszystkie' else self.company_var.get(),
            'radius': int(self.radius_var.get()),
            'coordinates': self.current_coords
        }


@dataclass
class Location:
    street: str = ""
    city: str = ""
    coordinates: Optional[Tuple[float, float]] = None
    radius: int = 5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "street": self.street,
            "city": self.city,
            "coordinates": self.coordinates,
            "radius": self.radius
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        coords_data = data.get('coordinates')
        coordinates = None
        if coords_data and isinstance(coords_data, (list, tuple)) and len(coords_data) == 2:
            try:
                coordinates = (float(coords_data[0]), float(coords_data[1]))
            except (ValueError, TypeError):
                coordinates = None

        return cls(
            street=str(data.get('street', "")),
            city=str(data.get('city', "")),
            coordinates=coordinates,
            radius=int(data.get('radius', 5))
        )


@dataclass
class Filters:
    keywords: str = ""
    company: Optional[str] = None
    companies_list: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "keywords": self.keywords,
            "company": self.company,
            "companies_list": self.companies_list or []
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Filters':
        return cls(
            keywords=str(data.get('keywords', "")),
            company=data.get('company'),
            companies_list=list(data.get('companies_list', []))
        )


class TGTGSettings:
    """Zarządzanie ustawieniami aplikacji"""

    DEFAULT_CONFIG = {
        "refresh_interval": 30,
        "location": {
            "street": "",
            "city": "",
            "coordinates": None,
            "radius": 5
        },
        "filters": {
            "keywords": "",
            "company": None,
            "companies_list": []
        },
        "email": "",
        "access_token": "",
        "refresh_token": "",
        "user_id": "",
        "cookie": "",
        "notification_methods": ["console"],
        "favorite_stores": [],
        "min_price": 0,
        "max_price": 1000,
        "auto_reserve": False,
        "blacklist": [],
        "quiet_hours": {
            "start": "23:00",
            "end": "07:00"
        }
    }

    def __init__(self):
        self.logger = NiceLogger("TGTGSettings").get_logger()
        self.logger.info("=== Inicjalizacja menedżera ustawień ===")

        # Użyj "Documents" zamiast "Dokumenty"
        self.config_dir = Path.home() / "Documents" / "TGTG Detector"
        self.config_path = self.config_dir / "config.json"

        self.logger.info(f"Ścieżka konfiguracji: {self.config_path}")

        # Utwórz katalog, jeśli nie istnieje
        if not self.config_dir.exists():
            self.logger.info(f"Tworzenie katalogu konfiguracji: {self.config_dir}")
            self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config = self.load_config()
        self.logger.debug(f"Załadowana konfiguracja: {self.config}")

    def load_config(self) -> Dict[str, Any]:
        """Wczytuje konfigurację z pliku"""
        self.logger.debug("=== Wczytywanie konfiguracji ===")

        if not self.config_path.exists():
            self.logger.info(f"Plik konfiguracji nie istnieje, tworzę domyślny: {self.config_path}")
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG

        try:
            self.logger.debug(f"Wczytywanie konfiguracji z: {self.config_path}")
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                merged_config = {**self.DEFAULT_CONFIG, **config}
                self.logger.debug(f"Załadowana konfiguracja: {merged_config}")
                return merged_config
        except Exception as e:
            self.logger.error(f"Błąd podczas wczytywania konfiguracji: {e}", exc_info=True)
            raise

    def save_config(self, config: Dict[str, Any]):
        """Zapisuje konfigurację do pliku"""
        self.logger.debug("=== Zapisywanie konfiguracji ===")

        try:
            self.logger.info(f"Zapisywanie konfiguracji do: {self.config_path}")
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.config = config
            self.logger.debug("Konfiguracja została pomyślnie zapisana")
            self.logger.debug(f"Zapisana konfiguracja: {config}")
        except Exception as e:
            self.logger.error(f"Błąd podczas zapisywania konfiguracji: {e}", exc_info=True)
            raise

    def get_location(self) -> Location:
        """Pobiera ustawienia lokalizacji"""
        self.logger.debug("Pobieranie ustawień lokalizacji")
        return Location.from_dict(self.config.get('location', {}))

    def get_filters(self) -> Filters:
        """Pobiera ustawienia filtrów"""
        self.logger.debug("Pobieranie ustawień filtrów")
        return Filters.from_dict(self.config.get('filters', {}))

    def update_location(self, location: Location):
        """Aktualizuje ustawienia lokalizacji"""
        self.logger.debug(f"Aktualizacja lokalizacji: {location}")
        self.config['location'] = location.to_dict()
        self.save_config(self.config)

    def update_filters(self, filters: Filters):
        """Aktualizuje ustawienia filtrów"""
        self.logger.debug(f"Aktualizacja filtrów: {filters}")
        self.config['filters'] = filters.to_dict()
        self.save_config(self.config)

    def update_credentials(self, credentials: Dict[str, str]):
        """Aktualizuje dane uwierzytelniające"""
        self.logger.info("=== Aktualizacja danych uwierzytelniających ===")
        self.logger.debug(f"Nowe credentials: {credentials}")

        self.config.update({
            "access_token": credentials.get("access_token", ""),
            "refresh_token": credentials.get("refresh_token", ""),
            "user_id": credentials.get("user_id", ""),
            "cookie": credentials.get("cookie", "")
        })
        self.save_config(self.config)
