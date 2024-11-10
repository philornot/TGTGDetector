import asyncio
import signal
import tkinter as tk

from src.api import TGTGApiClient
from src.config import TGTGSettings
from src.gui import CredentialsWindow, TGTGStyles, MainWindow
from src.utils import NiceLogger


class TGTGDetector:
    """
    Główna klasa aplikacji TGTG Detector
    """

    def __init__(self):
        self.logger = NiceLogger("TGTG_Detector").get_logger()
        self.logger.info("=== Inicjalizacja TGTG Detector ===")

        self.is_running = True
        self.api_client = None
        self.settings = TGTGSettings()
        self.root = None
        self.main_window = None
        self.last_check_time = None

        self.logger.debug("Konfiguracja obsługi sygnałów...")
        self._setup_signal_handlers()
        self.logger.debug("Inicjalizacja zakończona")

    def _setup_signal_handlers(self):
        """Konfiguracja obsługi sygnałów systemowych"""
        self.logger.debug("=== Konfiguracja sygnałów systemowych ===")
        try:
            signals = (signal.SIGTERM, signal.SIGINT)
            for sig in signals:
                signal.signal(sig, self._signal_handler)
                self.logger.debug(f"Zarejestrowano handler dla sygnału {sig}")
        except Exception as e:
            self.logger.error(f"Błąd podczas konfiguracji sygnałów: {e}", exc_info=True)

    def _has_valid_credentials(self) -> bool:
        """Sprawdza, czy są zapisane poprawne dane logowania"""
        self.logger.debug("Sprawdzanie zapisanych credentials...")

        config = self.settings.config
        required_fields = ['access_token', 'refresh_token', 'user_id', 'cookie']

        # Sprawdź, czy wszystkie wymagane pola są obecne i niepuste
        credentials_present = all(
            bool(config.get(field)) and len(str(config.get(field)).strip()) > 0
            for field in required_fields
        )

        self.logger.debug(f"Wymagane pola: {required_fields}")
        self.logger.debug(f"Status poszczególnych pól:")
        for field in required_fields:
            value = config.get(field, '')
            is_present = bool(value) and len(str(value).strip()) > 0
            self.logger.debug(f"- {field}: {'✓' if is_present else '✗'}")

        self.logger.debug(f"Wynik sprawdzenia credentials: {credentials_present}")
        return credentials_present

    def _create_root_window(self):
        """Tworzy główne okno aplikacji"""
        self.logger.debug("=== Tworzenie głównego okna aplikacji ===")

        try:
            if not self.root:
                self.root = tk.Tk()
                self.logger.debug("Utworzono nowy obiekt Tk")

                # Konfiguracja głównego okna
                self.root.withdraw()  # Ukryj na start
                self.root.title("TGTG Monitor")

                # Zastosuj style
                TGTGStyles.apply_theme(self.root)
                self.logger.debug("Zastosowano style")

                self.logger.debug("Główne okno zostało utworzone")
            else:
                self.logger.debug("Główne okno już istnieje")

        except Exception as e:
            self.logger.error(f"Błąd podczas tworzenia głównego okna: {e}", exc_info=True)
            raise

    async def _show_credentials_window(self):
        """Pokazuje okno logowania i czeka na wprowadzenie danych"""
        self.logger.info("=== Pokazywanie okna logowania ===")

        try:
            self._create_root_window()

            self.logger.debug("Tworzenie okna credentials...")
            credentials_window = CredentialsWindow(self.root)

            async def update_window():
                while credentials_window.is_active:
                    try:
                        credentials_window.update()
                        await asyncio.sleep(0.05)
                    except Exception as ex:
                        self.logger.error(f"Błąd podczas aktualizacji okna credentials: {ex}")
                        break

            self.logger.debug("Uruchamianie pętli aktualizacji okna...")
            update_task = asyncio.create_task(update_window())

            await credentials_window.wait_for_completion()
            self.logger.debug("Okno credentials zakończyło pracę")

            update_task.cancel()
            try:
                await update_task
            except asyncio.CancelledError:
                self.logger.debug("Task aktualizacji okna został anulowany")

            # Reload konfiguracji po zamknięciu okna credentials
            self.logger.debug("Przeładowywanie konfiguracji po logowaniu...")
            self.settings = TGTGSettings()  # To przeładuje konfigurację z pliku

            if not self._has_valid_credentials():
                self.logger.critical("Nie wprowadzono wymaganych danych logowania!")
                raise ValueError("Brak wymaganych danych logowania")

        except Exception as e:
            self.logger.error(f"Błąd w oknie credentials: {e}", exc_info=True)
            raise

    def _show_main_window(self):
        """Pokazuje główne okno aplikacji"""
        self.logger.info("=== Uruchamianie głównego okna aplikacji ===")

        try:
            self.logger.debug("Inicjalizacja głównego okna...")
            self.main_window = MainWindow(self.root, self.api_client)

            self.logger.debug("Uruchamianie głównego okna...")
            self.main_window.run()

            self.logger.info("Główne okno zostało pomyślnie uruchomione")

        except Exception as e:
            self.logger.error(f"Błąd podczas pokazywania głównego okna: {e}", exc_info=True)
            raise

    def _signal_handler(self, signum, _):
        """Obsługa sygnałów zatrzymania"""
        self.logger.warning(f"Otrzymano sygnał {signum}. Rozpoczynam bezpieczne zatrzymywanie...")
        self.is_running = False
        if self.root:
            self.root.quit()

    async def start(self):
        """Główna metoda startująca aplikację"""
        self.logger.info("=== Uruchamianie aplikacji TGTG Monitor ===")

        try:
            # Inicjalizacja głównego okna
            self._create_root_window()

            # Sprawdź dane logowania
            if not self._has_valid_credentials():
                self.logger.warning("Brak wymaganych danych logowania. Otwieram okno logowania...")
                await self._show_credentials_window()

            # Inicjalizacja API
            self.logger.debug("Inicjalizacja API...")
            self.api_client = TGTGApiClient()

            try:
                self.logger.debug("Próba logowania z zapisanymi danymi...")
                await self.api_client.login(
                    email=self.settings.config['email'],
                    access_token=self.settings.config.get('access_token')
                )
            except Exception as e:
                self.logger.error(f"Błąd logowania z zapisanymi danymi: {e}")
                self.logger.info("Próbuję ponownie z nowymi danymi logowania...")
                await self._show_credentials_window()
                await self.api_client.login(
                    email=self.settings.config['email'],
                    access_token=self.settings.config.get('access_token')
                )

            # Pokaż główne okno
            if self.api_client and self.api_client.is_logged_in:
                self.logger.info("Poprawnie zalogowano, pokazuję główne okno...")
                self._show_main_window()
            else:
                raise Exception("Nie udało się zalogować")

        except asyncio.CancelledError:
            self.logger.warning("Otrzymano żądanie anulowania...")
        except Exception as e:
            self.logger.error(f"Wystąpił błąd w głównej pętli: {e}", exc_info=True)
            raise
        finally:
            await self.stop()

    async def stop(self):
        """Bezpieczne zatrzymanie aplikacji"""
        self.logger.info("=== Zatrzymywanie aplikacji ===")

        try:
            self.is_running = False
            self.logger.debug("Flaga is_running ustawiona na False")

            if self.api_client:
                self.logger.debug("Czyszczenie API client...")
                await self.api_client.cleanup()

            if self.root:
                self.logger.debug("Zamykanie głównego okna...")
                try:
                    self.root.quit()
                    self.root.destroy()
                except Exception as e:
                    self.logger.error(f"Błąd podczas zamykania okna: {e}")

            self.logger.info("Aplikacja została pomyślnie zatrzymana")

        except Exception as e:
            self.logger.error(f"Błąd podczas zatrzymywania aplikacji: {e}", exc_info=True)

    def run(self):
        """Uruchamia główne okno"""
        self.logger.info("=== Uruchamianie głównego okna ===")
        try:
            if not self.root.winfo_ismapped():
                self.logger.debug("Okno nie jest widoczne, pokazuję...")
                self.root.deiconify()

            self.logger.debug("Uruchamiam główną pętlę...")

            # Utworzenie i ustawienie pętli zdarzeń
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            def update():
                if self.is_running:
                    try:
                        loop.run_until_complete(asyncio.sleep(0.1))
                        self.root.after(100, update)
                    except Exception as e:
                        self.logger.error(f"Błąd w pętli update: {e}")

            update()
            self.root.mainloop()
            self.logger.info("Główna pętla okna zakończona")

        except Exception as e:
            self.logger.error(f"Błąd podczas uruchamiania głównego okna: {e}", exc_info=True)
            raise


async def main():
    logger = NiceLogger("Main").get_logger()
    detector = TGTGDetector()
    try:
        logger.info("=== Uruchamianie głównej funkcji aplikacji ===")
        await detector.start()
    except KeyboardInterrupt:
        logger.warning("Otrzymano KeyboardInterrupt")
        await detector.stop()
    except Exception as e:
        logger.critical(f"Krytyczny błąd programu: {e}", exc_info=True)
        raise
    finally:
        logger.info("=== Zakończenie działania aplikacji ===")


if __name__ == "__main__":
    asyncio.run(main())
