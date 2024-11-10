import asyncio
import sys
import tkinter as tk
from tkinter import ttk, messagebox

from .auth_handler import AuthenticationHandler
from .components import EmailFrame, CodeFrame, ButtonFrame
from ..styles.theme import TGTGStyles
from ...utils import TGTGLogger


class CredentialsWindow:
    """Okno do generowania i zarządzania danymi uwierzytelniającymi TGTG"""

    def __init__(self, parent=None):
        self.logger = TGTGLogger("CredentialsWindow").get_logger()
        self.logger.info("=== Rozpoczęcie inicjalizacji okna credentials ===")
        self.logger.debug(f"Inicjalizacja z parent: {parent}")

        try:
            # Szczegółowe logowanie wersji i środowiska
            self.logger.debug(f"Python version: {sys.version}")
            self.logger.debug(f"Tkinter version: {tk.TkVersion}")
            self.logger.debug(f"System platform: {sys.platform}")
            self.logger.debug(f"System encoding: {sys.getdefaultencoding()}")

            # Inicjalizacja okna
            self.root = tk.Toplevel(parent) if parent else tk.Tk()
            self.logger.debug(f"Typ okna: {'Toplevel' if parent else 'Tk'}")
            self.logger.debug(f"Window identifier: {self.root.winfo_id()}")

            # Konfiguracja okna
            self._configure_window()

            # Komponent autentykacji
            self.logger.debug("Inicjalizacja komponentu autentykacji...")
            self.auth_handler = AuthenticationHandler()

            # Event do sygnalizacji zakończenia
            self.credentials_ready = asyncio.Event()
            self.logger.debug("Utworzono event asyncio dla sygnalizacji credentials")

            # Flaga aktywności okna
            self.is_active = True
            self.logger.debug("Ustawiono flagę aktywności okna")

            # Inicjalizacja komponentów UI
            self._initialize_ui()

            self.logger.info("=== Inicjalizacja okna credentials zakończona pomyślnie ===")

        except Exception as ex:
            self.logger.error(f"!!! Krytyczny błąd podczas inicjalizacji okna: {ex}", exc_info=True)
            self.logger.error(f"Typ błędu: {type(ex).__name__}")
            raise

    def _configure_window(self):
        """Konfiguruje podstawowe parametry okna"""
        self.logger.debug("=== Rozpoczęcie konfiguracji parametrów okna ===")

        try:
            # Podstawowa konfiguracja
            self.root.title("TGTG Detector - Logowanie")
            self.logger.debug("Ustawiono tytuł okna")

            self.root.resizable(False, False)
            self.logger.debug("Zablokowano możliwość zmiany rozmiaru")

            self.root.grab_set()
            self.logger.debug("Ustawiono grab_set() dla okna")

            # Geometria okna
            size = '400x400'
            self.root.geometry(size)
            self.logger.debug(f'Ustawiono geometrię okna: {size}')

            # Protokół zamknięcia
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            self.logger.debug("Zarejestrowano protokół WM_DELETE_WINDOW")

            # Aplikacja stylów
            self.logger.debug("Rozpoczęcie aplikacji stylów Sun Valley...")
            TGTGStyles.apply_theme(self.root)
            self.logger.debug("Style zostały pomyślnie zastosowane")

            self.logger.debug("=== Konfiguracja okna zakończona pomyślnie ===")

        except Exception as ex:
            self.logger.error(f"Błąd podczas konfiguracji okna: {ex}", exc_info=True)
            raise

    def _initialize_ui(self):
        """Inicjalizuje wszystkie komponenty UI"""
        self.logger.debug("=== Rozpoczęcie inicjalizacji komponentów UI ===")

        try:
            # Główny kontener
            self.logger.debug("Tworzenie głównego frame...")
            main_frame = ttk.Frame(self.root)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.logger.debug("Główny frame został utworzony i spakowany")

            # Nagłówek
            self.logger.debug("Inicjalizacja nagłówka...")
            self._create_header(main_frame)
            self.logger.debug("Nagłówek został utworzony")

            # Komponenty formularza
            self.logger.debug("Inicjalizacja komponentów formularza...")

            self.logger.debug("Tworzenie EmailFrame...")
            self.email_frame = EmailFrame(main_frame)

            self.logger.debug("Tworzenie CodeFrame...")
            self.code_frame = CodeFrame(main_frame)

            self.logger.debug("Tworzenie ButtonFrame...")
            self.button_frame = ButtonFrame(main_frame)

            # Podpięcie akcji
            self.logger.debug("Podpinanie akcji do przycisków...")
            self.button_frame.bind_auth_action(self._handle_auth_button)
            self.button_frame.bind_close_action(self._on_closing)
            self.logger.debug("Akcje zostały podpięte")

            # Status
            self.logger.debug("Inicjalizacja pola statusu...")
            self._create_status(main_frame)
            self.logger.debug("Pole statusu zostało utworzone")

            # Centrowanie okna
            self.logger.debug("Centrowanie okna...")
            self._center_window()
            self.logger.debug("Okno zostało wycentrowane")

            self.logger.debug("=== Inicjalizacja UI zakończona pomyślnie ===")

        except Exception as e:
            self.logger.error(f"Błąd podczas inicjalizacji UI: {e}", exc_info=True)
            raise

    def _create_header(self, parent: ttk.Frame):
        """Tworzy nagłówek okna"""
        self.logger.debug("=== Tworzenie nagłówka ===")

        try:
            # Główny tytuł
            header_label = ttk.Label(
                parent,
                text="Logowanie do Too Good To Go",
                style='Header.TLabel'
            )
            header_label.pack(fill=tk.X, pady=(0, 20))
            self.logger.debug("Utworzono główny tytuł")

            # Instrukcje
            instructions_label = ttk.Label(
                parent,
                text="Podaj adres email używany w aplikacji Too Good To Go.\n"
                     "Po kliknięciu przycisku otrzymasz email z linkiem do zalogowania.\n\n"
                     "UWAGA: Link należy otworzyć na komputerze\n"
                     "(otwarcie na telefonie nie zadziała jeśli masz zainstalowaną aplikację TGTG).",
                style='Normal.TLabel',
                wraplength=350
            )
            instructions_label.pack(fill=tk.X, pady=(0, 10))
            self.logger.debug("Utworzono instrukcje")

            self.logger.debug("=== Nagłówek utworzony pomyślnie ===")

        except Exception as e:
            self.logger.error(f"Błąd podczas tworzenia nagłówka: {e}", exc_info=True)
            raise

    def _create_status(self, parent: ttk.Frame):
        """Tworzy pole statusu"""
        self.logger.debug("=== Tworzenie pola statusu ===")

        try:
            self.status_var = tk.StringVar(value="Oczekiwanie na wprowadzenie emaila...")
            self.logger.debug("Utworzono zmienną statusu")

            self.status_label = ttk.Label(
                parent,
                textvariable=self.status_var,
                style='Status.TLabel',
                wraplength=350
            )
            self.status_label.pack(fill=tk.X, pady=10)
            self.logger.debug("Utworzono i spakowano label statusu")

            self.logger.debug("=== Pole statusu utworzone pomyślnie ===")

        except Exception as e:
            self.logger.error(f"Błąd podczas tworzenia pola statusu: {e}", exc_info=True)
            raise

    def _center_window(self):
        """Centruje okno na ekranie"""
        self.logger.debug("=== Rozpoczęcie centrowania okna ===")

        try:
            # Wymuszenie przetworzenia oczekujących zdarzeń
            self.root.update_idletasks()
            self.logger.debug("Wymuszono update_idletasks()")

            # Pobierz wymiary ekranu
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.logger.debug(f"Wymiary ekranu: {screen_width}x{screen_height}")

            # Pobierz wymiary okna
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            self.logger.debug(f"Wymiary okna: {width}x{height}")

            # Oblicz pozycję
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)
            self.logger.debug(f"Obliczona pozycja: x={x}, y={y}")

            self.root.geometry(f'{width}x{height}+{x}+{y}')
            self.logger.debug(f"Ustawiono geometrię okna: {width}x{height}+{x}+{y}")

            # Wymuszenie aktualizacji
            self.root.update()
            self.logger.debug("Wymuszono update()")

            self.logger.debug("=== Centrowanie okna zakończone pomyślnie ===")

        except Exception as e:
            self.logger.error(f"Błąd podczas centrowania okna: {e}", exc_info=True)
            raise

    def _on_closing(self):
        """Obsługa zamknięcia okna"""
        self.logger.info("=== Rozpoczęcie procedury zamykania okna ===")
        try:
            self.is_active = False
            self.logger.debug("Ustawiono flagę is_active=False")

            self.credentials_ready.set()
            self.logger.debug("Ustawiono credentials_ready event")

            self.root.destroy()
            self.logger.info("Okno zostało zamknięte")

        except Exception as e:
            self.logger.error(f"Błąd podczas zamykania okna: {e}", exc_info=True)
            raise

    def _handle_auth_button(self):
        """Handler przycisku autentykacji — nie async"""
        self.logger.debug("Obsługa przycisku autentykacji")
        asyncio.create_task(self._start_auth_process())

    async def _start_auth_process(self):
        """Rozpoczyna proces autentykacji"""
        self.logger.info("=== Rozpoczęcie procesu autentykacji ===")

        try:
            email = self.email_frame.get_email()
            self.logger.debug(f"Pobrano email: {email}")

            if not email:
                self.logger.warning("Próba autentykacji bez podania emaila")
                messagebox.showerror("Błąd", "Podaj adres email!")
                return

            # Rozpocznij proces logowania, tylko jeśli jeszcze nie jest w toku
            if not self.auth_handler.is_auth_in_progress:
                self.status_var.set("Wysyłanie emaila z linkiem do logowania...\nSprawdź swoją skrzynkę!")
                self.logger.info(f"Rozpoczęcie logowania dla: {email}")

                try:
                    await self.auth_handler.start_login(email)
                    self.logger.info("Logowanie zakończone sukcesem")

                    # Poczekaj chwilę, żeby użytkownik zobaczył komunikat
                    self.status_var.set("Logowanie zakończone sukcesem!")
                    await asyncio.sleep(1)

                    # Zamknij okno
                    messagebox.showinfo("Sukces", "Logowanie zakończone sukcesem!")
                    self._on_closing()

                except Exception as e:
                    self.logger.error(f"Błąd podczas procesu logowania: {e}")
                    self.status_var.set(f"Błąd logowania: {str(e)}")
                    messagebox.showerror("Błąd", f"Błąd logowania: {str(e)}")
            else:
                self.logger.warning("Proces autentykacji jest już w toku")
                self.status_var.set("Logowanie w toku...")

        except Exception as e:
            self.logger.error(f"Błąd podczas procesu autentykacji: {e}", exc_info=True)
            self.status_var.set(f"Błąd: {str(e)}")
            messagebox.showerror("Błąd", f"Wystąpił błąd: {str(e)}")

    async def wait_for_completion(self):
        """Czeka na zakończenie procesu autentykacji"""
        self.logger.debug("Rozpoczęcie oczekiwania na zakończenie autentykacji...")
        await self.credentials_ready.wait()
        self.logger.debug("Zakończono oczekiwanie na autentykację")

    def update(self):
        """Aktualizuje okno"""
        try:
            self.root.update()
        except Exception as e:
            self.logger.error(f"Błąd podczas aktualizacji okna: {e}", exc_info=True)
            raise
