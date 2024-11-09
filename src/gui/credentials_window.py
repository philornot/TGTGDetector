import asyncio
import json
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox

from tgtg import TgtgClient

from .styles import TGTGStyles
from ..utils import TGTGLogger


class CredentialsWindow:
    """Okno do generowania i zarządzania danymi uwierzytelniającymi TGTG"""

    def __init__(self, parent=None):
        self.logger = TGTGLogger("CredentialsWindow").get_logger()
        self.logger.info("=== Rozpoczęcie inicjalizacji okna credentials ===")

        try:
            self.logger.debug(f"Python version: {sys.version}")
            self.logger.debug(f"Tkinter version: {tk.TkVersion}")

            # Tworzenie okna
            self.logger.debug("Tworzenie okna głównego...")
            self.root = tk.Toplevel(parent) if parent else tk.Tk()
            self.logger.debug(f"Typ okna: {'Toplevel' if parent else 'Tk'}")

            self.root.title("TGTG Detector - Generator Credentiali")
            self.logger.debug("Ustawiono tytuł okna")

            # Wymuszenie przetwarzania zdarzeń przed ustawieniem geometrii
            self.root.update_idletasks()

            self.root.geometry("400x300")
            self.logger.debug("Ustawiono geometrię okna: 400x300")

            # Flaga aktywności okna
            self.is_active = True
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            self.logger.debug("Skonfigurowano protokół zamknięcia okna")

            # Event do sygnalizacji zakończenia generowania credentials
            self.credentials_ready = asyncio.Event()
            self.logger.debug("Utworzono event asyncio")

            # Aplikacja stylów
            self.logger.debug("Rozpoczęcie aplikowania stylów...")
            try:
                TGTGStyles.apply_theme(self.root)
                self.logger.debug("Pomyślnie zastosowano style")
            except Exception as style_error:
                self.logger.error(f"Błąd podczas aplikowania stylów: {style_error}")
                raise

            # Konfiguracja widgetów
            self.logger.debug("Rozpoczęcie tworzenia widgetów...")
            self._create_widgets()
            self.logger.debug("Widgety zostały utworzone")

            self._center_window()
            self.logger.debug("Okno zostało wycentrowane")

            # Upewnij się, że okno jest na wierzchu
            self.root.lift()
            self.root.focus_force()

            # Wymuszenie odświeżenia okna
            self.root.update()

            self.logger.info("=== Inicjalizacja okna credentials zakończona pomyślnie ===")

        except Exception as e:
            self.logger.error(f"!!! Krytyczny błąd podczas inicjalizacji okna: {e}", exc_info=True)
            self.logger.error(f"Typ błędu: {type(e).__name__}")
            raise

    def _create_widgets(self):
        """Tworzy i konfiguruje wszystkie widgety"""
        try:
            self.logger.debug("=== Rozpoczęcie tworzenia widgetów ===")

            # Frame główny
            self.logger.debug("Tworzenie głównego frame...")
            main_frame = ttk.Frame(self.root)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.logger.debug("Główny frame utworzony i spakowany")

            # Nagłówek
            self.logger.debug("Tworzenie nagłówka...")
            header = ttk.Label(
                main_frame,
                text="Generator danych logowania TGTG",
                style='Header.TLabel'
            )
            header.pack(fill=tk.X, pady=(0, 20))
            self.logger.debug("Nagłówek utworzony")

            # Instrukcje
            self.logger.debug("Tworzenie instrukcji...")
            instructions = ttk.Label(
                main_frame,
                text="Podaj adres email używany w aplikacji Too Good To Go.\n"
                     "Otrzymasz email z linkiem potwierdzającym.",
                style='Normal.TLabel',
                wraplength=350
            )
            instructions.pack(fill=tk.X, pady=(0, 10))
            self.logger.debug("Instrukcje utworzone")

            # Email frame
            self.logger.debug("Tworzenie frame dla emaila...")
            email_frame = ttk.Frame(main_frame)
            email_frame.pack(fill=tk.X, pady=5)

            ttk.Label(
                email_frame,
                text="Email TGTG:",
                style='Normal.TLabel'
            ).pack(side=tk.LEFT)

            self.email_var = tk.StringVar()
            email_entry = ttk.Entry(email_frame, textvariable=self.email_var)
            email_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
            self.logger.debug("Frame emaila utworzony")

            # Przyciski
            self.logger.debug("Tworzenie przycisków...")
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill=tk.X, pady=20)

            ttk.Button(
                btn_frame,
                text="Generuj credentials",
                command=self._start_credentials_generation
            ).pack(side=tk.LEFT, padx=5)

            ttk.Button(
                btn_frame,
                text="Zamknij",
                command=self._on_closing
            ).pack(side=tk.RIGHT, padx=5)
            self.logger.debug("Przyciski utworzone")

            # Status
            self.logger.debug("Tworzenie pola statusu...")
            self.status_var = tk.StringVar(value="Oczekiwanie na wprowadzenie emaila...")
            self.status_label = ttk.Label(
                main_frame,
                textvariable=self.status_var,
                style='Status.TLabel',
                wraplength=350
            )
            self.status_label.pack(fill=tk.X, pady=10)
            self.logger.debug("Pole statusu utworzone")

            # Wymuszenie aktualizacji
            main_frame.update()
            self.logger.debug("Wymuszono aktualizację main_frame")

            self.logger.info("=== Wszystkie widgety zostały utworzone pomyślnie ===")

        except Exception as e:
            self.logger.error(f"!!! Błąd podczas tworzenia widgetów: {e}", exc_info=True)
            raise

    def _center_window(self):
        """Centruje okno na ekranie"""
        try:
            self.logger.debug("Rozpoczęcie centrowania okna...")

            # Wymuszenie przetworzenia oczekujących zdarzeń
            self.root.update_idletasks()

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

        except Exception as e:
            self.logger.error(f"Błąd podczas centrowania okna: {e}", exc_info=True)
            raise

    def _on_closing(self):
        """Obsługa zamknięcia okna"""
        self.logger.info("Zamykanie okna credentials")
        self.is_active = False
        self.credentials_ready.set()
        self.root.destroy()

    def _start_credentials_generation(self):
        """Rozpoczyna generowanie credentials w osobnym wątku"""
        email = self.email_var.get().strip()
        if not email:
            self.logger.warning("Próba generowania credentials bez podania emaila")
            messagebox.showerror("Błąd", "Podaj adres email!")
            return

        self.logger.info(f"Rozpoczęcie generowania credentials dla: {email}")
        self.status_var.set("Generowanie credentiali... Sprawdź email!")

        # Uruchom generowanie credentials w osobnym wątku
        asyncio.create_task(self._generate_credentials(email))

    async def _generate_credentials(self, email: str):
        """Generuje credentials i zapisuje je do pliku"""
        try:
            self.logger.debug("Tworzenie klienta TGTG...")
            client = TgtgClient(email=email)

            self.logger.info("Pobieranie credentials...")
            credentials = client.get_credentials()

            # Przygotuj config
            config_dir = Path.home() / "Dokumenty" / "TGTG Detector"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_path = config_dir / "config.json"

            self.logger.debug(f"Zapisywanie credentials do: {config_path}")

            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {
                    "refresh_interval": 30,
                    "locations": [
                        {
                            "lat": 52.2297,
                            "lng": 21.0122,
                            "radius": 5
                        }
                    ],
                    "notification_methods": ["console"],
                    "favorite_stores": [],
                    "min_price": 0,
                    "max_price": 1000,
                    "auto_reserve": False
                }

            # Aktualizuj credentials
            config.update({
                "email": email,
                "access_token": credentials["access_token"],
                "refresh_token": credentials["refresh_token"],
                "user_id": credentials["user_id"],
                "cookie": credentials["cookie"]
            })

            # Zapisz config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

            self.logger.info("Credentials zostały pomyślnie wygenerowane i zapisane")
            self.status_var.set(
                "Credentials wygenerowane i zapisane w config.json!\n"
                "Możesz teraz zamknąć to okno."
            )
            messagebox.showinfo(
                "Sukces",
                "Credentials zostały zapisane w pliku config.json"
            )

            # Sygnalizuj zakończenie generowania credentials
            self.credentials_ready.set()
            self.is_active = False
            self.root.destroy()

        except Exception as e:
            self.logger.error(f"Błąd podczas generowania credentials: {e}")
            self.status_var.set(f"Błąd: {str(e)}")
            messagebox.showerror("Błąd", f"Wystąpił błąd: {str(e)}")

    async def wait_for_completion(self):
        """Czeka na zakończenie generowania credentials"""
        await self.credentials_ready.wait()
        self.logger.debug("Zakończono oczekiwanie na credentials")

    def update(self):
        """Aktualizuje okno"""
        self.root.update()
