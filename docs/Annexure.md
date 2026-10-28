# ANNEXURE
# QuickDesk – Dynamic Wi-Fi Credential Management System

This annexure contains organized implementation snippets for the QuickDesk Raspberry Pi hotspot system. These are reference snippets and should be integrated and tested with the project's actual network configuration before deployment.

## A. Required Libraries and Packages

```bash
sudo apt update
sudo apt install hostapd dnsmasq python3-tk python3-pil python3-pil.imagetk
python3 -m pip install qrcode[pil]
```

## B. Dynamic Password Generator

This function creates an 8-character alphanumeric password. For production use, prefer Python's `secrets` module instead of `random`.

```python
import secrets
import string

def generate_password(length=8):
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))
```

## C. Wi-Fi QR Code Generator

```python
import qrcode

def generate_qr(ssid, password, filename="wifi_qr.png"):
    wifi_data = f"WIFI:T:WPA;S:{ssid};P:{password};;"
    qr = qrcode.make(wifi_data)
    qr.save(filename)
    return filename
```

## D. Update the hostapd Configuration

This example writes SSID and passphrase to hostapd. Verify the configuration path and preserve settings required by your installation.

```python
from pathlib import Path

HOSTAPD_CONFIG = Path("/etc/hostapd/hostapd.conf")

def update_wifi_password(new_password, ssid="Quick"):
    config = f"""\
interface=wlan0
driver=nl80211
ssid={ssid}
hw_mode=g
channel=6
wpa=2
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
wpa_passphrase={new_password}
"""
    HOSTAPD_CONFIG.write_text(config, encoding="utf-8")
```

**Note:** This direct-write example is simplified. Validate inputs, protect the configuration file, and avoid embedding real credentials in source control.

## E. Restart Hotspot Services

```python
import subprocess

def restart_hotspot():
    subprocess.run(["sudo", "systemctl", "restart", "hostapd"], check=True)
    subprocess.run(["sudo", "systemctl", "restart", "dnsmasq"], check=True)
```

The Python process needs an appropriately configured privilege policy. Avoid unrestricted passwordless sudo.

## F. Countdown and Credential Rotation

Use Tkinter's `after()` callback rather than `time.sleep()`, which blocks the interface. This example assumes the helper functions above are configured and authorized.

```python
import tkinter as tk
from PIL import Image, ImageTk

SSID = "Quick"
ROTATION_SECONDS = 120

root = tk.Tk()
root.title("QuickDesk")

tk.Label(root, text=f"SSID: {SSID}").pack()
password_label = tk.Label(root, text="Password: —")
password_label.pack()
timer_label = tk.Label(root, text="")
timer_label.pack()
qr_label = tk.Label(root)
qr_label.pack()

current_password = None
qr_photo = None

def refresh_qr(password):
    global qr_photo
    qr_path = generate_qr(SSID, password)
    image = Image.open(qr_path)
    qr_photo = ImageTk.PhotoImage(image)
    qr_label.config(image=qr_photo)

def countdown(remaining):
    timer_label.config(text=f"Time Left: {remaining}s")
    if remaining <= 0:
        rotate_credentials()
    else:
        root.after(1000, lambda: countdown(remaining - 1))

def rotate_credentials():
    global current_password
    new_password = generate_password()
    try:
        update_wifi_password(new_password, SSID)
        restart_hotspot()
        current_password = new_password
        password_label.config(text=f"Password: {current_password}")
        refresh_qr(current_password)
        countdown(ROTATION_SECONDS)
    except Exception as exc:
        timer_label.config(text=f"Credential update failed: {exc}")
        root.after(5000, rotate_credentials)

root.after(0, rotate_credentials)
root.mainloop()
```

**Implementation notes:**
- This is an illustrative integration, not a deployment-ready service.
- Restarting services may disconnect active clients.
- Confirm that the QR code, displayed password and active hotspot credentials stay synchronized.
- A failed restart requires robust recovery and verification; this example reports an error and retries.
- Protect the display and logs because credentials are sensitive.
- Use a dedicated least-privilege service design for production.

## G. Functional Testing Checklist

1. Verify hotspot initialization.
2. Confirm clients can connect using current credentials.
3. Check that the QR code contains the active credentials.
4. Verify countdown and rotation interval.
5. Confirm updates reach the hotspot configuration.
6. Test client reconnection after rotation.
7. Record errors and connectivity interruptions.

## H. Project Dependencies

- Raspberry Pi OS
- Python 3
- hostapd
- dnsmasq
- qrcode
- Pillow
- Tkinter
- Ethernet internet connection
- Wi-Fi interface (`wlan0`, subject to device configuration)
