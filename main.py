"""
QuickDesk - Dynamic Wi-Fi Credential Management System
Illustrative Raspberry Pi prototype.

Before running:
- Configure hostapd and dnsmasq for your Raspberry Pi.
- Review HOSTAPD_CONFIG and wireless interface.
- Configure a restricted, least-privilege way to update hostapd and restart services.
- Do not commit real passwords or sensitive configuration.
"""

import secrets
import string
import subprocess
import tempfile
import tkinter as tk
from pathlib import Path

import qrcode
from PIL import Image, ImageTk

SSID = "Quick"
ROTATION_SECONDS = 120
HOSTAPD_CONFIG = Path("/etc/hostapd/hostapd.conf")
QR_FILE = Path("wifi_qr.png")


def generate_password(length=8):
    """Generate an 8-character uppercase alphanumeric password."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_qr(ssid, password, filename=QR_FILE):
    """Generate a QR code for WPA/WPA2 Wi-Fi connection."""
    wifi_data = f"WIFI:T:WPA;S:{ssid};P:{password};;"
    qrcode.make(wifi_data).save(filename)
    return Path(filename)


def build_hostapd_config(password, ssid=SSID):
    """Build a basic hostapd configuration; adapt to your network setup."""
    return f"""interface=wlan0
driver=nl80211
ssid={ssid}
hw_mode=g
channel=6
wpa=2
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
wpa_passphrase={password}
"""


def update_wifi_password(password, ssid=SSID):
    """
    Write a staged config and install it with sudo.
    This requires authorization and is not a substitute for a
    carefully configured, restricted service/privilege policy.
    """
    content = build_hostapd_config(password, ssid)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".conf", delete=False
    ) as staged:
        staged.write(content)
        staged_path = Path(staged.name)

    try:
        subprocess.run(
            ["sudo", "install", "-m", "600", str(staged_path),
             str(HOSTAPD_CONFIG)],
            check=True,
        )
    finally:
        staged_path.unlink(missing_ok=True)


def restart_hotspot():
    """Restart network services; this may disconnect current clients."""
    subprocess.run(
        ["sudo", "systemctl", "restart", "hostapd"], check=True
    )
    subprocess.run(
        ["sudo", "systemctl", "restart", "dnsmasq"], check=True
    )


class QuickDeskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickDesk")
        self.root.geometry("360x500")

        self.password_label = tk.Label(root, text="Password: initializing…")
        self.password_label.pack(pady=8)

        self.ssid_label = tk.Label(root, text=f"SSID: {SSID}")
        self.ssid_label.pack(pady=8)

        self.timer_label = tk.Label(root, text="Countdown: —")
        self.timer_label.pack(pady=8)

        self.qr_label = tk.Label(root)
        self.qr_label.pack(pady=12)

        self.status_label = tk.Label(root, text="Starting…", wraplength=330)
        self.status_label.pack(pady=8)

        self.qr_photo = None
        self.password = None
        self.root.after(300, self.rotate_credentials)

    def show_qr(self, password):
        qr_path = generate_qr(SSID, password)
        image = Image.open(qr_path)
        image.thumbnail((220, 220))
        self.qr_photo = ImageTk.PhotoImage(image)
        self.qr_label.config(image=self.qr_photo)

    def rotate_credentials(self):
        new_password = generate_password()
        self.status_label.config(text="Updating hotspot credentials…")
        try:
            update_wifi_password(new_password)
            restart_hotspot()
            self.show_qr(new_password)
        except (OSError, subprocess.CalledProcessError) as error:
            self.status_label.config(
                text=f"Update failed. Check service/configuration: {error}"
            )
            self.root.after(5000, self.rotate_credentials)
            return

        self.password = new_password
        self.password_label.config(text=f"Password: {self.password}")
        self.status_label.config(text="Credentials updated.")
        self.update_countdown(ROTATION_SECONDS)

    def update_countdown(self, remaining):
        self.timer_label.config(text=f"Countdown: {remaining}s")
        if remaining <= 0:
            self.rotate_credentials()
        else:
            self.root.after(
                1000, lambda: self.update_countdown(remaining - 1)
            )


if __name__ == "__main__":
    app_root = tk.Tk()
    QuickDeskApp(app_root)
    app_root.mainloop()
