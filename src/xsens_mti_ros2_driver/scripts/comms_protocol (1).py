"""
comms_protocol.py
-----------------
Shared low-level helpers for the Jetson <-> Raspberry Pi communication layer.

All messages are framed as:
    [4-byte big-endian length][UTF-8 JSON payload]

This ensures clean reads even when TCP delivers data in fragments.
"""

import json
import socket
import struct
import logging
from typing import Any

log = logging.getLogger(__name__)

# ── Network defaults (override via environment or pass explicitly) ──────────
JETSON_HOST = "192.168.1.10"   # Jetson's static IP on the Ethernet link
RPI_HOST    = "192.168.1.20"   # Raspberry Pi's static IP on the Ethernet link

GPS_PORT    = 5100   # RPi listens here for incoming GPS data from the Jetson
RESULT_PORT = 5101   # Jetson listens here for results / reposition signals

CONNECT_TIMEOUT = 10.0   # seconds – how long to wait when opening a connection
RECV_TIMEOUT    = 30.0   # seconds – how long to block on a single recv call

# ── Message type constants ──────────────────────────────────────────────────
MSG_GPS        = "GPS_DATA"       # Jetson → RPi: GPS fix
MSG_LOCATION   = "LOCATION"       # RPi → Jetson: survivor coordinates confirmed
MSG_REPOSITION = "REPOSITION"     # RPi → Jetson: scan insufficient, move and retry
MSG_ACK        = "ACK"            # Generic acknowledgement


# ── Framing helpers ─────────────────────────────────────────────────────────

def send_message(sock: socket.socket, payload: dict) -> None:
    """Serialise *payload* to JSON, prefix with a 4-byte length, and send."""
    data = json.dumps(payload).encode("utf-8")
    header = struct.pack(">I", len(data))
    sock.sendall(header + data)
    log.debug("Sent %s (%d bytes)", payload.get("type"), len(data))


def recv_message(sock: socket.socket) -> dict:
    """
    Block until a complete framed message arrives.

    Returns the decoded dict, or raises:
      - ConnectionError   if the peer closed the connection mid-stream
      - json.JSONDecodeError  if the payload is malformed
    """
    raw_len = _recv_exactly(sock, 4)
    msg_len = struct.unpack(">I", raw_len)[0]
    raw_body = _recv_exactly(sock, msg_len)
    payload = json.loads(raw_body.decode("utf-8"))
    log.debug("Received %s (%d bytes)", payload.get("type"), msg_len)
    return payload


def _recv_exactly(sock: socket.socket, n: int) -> bytes:
    """Read exactly *n* bytes from *sock*, handling partial TCP deliveries."""
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Connection closed before all bytes arrived")
        buf.extend(chunk)
    return bytes(buf)


# ── Convenience constructors ────────────────────────────────────────────────

def make_gps_message(lat: float, lon: float, heading: float,
                     altitude: float = 0.0, fix_quality: int = 1) -> dict:
    """Build a GPS_DATA message dict ready to pass to send_message()."""
    return {
        "type":        MSG_GPS,
        "latitude":    lat,
        "longitude":   lon,
        "heading":     heading,
    }


def make_location_message(lat: float, lon: float,
                          confidence: float = 1.0) -> dict:
    """Build a LOCATION result message (survivor's estimated position)."""
    return {
        "type":       MSG_LOCATION,
        "latitude":   lat,
        "longitude":  lon,
        "confidence": confidence,
    }


def make_reposition_message(reason: str = "Insufficient RF data") -> dict:
    """Build a REPOSITION signal telling the Jetson to move and retry."""
    return {
        "type":   MSG_REPOSITION,
        "reason": reason,
    }
