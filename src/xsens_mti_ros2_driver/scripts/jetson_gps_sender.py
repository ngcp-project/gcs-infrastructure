"""
jetson_gps_sender.py
--------------------
Runs on the **Jetson**.
"""

import logging
import socket
import time

from comms_protocol import (
    CONNECT_TIMEOUT,
    GPS_PORT,
    RPI_HOST,
    make_gps_message,
    recv_message,
    send_message,
    MSG_ACK,
)

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [JETSON-SENDER] %(levelname)s %(message)s",
)


# ── GPS acquisition ─────────────────────────────────────────────────────────

def read_gps_fix() -> dict:

    # ── STUB: replace with real GPS driver ──────────────────────────────────
    # import random
    coords = []
    with open('ntrip_coords.txt', 'r') as f:
        for line in f:
            lat, lon, z = map(float, line.strip().split(','))
    coords.append({
        "latitude":  lat,
        "longitude": lon,
        "heading":  z ,
    })
    print(coords)
    # log.info(
    #    "GPS fix: lat=%.6f lon=%.6f heading=%.1f°",
    #   fix["latitude"], fix["longitude"], fix["heading"],
    # )
    # return fix
    # ── END STUB ─────────────────────────────────────────────────────────────


# ── Transmission ─────────────────────────────────────────────────────────────

def send_gps_to_rpi(
    host: str = RPI_HOST,
    port: int = GPS_PORT,
    retries: int = 3,
    retry_delay: float = 2.0,
) -> bool:
    """
    Read the current GPS fix and send it to the Raspberry Pi.

    Parameters
    ----------
    host        : RPi's IP address on the Ethernet link.
    port        : TCP port the RPi GPS server is listening on.
    retries     : Number of connection attempts before giving up.
    retry_delay : Seconds to wait between retries.

    Returns True on successful delivery (RPi sent ACK), False otherwise.
    """
    fix = read_gps_fix()
    message = make_gps_message(
        lat=fix["latitude"],
        lon=fix["longitude"],
        heading=fix["heading"],
    )

    for attempt in range(1, retries + 1):
        try:
            log.info("Connecting to RPi at %s:%d (attempt %d/%d)", host, port, attempt, retries)
            with socket.create_connection((host, port), timeout=CONNECT_TIMEOUT) as sock:
                sock.settimeout(10.0)
                send_message(sock, message)
                log.info("GPS data sent — waiting for ACK")

                ack = recv_message(sock)
                if ack.get("type") == MSG_ACK:
                    log.info("ACK received from RPi")
                    return True
                else:
                    log.warning("Unexpected response: %s", ack)

        except (ConnectionRefusedError, TimeoutError, OSError) as exc:
            log.warning("Connection attempt %d failed: %s", attempt, exc)
            if attempt < retries:
                time.sleep(retry_delay)

    log.error("Failed to deliver GPS data after %d attempts", retries)
    return False


# ── Standalone entry point ───────────────────────────────────────────────────

if __name__ == "__main__":
    success = send_gps_to_rpi()
    if not success:
        raise SystemExit("GPS transmission failed")
