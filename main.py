import asyncio
import random
import signal
import time
import tkinter as tk
from datetime import datetime

from src.api import TGTGApiClient
from src.config import TGTGSettings
from src.gui import SettingsWindow, CredentialsWindow, TGTGStyles
from src.utils import TGTGLogger


class TGTGDetector:
    """
    Główna klasa aplikacji TGTG Detector
    """

    def __init__(self):
        self.logger = TGTGLogger("TGTG_Detector").get_logger()
        self.logger.info("Inicjalizacja TGTG Detector...")

        self.is_running = True
        self.api_client = None
        self.settings = TGTGSettings()
        self._setup_signal_handlers()
        self.last_check_time = None

        # Root dla okien Tkinter
        self.tk_root = None

    def _setup_signal_handlers(self):
        """Konfiguracja obsługi sygnałów systemowych"""
        self.logger.debug("Konfiguracja obsługi sygnałów systemowych...")
        signals = (signal.SIGTERM, signal.SIGINT)
        for sig in signals:
            signal.signal(sig, self._signal_handler)

    async def _show_settings_window(self):
        """Pokazuje okno ustawień"""
        if not self.tk_root:
            self.tk_root = tk.Tk()
            self.tk_root.withdraw()  # Ukryj główne okno
            TGTGStyles.apply_theme(self.tk_root)  # Aplikuj style do root window

        settings_window = SettingsWindow(self.tk_root)
        settings_window.run()

    def _signal_handler(self, signum, _):
        """Obsługa sygnałów zatrzymania"""
        self.logger.warning(f"Otrzymano sygnał {signum}. Rozpoczynam bezpieczne zatrzymywanie...")
        self.is_running = False

    async def _show_credentials_window(self):
        """Pokazuje okno do wprowadzania credentials i czeka na ich wprowadzenie"""
        if not self.tk_root:
            self.logger.debug("Tworzenie głównego okna Tk...")
            self.tk_root = tk.Tk()
            self.tk_root.withdraw()  # Ukryj główne okno

        self.logger.debug("Tworzenie okna credentials...")
        credentials_window = CredentialsWindow(self.tk_root)

        # Funkcja do aktualizacji okna w pętli zdarzeń asyncio
        async def update_window():
            last_log_time = 0
            try:
                while credentials_window.is_active:
                    current_time = time.time()
                    # Log tylko co 5 sekund
                    if current_time - last_log_time >= 5:
                        self.logger.debug("Okno credentials aktywne...")
                        last_log_time = current_time

                    credentials_window.root.update()
                    await asyncio.sleep(0.05)
            except Exception as e:
                self.logger.error(f"Błąd podczas aktualizacji okna: {e}")
                credentials_window.is_active = False

        # Uruchom aktualizację okna w tle
        update_task = asyncio.create_task(update_window())

        # Czekaj na zakończenie wprowadzania credentials
        self.logger.debug("Oczekiwanie na wprowadzenie credentials...")
        await credentials_window.wait_for_completion()

        # Zakończ task aktualizacji okna
        update_task.cancel()
        try:
            await update_task
        except asyncio.CancelledError:
            pass

        # Sprawdź, czy credentials zostały zapisane
        self.logger.debug("Sprawdzanie czy credentials zostały zapisane...")
        new_config = self.settings.load_config()
        if not all([
            new_config.get('access_token'),
            new_config.get('refresh_token'),
            new_config.get('user_id'),
            new_config.get('cookie')
        ]):
            self.logger.critical("Nie wprowadzono wymaganych danych logowania!")
            raise ValueError("Brak wymaganych danych logowania")

        self.logger.info("Pomyślnie wprowadzono dane logowania")
        return new_config

    async def _initialize_api(self):
        """Inicjalizacja klienta API"""
        if not self.api_client:
            self.api_client = TGTGApiClient()
            config = self.settings.config

            # Sprawdź, czy mamy wszystkie wymagane dane logowania
            if not all([
                config.get('access_token'),
                config.get('refresh_token'),
                config.get('user_id'),
                config.get('cookie')
            ]):
                self.logger.warning("Brak wymaganych danych logowania. Otwieram okno konfiguracji...")
                config = await self._show_credentials_window()

            try:
                await self.api_client.login(
                    email=config['email'],
                    access_token=config.get('access_token')
                )
            except Exception as e:
                self.logger.error(f"Błąd logowania z zapisanymi danymi: {e}")
                self.logger.info("Próbuję ponownie z nowymi danymi logowania...")
                config = await self._show_credentials_window()
                await self.api_client.login(
                    email=config['email'],
                    access_token=config.get('access_token')
                )

    async def check_available_items(self):
        """
        Sprawdza dostępne paczki
        """
        try:
            self.logger.debug("Rozpoczynam sprawdzanie dostępnych paczek...")
            await self._initialize_api()

            all_items = []
            for location in self.settings.config['locations']:
                items = await self.api_client.get_items(
                    lat=location['lat'],
                    lng=location['lng'],
                    radius=location.get('radius', 5)
                )
                all_items.extend(items)

            if all_items:
                self.logger.info(f"Znaleziono {len(all_items)} dostępnych paczek")

                filtered_items = [
                    item for item in all_items
                    if self.settings.config['min_price'] <= (
                            float(item['item']['price_including_taxes']['minor_units']) / 100) <=
                       self.settings.config['max_price']
                ]

                sample_size = min(5, len(filtered_items))
                sample_items = random.sample(filtered_items, sample_size) if filtered_items else []

                self.logger.info("=== Przykładowe dostępne paczki ===")
                for item in sample_items:
                    self.logger.info("\n" + self.api_client.format_item_info(item))
                self.logger.info("================================")
            else:
                self.logger.info("Brak dostępnych paczek w wybranych lokalizacjach")

            self.last_check_time = datetime.now()

        except Exception as e:
            self.logger.error(f"Błąd podczas sprawdzania paczek: {e}")

    async def start(self):
        """
        Główna metoda startująca monitoring
        """
        self.logger.info("Rozpoczynam monitoring TGTG...")
        while self.is_running:
            try:
                await self.check_available_items()

                if self.last_check_time:
                    self.logger.debug(f"Ostatnie sprawdzenie: {self.last_check_time.strftime('%H:%M:%S')}")

                await asyncio.sleep(self.settings.config['refresh_interval'])

            except asyncio.CancelledError:
                self.logger.warning("Otrzymano żądanie anulowania...")
                break
            except Exception as e:
                self.logger.error(f"Wystąpił błąd w głównej pętli: {e}")
                await asyncio.sleep(5)

        self.logger.info("Monitoring zatrzymany")

    async def stop(self):
        """
        Bezpieczne zatrzymanie detektora
        """
        self.logger.info("Otrzymano żądanie zatrzymania...")
        self.is_running = False
        if self.api_client:
            await self.api_client.cleanup()
        if self.tk_root:
            self.tk_root.destroy()


async def main():
    detector = TGTGDetector()
    try:
        await detector.start()
    except KeyboardInterrupt:
        await detector.stop()
    except Exception as e:
        detector.logger.critical(f"Krytyczny błąd programu: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
