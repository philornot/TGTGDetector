import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path
from tgtg import TgtgClient


class CredentialsWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TGTG Detector - Generator Credentiali")
        self.root.geometry("400x300")

        # Konfiguracja styli
        self.style = ttk.Style()
        self.style.configure('TButton', padding=5)
        self.style.configure('TLabel', padding=5)
        self.style.configure('TEntry', padding=5)

        self._create_widgets()
        self._center_window()

    def _create_widgets(self):
        # Frame główny
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Etykieta i pole email
        ttk.Label(main_frame, text="Podaj email z TGTG:").pack(fill=tk.X)
        self.email_var = tk.StringVar()
        email_entry = ttk.Entry(main_frame, textvariable=self.email_var)
        email_entry.pack(fill=tk.X, pady=5)

        # Przyciski
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=20)

        ttk.Button(
            btn_frame,
            text="Generuj credentials",
            command=self._generate_credentials
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Zamknij",
            command=self.root.quit
        ).pack(side=tk.RIGHT, padx=5)

        # Status
        self.status_var = tk.StringVar(value="Oczekiwanie...")
        status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            wraplength=350
        )
        status_label.pack(fill=tk.X, pady=10)

    def _center_window(self):
        """Centruje okno na ekranie"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def _generate_credentials(self):
        """Generuje credentials i zapisuje je do pliku"""
        email = self.email_var.get().strip()
        if not email:
            messagebox.showerror("Błąd", "Podaj adres email!")
            return

        try:
            self.status_var.set("Generowanie credentiali... Sprawdź email!")
            self.root.update()

            client = TgtgClient(email=email)
            credentials = client.get_credentials()

            # Przygotuj config
            config_dir = Path.home() / "Dokumenty" / "TGTG Detector"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_path = config_dir / "config.json"

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

            self.status_var.set(
                "Credentials wygenerowane i zapisane w config.json!\n"
                "Możesz teraz uruchomić główny program."
            )
            messagebox.showinfo(
                "Sukces",
                "Credentials zostały zapisane w pliku config.json"
            )

        except Exception as e:
            self.status_var.set(f"Błąd: {str(e)}")
            messagebox.showerror("Błąd", f"Wystąpił błąd: {str(e)}")

    def run(self):
        """Uruchamia aplikację"""
        self.root.mainloop()


if __name__ == "__main__":
    app = CredentialsWindow()
    app.run()