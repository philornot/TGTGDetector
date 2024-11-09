from typing import Optional, List, Dict, Any

from tgtg import TgtgClient

from ..config import TGTGSettings
from ..utils import TGTGLogger


class TGTGApiClient:
    """
    Klient API dla Too Good To Go
    """

    def __init__(self):
        self.logger = TGTGLogger("TGTG_API").get_logger()
        self.client = None
        self.settings = TGTGSettings()

    async def login(self, email: str, access_token: Optional[str] = None):
        """
        Logowanie do TGTG
        """
        self.logger.info("Rozpoczynam proces logowania...")

        try:
            config = self.settings.config

            # Jeśli już mamy klienta, nie logujemy się ponownie
            if self.client is not None:
                self.logger.info("Używam istniejącej sesji")
                return

            if access_token and config.get('refresh_token') and config.get('user_id') and config.get('cookie'):
                self.logger.debug("Próba logowania przy użyciu zapisanych credentials...")
                self.client = TgtgClient(
                    access_token=config['access_token'],
                    refresh_token=config['refresh_token'],
                    user_id=config['user_id'],
                    cookie=config['cookie']
                )
                self.logger.info("Zalogowano przy użyciu zapisanych credentials")
            else:
                self.logger.debug("Brak zapisanych credentials, inicjalizacja nowego klienta...")
                self.client = TgtgClient(email=email)
                credentials = self.client.get_credentials()
                self.settings.update_credentials(credentials)
                self.logger.info("Logowanie zakończone sukcesem")

        except Exception as e:
            self.logger.error(f"Błąd podczas logowania: {e}")
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
