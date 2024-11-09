import asyncio
import random  # Dodaj import na górze pliku
import signal
from datetime import datetime

from src.api import TGTGApiClient
from src.config import TGTGSettings
from src.utils import TGTGLogger


class TGTGDetector:
    """
    Główna klasa aplikacji TGTG Detector
    """

    def __init__(self):
        self.logger = TGTGLogger("TGTG_Detector").get_logger()
        self.logger.info("Inicjalizacja TGTG Detector...")

        # Flaga do kontroli głównej pętli
        self.is_running = True

        # Klient API
        self.api_client = None

        # Wczytanie konfiguracji
        self.settings = TGTGSettings()

        # Konfiguracja obsługi sygnałów
        self._setup_signal_handlers()

        # Status ostatniego sprawdzenia
        self.last_check_time = None

    def _setup_signal_handlers(self):
        """Konfiguracja obsługi sygnałów systemowych"""
        self.logger.debug("Konfiguracja obsługi sygnałów systemowych...")
        signals = (signal.SIGTERM, signal.SIGINT)
        for sig in signals:
            signal.signal(sig, self._signal_handler)

    def _signal_handler(self, signum, _):
        """Obsługa sygnałów zatrzymania"""
        self.logger.warning(f"Otrzymano sygnał {signum}. Rozpoczynam bezpieczne zatrzymywanie...")
        self.is_running = False

    async def _initialize_api(self):
        """Inicjalizacja klienta API"""
        if not self.api_client:
            self.api_client = TGTGApiClient()
            config = self.settings.config
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

                # Filtrowanie według ceny
                filtered_items = [
                    item for item in all_items
                    if self.settings.config['min_price'] <= (
                            float(item['item']['price_including_taxes']['minor_units']) / 100) <=
                    self.settings.config['max_price']
                ]

                # Wyświetl do 5 losowych paczek dla testów
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
                await asyncio.sleep(5)  # Czekaj przed ponowną próbą

        self.logger.info("Monitoring zatrzymany")

    async def stop(self):
        """
        Bezpieczne zatrzymanie detektora
        """
        self.logger.info("Otrzymano żądanie zatrzymania...")
        self.is_running = False
        if self.api_client:
            await self.api_client.cleanup()


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
