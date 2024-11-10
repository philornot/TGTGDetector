import asyncio
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any

from plyer import notification

from .components import PackagesList, OptionsFrame, LocationAndFiltersFrame
from ... import TGTGLogger, TGTGSettings, TGTGApiClient


class MainWindow:
    """Główne okno aplikacji TGTG Monitor"""

    def __init__(self, root: Optional[tk.Tk] = None, api_client: Optional[TGTGApiClient] = None):
        self.logger = TGTGLogger("MainWindow").get_logger()
        self.logger.info("=== Rozpoczęcie inicjalizacji głównego okna ===")
        self.logger.debug(f"Otrzymane parametry: root={root}, api_client={api_client}")

        try:
            # Inicjalizacja komponentów backendowych
            self.logger.debug("Inicjalizacja komponentów backendowych...")
            self.settings = TGTGSettings()
            self.logger.debug(f"Ustawienia załadowane: {self.settings.config_path}")

            self.api_client = api_client
            self.logger.debug(f"Status API client: {'załadowany' if api_client else 'brak'}")

            # Stan aplikacji
            self.logger.debug("Inicjalizacja stanu aplikacji...")
            self.packages = []
            self.last_check_time = None
            self.is_running = True
            self.selected_package = None

            # Inicjalizacja event loop i kolejki async
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.async_queue = asyncio.Queue()

            self.logger.debug(f"Stan aplikacji zainicjalizowany: is_running={self.is_running}")

            # GUI
            self.logger.debug("=== Rozpoczęcie konfiguracji GUI ===")
            self.root = root
            self._configure_window()
            self._initialize_ui()

            # Uruchom monitoring
            self.logger.debug("Uruchamianie monitoringu w tle...")
            self._schedule_package_check()
            self.logger.debug("Task monitoringu utworzony")

            self.logger.info("=== Inicjalizacja głównego okna zakończona ===")

        except Exception as e:
            self.logger.critical(f"!!! Krytyczny błąd podczas inicjalizacji okna: {e}", exc_info=True)
            raise

    def _configure_window(self):
        """Konfiguracja podstawowych parametrów okna"""
        self.logger.debug("=== Rozpoczęcie konfiguracji parametrów okna ===")

        try:
            # Podstawowa konfiguracja
            self.root.title("TGTG Monitor")
            self.root.geometry("1600x900")
            self.root.minsize(1200, 800)
            self.logger.debug("Ustawiono podstawowe parametry okna")

            # Grid configuration
            self.logger.debug("Konfiguracja układu grid...")
            self.root.grid_columnconfigure(1, weight=3)  # Kolumna z listą
            self.root.grid_rowconfigure(0, weight=1)  # Wiersz z lokalizacją i listą
            self.logger.debug("Skonfigurowano układ grid")

            # Protokół zamknięcia
            self.logger.debug("Konfiguracja protokołu zamknięcia...")
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            self.logger.debug("Protokół zamknięcia skonfigurowany")

            # Wycentruj okno
            self._center_window()

            self.logger.debug("=== Konfiguracja okna zakończona ===")

        except Exception as e:
            self.logger.error(f"Błąd podczas konfiguracji okna: {e}", exc_info=True)
            raise

    def _initialize_ui(self):
        """Inicjalizacja interfejsu użytkownika"""
        self.logger.debug("=== Inicjalizacja komponentów UI ===")

        try:
            # Lewa strona — lokalizacja i filtry
            self.logger.debug("Inicjalizacja komponentu lokalizacji i filtrów...")
            left_container = ttk.Frame(self.root)
            left_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            self.location_filters = LocationAndFiltersFrame(left_container, self)
            self.logger.debug("Komponent lokalizacji i filtrów zainicjalizowany")

            # Prawa strona — lista paczek
            self.logger.debug("Inicjalizacja komponentu listy paczek...")
            packages_container = ttk.Frame(self.root)
            packages_container.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
            self.packages_list = PackagesList(packages_container)
            self.logger.debug("Komponent listy paczek zainicjalizowany")

            # Dolny panel — opcje
            self.logger.debug("Inicjalizacja komponentu opcji...")
            options_container = ttk.Frame(self.root)
            options_container.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
            self.options_frame = OptionsFrame(
                options_container,
                settings=self.settings.config
            )
            self.logger.debug("Komponent opcji zainicjalizowany")

            # Bindowanie akcji
            self.logger.debug("Bindowanie akcji komponentów...")
            self.packages_list.bind_select(self._on_package_select)
            self.options_frame.bind_save(self._save_settings)
            self.root.bind('<<LocationUpdated>>', self._on_location_updated)
            self.logger.debug("Akcje zostały zbindowane")

            self.logger.debug("=== Inicjalizacja UI zakończona pomyślnie ===")

        except Exception as e:
            self.logger.error(f"Błąd podczas inicjalizacji UI: {e}", exc_info=True)
            raise

    def _center_window(self):
        """Centruje okno na ekranie"""
        self.logger.debug("=== Rozpoczęcie centrowania okna ===")

        try:
            # Wymuszenie przetworzenia oczekujących zdarzeń
            self.root.update_idletasks()

            # Pobierz wymiary
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()

            # Oblicz pozycję
            x = (screen_width // 2) - (window_width // 2)
            y = (screen_height // 2) - (window_height // 2)

            # Ustaw pozycję
            self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')

        except Exception as e:
            self.logger.error(f"Błąd podczas centrowania okna: {e}", exc_info=True)
            raise

    def _process_async_queue(self):
        """Przetwarza zadania asynchroniczne w kolejce"""
        try:
            while True:
                try:
                    coro = self.async_queue.get_nowait()
                    future = asyncio.run_coroutine_threadsafe(coro, self.loop)
                    future.add_done_callback(self._handle_async_result)
                except asyncio.QueueEmpty:
                    break
                except Exception as e:
                    self.logger.error(f"Błąd przetwarzania kolejki async: {e}")

            if self.is_running:
                self.root.after(100, self._process_async_queue)

        except Exception as e:
            self.logger.error(f"Błąd w _process_async_queue: {e}")
            if self.is_running:
                self.root.after(100, self._process_async_queue)

    def _handle_async_result(self, future):
        """Obsługuje wyniki zadań asynchronicznych"""
        try:
            result = future.result()
            if result is not None:
                self.logger.debug(f"Zadanie asynchroniczne zakończone z wynikiem: {result}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Błąd w zadaniu asynchronicznym: {e}")

    def _schedule_package_check(self):
        """Planuje sprawdzanie paczek"""
        if self.is_running:
            self.async_queue.put_nowait(self._check_packages())
            interval = self.options_frame.get_values().get('refresh_interval', 30)
            self.root.after(interval * 1000, self._schedule_package_check)

    def _on_location_updated(self, _):
        """Obsługa zmiany lokalizacji"""
        self.logger.info("Lokalizacja została zaktualizowana, odświeżam listę paczek...")
        self.async_queue.put_nowait(self._check_packages())

    def _on_package_select(self, _):
        """Obsługa wyboru paczki z listy"""
        self.logger.debug("=== Obsługa wyboru paczki ===")

        try:
            selection = self.packages_list.treeview.selection()
            if selection:
                item_id = selection[0]
                self.selected_package = next(
                    (p for p in self.packages if str(id(p)) == item_id),
                    None
                )
        except Exception as e:
            self.logger.error(f"Błąd podczas obsługi wyboru paczki: {e}")

    def _save_settings(self):
        """Zapisuje ustawienia"""
        self.logger.info("=== Rozpoczęcie zapisywania ustawień ===")

        try:
            # Pobierz wartości z obu komponentów
            options_values = self.options_frame.get_values()
            filter_values = self.location_filters.get_filters()

            # Połącz wartości
            values = {**options_values, **filter_values}

            # Aktualizuj konfigurację
            self.settings.config.update(values)

            # Zapisz do pliku
            self.settings.save_config(self.settings.config)

            messagebox.showinfo("Sukces", "Ustawienia zostały zapisane")
            self.logger.info("Ustawienia zostały pomyślnie zapisane")

        except ValueError as e:
            self.logger.error(f"Błąd walidacji wartości: {e}")
            messagebox.showerror("Błąd", f"Nieprawidłowe wartości: {str(e)}")
        except Exception as e:
            self.logger.error(f"Błąd podczas zapisywania ustawień: {e}")
            messagebox.showerror("Błąd", f"Wystąpił błąd: {str(e)}")

    def _send_notification(self, package: Dict[str, Any]):
        """Wysyła powiadomienie o nowej paczce"""
        try:
            store = package.get('store', {})
            price = package.get('item', {}).get('price_including_taxes', {})
            price_value = float(price.get('minor_units', 0)) / 100

            store_name = store.get('store_name', 'Nieznany sklep')
            self.logger.debug(f"Przygotowanie powiadomienia dla: {store_name}")

            notification.notify(
                title='Nowa paczka TGTG!',
                message=f"{store_name}\nCena: {price_value:.2f} PLN",
                app_name='TGTG Monitor',
                timeout=10
            )

        except Exception as e:
            self.logger.error(f"Błąd podczas wysyłania powiadomienia: {e}")

    async def _check_packages(self):
        """Sprawdza dostępne paczki"""
        self.logger.debug("=== Rozpoczęcie sprawdzania paczek ===")

        try:
            # Sprawdź, czy mamy lokalizację
            filters = self.location_filters.get_filters()
            if not filters['coordinates']:
                self.logger.warning("Brak ustawionej lokalizacji!")
                return

            lat, lon = filters['coordinates']
            radius = filters['radius']

            # Pobierz paczki
            items = await self.api_client.get_items(
                lat=lat,
                lng=lon,
                radius=radius
            )

            # Aktualizuj listę firm
            companies = {item['store']['store_name'] for item in items}
            self.location_filters.update_companies(list(companies))

            # Zastosuj filtry
            filtered_items = self._apply_filters(items, filters)

            # Sprawdź nowe paczki
            if self.packages:  # Jeśli nie jest to pierwsze sprawdzenie
                self._check_new_packages(filtered_items)

            # Aktualizuj listę i GUI
            self.packages = filtered_items
            self.packages_list.update_packages(filtered_items)

            # Aktualizuj czas ostatniego sprawdzenia
            self.last_check_time = datetime.now()

        except Exception as e:
            self.logger.error(f"Błąd podczas sprawdzania paczek: {e}")

    def _apply_filters(self, items: list, filters: dict) -> list:
        """Aplikuje filtry do listy paczek"""
        filtered_items = items

        # Filtr słów kluczowych
        if filters['keywords']:
            keywords = filters['keywords'].lower().split()
            filtered_items = [
                item for item in filtered_items
                if any(keyword in item['store']['store_name'].lower() for keyword in keywords)
            ]

        # Filtr firmy
        if filters['company']:
            filtered_items = [
                item for item in filtered_items
                if item['store']['store_name'] == filters['company']
            ]

        # Filtr ceny
        values = self.options_frame.get_values()
        min_price = values['min_price']
        max_price = values['max_price']

        filtered_items = [
            item for item in filtered_items
            if min_price <= (float(item['item']['price_including_taxes']['minor_units']) / 100) <= max_price
        ]

        return filtered_items

    def _check_new_packages(self, new_items: list):
        """Sprawdza i powiadamia o nowych paczkach"""
        old_ids = {p['item']['item_id'] for p in self.packages}

        for package in new_items:
            if package['item']['item_id'] not in old_ids:
                store_name = package['store']['store_name']
                self.logger.info(f"Znaleziono nową paczkę: {store_name}")
                self._send_notification(package)

    def _on_closing(self):
        """Obsługa zamknięcia okna"""
        self.logger.info("=== Rozpoczęcie procedury zamykania ===")

        try:
            self.is_running = False

            if messagebox.askokcancel("Zamykanie", "Czy na pewno chcesz zamknąć aplikację?"):
                # Anuluj wszystkie oczekujące taski
                for task in asyncio.all_tasks(self.loop):
                    task.cancel()

                # Zatrzymaj i zamknij event loop
                self.loop.stop()
                self.loop.close()

                self.root.quit()
                self.logger.info("Aplikacja została zamknięta")
            else:
                self.is_running = True
                self.logger.debug("Użytkownik anulował zamknięcie")

        except Exception as e:
            self.logger.error(f"Błąd podczas zamykania aplikacji: {e}")

    def run(self):
        """Uruchamia główne okno"""
        self.logger.info("=== Uruchamianie głównego okna ===")
        try:
            if not self.root.winfo_ismapped():
                self.logger.debug("Okno nie jest widoczne, pokazuję...")
                self.root.deiconify()

            # Uruchom przetwarzanie kolejki async
            self._process_async_queue()

            self.logger.debug("Uruchamiam główną pętlę...")
            self.root.mainloop()

            self.logger.info("Główna pętla okna zakończona")

        except Exception as e:
            self.logger.error(f"Błąd podczas uruchamiania głównego okna: {e}")
            raise
