# QuickDesk

**IoT-Based Dynamic Wi-Fi Credential Management System using Raspberry Pi**

QuickDesk is a prototype concept for sharing an Ethernet internet connection through a Wi-Fi hotspot while periodically rotating hotspot credentials. The interface is intended to show the SSID, current password, QR code, and countdown.

## Project contents

- `main.py` — illustrative Python prototype
- `docs/Annexure.md` — annexure and implementation snippets
- `requirements.txt` — Python package requirements

## Requirements

- Raspberry Pi OS
- Python 3
- A configured Wi-Fi interface (the example uses `wlan0`)
- Ethernet uplink
- `hostapd` and `dnsmasq`
- Tkinter and Pillow

Install system packages:

```bash
sudo apt update
sudo apt install hostapd dnsmasq python3-tk python3-pil python3-pil.imagetk
```

Install Python package:

```bash
python3 -m pip install -r requirements.txt
```

## Important configuration and security notes

1. Review the interface name, channel, country settings, hostapd path, and network routing before use.
2. The sample rewrites a basic hostapd configuration. Adapt it to your existing setup; overwriting configuration may disrupt networking.
3. The example invokes `sudo` for configuration installation and service restarts. It requires authorization. Do not enable unrestricted passwordless sudo. Prefer a dedicated, restricted service or helper with validated inputs.
4. Rotating the password and restarting the access point can disconnect clients.
5. Treat the displayed password and QR code as sensitive. Do not commit actual credentials, private keys, logs, or network configuration.
6. Test on a device and network you administer. The code is a prototype, not a hardened production hotspot manager.

## Run

On a properly configured Raspberry Pi, from this project directory:

```bash
python3 main.py
```

Run only after reviewing the configuration and privilege requirements above.

## Testing checklist

- Verify hotspot initialization and Ethernet internet sharing.
- Connect a client using the active credentials.
- Confirm QR code data matches the active password.
- Verify rotation and timer behavior.
- Check client reconnection and service logs.
- Record connection delay, throughput, and multi-client behavior.

## Repository layout

```text
QuickDesk/
├── docs/
│   └── Annexure.md
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```
