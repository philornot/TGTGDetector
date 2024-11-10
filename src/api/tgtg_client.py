from typing import Optional, List, Dict, Any

from tgtg import TgtgClient

from ..config import TGTGSettings
from ..utils import NiceLogger


class TGTGApiClient:
    """
    Klient API dla Too Good To Go
    """

    def __init__(self):
        self.logger = NiceLogger("TGTG_API").get_logger()
        self.client = None
        self.settings = TGTGSettings()
        self.is_logged_in = False

    async def login(self, email: str, access_token: Optional[str] = None):
        """
        Logowanie do TGTG. Wykorzystuje zapisane credentials, jeśli są dostępne,
        w przeciwnym razie próbuje zalogować się, używając dostarczonego tokenu lub emaila.
        """
        self.logger.info("Rozpoczynam proces logowania...")

        try:
            if self.is_logged_in and self.client:
                self.logger.info("Już zalogowany, pomijam proces logowania")
                return

            config = self.settings.config
            self.logger.debug("Sprawdzam zapisane credentials...")

            # Jeśli dostarczono access_token, użyj go zamiast zapisanych credentials
            if access_token:
                self.logger.info("Próba logowania z dostarczonym access_token...")
                if not all([
                    config.get('refresh_token'),
                    config.get('user_id'),
                    config.get('cookie')
                ]):
                    raise ValueError("Brakuje wymaganych danych dla dostarczonego access_token")

                self.client = TgtgClient(
                    access_token=access_token,
                    refresh_token=config['refresh_token'],
                    user_id=config['user_id'],
                    cookie=config['cookie']
                )
                try:
                    # Weryfikacja czy credentials działają
                    self.client.get_items()
                    self.is_logged_in = True
                    self.logger.info("Pomyślnie zalogowano przy użyciu dostarczonego access_token")
                    return
                except Exception as e:
                    self.logger.warning(f"Nie udało się użyć dostarczonego access_token: {e}")
                    self.is_logged_in = False

            # Sprawdź czy mamy kompletne zapisane credentials
            has_valid_credentials = all([
                config.get('access_token'),
                config.get('refresh_token'),
                config.get('user_id'),
                config.get('cookie')
            ])

            if has_valid_credentials:
                try:
                    self.logger.info("Znaleziono zapisane credentials, próba logowania...")
                    self.client = TgtgClient(
                        access_token=config['access_token'],
                        refresh_token=config['refresh_token'],
                        user_id=config['user_id'],
                        cookie=config['cookie']
                    )
                    # Weryfikacja czy credentials działają
                    self.client.get_items()
                    self.is_logged_in = True
                    self.logger.info("Pomyślnie zalogowano przy użyciu zapisanych credentials")
                    return
                except Exception as e:
                    self.logger.warning(f"Nie udało się użyć zapisanych credentials: {e}")
                    self.is_logged_in = False

            # Próba logowania przy użyciu emaila
            if email:
                self.logger.info(f"Próba logowania za pomocą emaila: {email}")
                try:
                    self.client = TgtgClient(email=email)
                    # TgtgClient automatycznie spróbuje się zalogować przez email
                    credentials = self.client.get_credentials()
                    self.settings.update_credentials(credentials)
                    self.is_logged_in = True
                    self.logger.info("Pomyślnie zalogowano przy użyciu emaila")
                    return
                except Exception as e:
                    self.logger.error(f"Nie udało się zalogować przy użyciu emaila: {e}")
                    self.is_logged_in = False

            # Jeśli dotarliśmy tutaj, oznacza to, że nie udało się zalogować żadną metodą
            raise ValueError("Nie udało się zalogować żadną z dostępnych metod")

        except Exception as e:
            self.logger.error(f"Błąd podczas logowania: {e}")
            self.is_logged_in = False
            raise

    async def get_items(self, lat: float, lng: float, radius: int = 5) -> List[Dict[str, Any]]:
        """
        Pobiera dostępne paczki w określonej lokalizacji
        """
        try:
            items = self.client.get_items(
                favorites_only=False,
                latitude=lat,
                longitude=lng,
                radius=radius,
            )
            return items

        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania paczek: {e}")
            return []

    @staticmethod
    def format_item_info(item: Dict[str, Any]) -> str:
        """
        Formatuje informacje o paczce do czytelnej postaci
        """
        store = item.get("store", {})
        items_available = item.get("items_available", 0)
        price = item.get("item", {}).get("price_including_taxes", {})
        price_value = float(price.get("minor_units", 0)) / 100
        pickup_interval = item.get("pickup_interval", {})

        return (
            f"🏪 {store.get('store_name', 'Nieznany sklep')}\n"
            f"📍 {store.get('store_location', {}).get('address', {}).get('address_line', 'Brak adresu')}\n"
            f"💰 {price_value:.2f} PLN\n"
            f"📦 Dostępnych paczek: {items_available}\n"
            f"🕒 Odbiór: {pickup_interval.get('start')} - {pickup_interval.get('end')}\n"
        )

    async def cleanup(self):
        """
        Czyszczenie zasobów
        """
        pass
