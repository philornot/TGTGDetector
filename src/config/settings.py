import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk, messagebox

from ..gui.styles import TGTGStyles


@dataclass
class Location:
    lat: float
    lng: float
    radius: int = 5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lat": self.lat,
            "lng": self.lng,
            "radius": self.radius
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        return cls(
            lat=float(data['lat']),
            lng=float(data['lng']),
            radius=int(data.get('radius', 5))
        )


class TGTGSettings:
    """Zarządzanie ustawieniami aplikacji"""

    DEFAULT_CONFIG = {
        "refresh_interval": 30,
        "locations": [
            {
                "lat": 52.2297,
                "lng": 21.0122,
                "radius": 5
            }
        ],
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
        self.config_dir = Path.home() / "Dokumenty" / "TGTG Detector"
        self.config_path = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Wczytuje konfigurację z pliku"""
        if not self.config_path.exists():
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Upewnij się, że wszystkie wymagane pola są obecne
                return {**self.DEFAULT_CONFIG, **config}
        except Exception as e:
            raise ValueError(f"Błąd podczas wczytywania konfiguracji: {e}")

    def save_config(self, config: Dict[str, Any]):
        """Zapisuje konfigurację do pliku"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.config = config
        except Exception as e:
            raise ValueError(f"Błąd podczas zapisywania konfiguracji: {e}")

    def get_location(self, index: int = 0) -> Optional[Location]:
        """Pobiera lokalizację o danym indeksie"""
        locations = self.config.get('locations', [])
        if index < len(locations):
            return Location.from_dict(locations[index])
        return None

    def update_credentials(self, credentials: Dict[str, str]):
        """Aktualizuje dane uwierzytelniające"""
        self.config.update({
            "access_token": credentials.get("access_token", ""),
            "refresh_token": credentials.get("refresh_token", ""),
            "user_id": credentials.get("user_id", ""),
            "cookie": credentials.get("cookie", "")
        })
        self.save_config(self.config)


class SettingsWindow:
    """Okno konfiguracji aplikacji"""

    def __init__(self, parent=None):
        self.settings = TGTGSettings()

        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("TGTG Detector - Ustawienia")
        self.window.geometry("600x400")

        TGTGStyles.apply_dark_theme(self.window)
        self._create_widgets()
        self._center_window()

    def _create_widgets(self):
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Zakładka Ogólne
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="Ogólne")

        # Interwał odświeżania
        ttk.Label(general_frame, text="Interwał odświeżania (sekundy):").pack(anchor=tk.W)
        self.refresh_var = tk.StringVar(value=str(self.settings.config['refresh_interval']))
        refresh_entry = ttk.Entry(general_frame, textvariable=self.refresh_var)
        refresh_entry.pack(fill=tk.X)

        # Lokalizacja
        ttk.Label(general_frame, text="Lokalizacja:").pack(anchor=tk.W, pady=(10, 0))
        location = self.settings.get_location(0)

        location_frame = ttk.Frame(general_frame)
        location_frame.pack(fill=tk.X)

        # Szerokość geograficzna
        self.lat_var = tk.StringVar(value=str(location.lat if location else ""))
        ttk.Label(location_frame, text="Szerokość:").pack(side=tk.LEFT)
        ttk.Entry(location_frame, textvariable=self.lat_var, width=15).pack(side=tk.LEFT, padx=5)

        # Długość geograficzna
        self.lng_var = tk.StringVar(value=str(location.lng if location else ""))
        ttk.Label(location_frame, text="Długość:").pack(side=tk.LEFT)
        ttk.Entry(location_frame, textvariable=self.lng_var, width=15).pack(side=tk.LEFT, padx=5)

        # Promień
        self.radius_var = tk.StringVar(value=str(location.radius if location else "5"))
        ttk.Label(location_frame, text="Promień (km):").pack(side=tk.LEFT)
        ttk.Entry(location_frame, textvariable=self.radius_var, width=5).pack(side=tk.LEFT, padx=5)

        # Przycisk zapisz
        ttk.Button(
            self.window,
            text="Zapisz",
            command=self._save_settings
        ).pack(side=tk.RIGHT, padx=10, pady=10)

    def _center_window(self):
        """Centruje okno na ekranie"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def _save_settings(self):
        """Zapisuje ustawienia"""
        try:
            self.settings.config['refresh_interval'] = int(self.refresh_var.get())
            self.settings.config['locations'] = [{
                "lat": float(self.lat_var.get()),
                "lng": float(self.lng_var.get()),
                "radius": int(self.radius_var.get())
            }]

            self.settings.save_config(self.settings.config)
            messagebox.showinfo("Sukces", "Ustawienia zostały zapisane")

        except ValueError as e:
            messagebox.showerror("Błąd", f"Nieprawidłowe wartości: {str(e)}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas zapisywania ustawień: {str(e)}")

    def run(self):
        """Uruchamia okno ustawień"""
        self.window.mainloop()


if __name__ == "__main__":
    app = SettingsWindow()
    app.run()