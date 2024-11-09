import tkinter as tk
from tkinter import ttk, messagebox

from ...config import TGTGSettings
from ...utils import TGTGLogger
from ..styles.theme import TGTGStyles
from .components import LocationFrame, RefreshIntervalFrame, ButtonFrame


class SettingsWindow:
    """Okno konfiguracji aplikacji"""

    def __init__(self, parent=None):
        self.logger = TGTGLogger("SettingsWindow").get_logger()
        self.logger.info("=== Rozpoczęcie inicjalizacji okna ustawień ===")

        try:
            # Inicjalizacja ustawień
            self.settings = TGTGSettings()
            self.logger.debug("Zainicjalizowano komponent ustawień")

            # Tworzenie okna
            self.window = tk.Toplevel(parent) if parent else tk.Tk()
            self.logger.debug(f"Utworzono okno typu: {'Toplevel' if parent else 'Tk'}")

            self._configure_window()
            self._initialize_ui()
            self._load_settings()

            self.logger.info("=== Inicjalizacja okna ustawień zakończona pomyślnie ===")

        except Exception as e:
            self.logger.error(f"Błąd podczas inicjalizacji okna ustawień: {e}", exc_info=True)
            raise

    def _configure_window(self):
        """Konfiguruje podstawowe parametry okna"""
        self.logger.debug("=== Konfiguracja parametrów okna ===")

        try:
            self.window.title("TGTG Detector - Ustawienia")
            self.window.geometry("600x400")
            self.window.resizable(False, False)

            # Jeśli jest okno rodzica, ustaw zależności
            if self.window.master:
                self.window.transient(self.window.master)
                self.window.grab_set()
                self.logger.debug("Ustawiono zależności względem okna rodzica")

            # Aplikacja stylów
            TGTGStyles.apply_theme(self.window)
            self.logger.debug("Zastosowano style")

            self.logger.debug("=== Konfiguracja okna zakończona ===")

        except Exception as e:
            self.logger.error(f"Błąd podczas konfiguracji okna: {e}", exc_info=True)
            raise

    def _initialize_ui(self):
        """Inicjalizuje komponenty UI"""
        self.logger.debug("=== Inicjalizacja komponentów UI ===")

        try:
            # Główny kontener z zakładkami
            notebook = ttk.Notebook(self.window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.logger.debug("Utworzono notebook")

            # Zakładka Ogólne
            general_frame = ttk.Frame(notebook)
            notebook.add(general_frame, text="Ogólne")
            self.logger.debug("Dodano zakładkę Ogólne")

            # Komponenty
            self.refresh_frame = RefreshIntervalFrame(general_frame)
            self.location_frame = LocationFrame(general_frame)
            self.button_frame = ButtonFrame(general_frame)

            # Podpięcie akcji
            self.button_frame.bind_save_action(self._save_settings)
            self.button_frame.bind_cancel_action(self._close_window)

            self.logger.debug("Utworzono i skonfigurowano wszystkie komponenty")

            # Centrowanie okna
            self._center_window()

        except Exception as e:
            self.logger.error(f"Błąd podczas inicjalizacji UI: {e}", exc_info=True)
            raise

    def _center_window(self):
        """Centruje okno na ekranie"""
        self.logger.debug("Centrowanie okna...")

        try:
            self.window.update_idletasks()
            width = self.window.winfo_width()
            height = self.window.winfo_height()
            x = (self.window.winfo_screenwidth() // 2) - (width // 2)
            y = (self.window.winfo_screenheight() // 2) - (height // 2)
            self.window.geometry(f'{width}x{height}+{x}+{y}')
            self.logger.debug(f"Ustawiono pozycję okna: {width}x{height}+{x}+{y}")

        except Exception as e:
            self.logger.error(f"Błąd podczas centrowania okna: {e}", exc_info=True)
            raise

    def _load_settings(self):
        """Ładuje zapisane ustawienia do formularza"""
        self.logger.debug("=== Ładowanie zapisanych ustawień ===")

        try:
            # Wczytaj interwał
            interval = self.settings.config['refresh_interval']
            self.refresh_frame.set_value(interval)
            self.logger.debug(f"Załadowano interwał: {interval}")

            # Wczytaj lokalizację
            location = self.settings.get_location(0)
            if location:
                self.location_frame.set_values(
                    location.lat,
                    location.lng,
                    location.radius
                )
                self.logger.debug(f"Załadowano lokalizację: {location.lat}, {location.lng}, {location.radius}")

            self.logger.debug("=== Załadowano wszystkie ustawienia ===")

        except Exception as e:
            self.logger.error(f"Błąd podczas ładowania ustawień: {e}", exc_info=True)
            raise

    def _save_settings(self):
        """Zapisuje ustawienia"""
        self.logger.info("=== Rozpoczęcie zapisywania ustawień ===")

        try:
            # Pobierz wartości
            interval = self.refresh_frame.get_value()
            lat, lng, radius = self.location_frame.get_values()

            # Aktualizuj konfigurację
            self.logger.debug("Aktualizacja konfiguracji...")
            self.settings.config['refresh_interval'] = interval
            self.settings.config['locations'] = [{
                "lat": lat,
                "lng": lng,
                "radius": radius
            }]

            # Zapisz konfigurację
            self.logger.debug("Zapisywanie konfiguracji...")
            self.settings.save_config(self.settings.config)

            messagebox.showinfo("Sukces", "Ustawienia zostały zapisane")
            self.logger.info("=== Ustawienia zostały pomyślnie zapisane ===")

            self._close_window()

        except ValueError as e:
            self.logger.error(f"Błąd walidacji: {e}")
            messagebox.showerror("Błąd", f"Nieprawidłowe wartości: {str(e)}")
        except Exception as e:
            self.logger.error(f"Błąd podczas zapisywania ustawień: {e}")
            messagebox.showerror("Błąd", f"Błąd podczas zapisywania ustawień: {str(e)}")

    def _close_window(self):
        """Zamyka okno ustawień"""
        self.logger.info("Zamykanie okna ustawień")
        self.window.destroy()

    def run(self):
        """Uruchamia okno ustawień"""
        self.logger.debug("Uruchamianie głównej pętli okna ustawień")
        self.window.mainloop()