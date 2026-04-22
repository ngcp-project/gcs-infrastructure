"""
jetson_result_listener.py
-------------------------
Runs on the **Jetson**.

This module owns only the Jetson-side communication loop:
  1. Send GPS to the Raspberry Pi.
  2. Wait for the Pi to send back either LOCATION or REPOSITION.
  3. Forward that received message to the appropriate Jetson-side subsystem.
"""

from __future__ import annotations

import logging
import socket
import threading
import time
from typing import Callable, Optional

from comms_protocol import (
    MSG_ACK,
    MSG_LOCATION,
    MSG_REPOSITION,
    RECV_TIMEOUT,
    RESULT_PORT,
    recv_message,
    send_message,
)
from jetson_gps_sender import send_gps_to_rpi

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [JETSON-LISTENER] %(levelname)s %(message)s",
)

SCAN_WINDOW_SECONDS = 240.0
MAX_SCAN_ATTEMPTS = 10


class ResultServer:
    """Accept one callback message from the Raspberry Pi and ACK it."""

    def __init__(self, port: int = RESULT_PORT, timeout: float = RECV_TIMEOUT):
        self.port = port
        self.timeout = timeout
        self._ready = threading.Event()

    def wait_for_result(self) -> Optional[dict]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("0.0.0.0", self.port))
            srv.listen(1)
            srv.settimeout(self.timeout)
            log.info("Listening for Pi result on port %d", self.port)
            self._ready.set()

            try:
                conn, addr = srv.accept()
                log.info("Pi connected from %s", addr)
            except TimeoutError:
                log.error("Timed out waiting for Pi result message")
                return None

            with conn:
                conn.settimeout(self.timeout)
                try:
                    msg = recv_message(conn)
                    send_message(conn, {"type": MSG_ACK})
                    return msg
                except Exception as exc:
                    log.error("Failed to receive/ack result message: %s", exc)
                    return None

    def wait_until_ready(self, timeout: float = 5.0) -> bool:
        return self._ready.wait(timeout)


def deliver_location(location_msg: dict) -> None:
    """Forward a confirmed survivor location to the next Jetson-side subsystem."""
    payload = {
        "latitude": location_msg["latitude"],
        "longitude": location_msg["longitude"],
        "confidence": location_msg.get("confidence", 1.0),
    }
    log.info(
        "Forward survivor location: lat=%.6f lon=%.6f conf=%.2f",
        payload["latitude"],
        payload["longitude"],
        payload["confidence"],
    )
    # Replace this stub with your actual interface handoff.


def notify_reposition_requested(result_msg: dict, attempt: int) -> None:
    """Forward the Pi's retry/reposition signal without commanding motion."""
    reason = result_msg.get("reason", "Insufficient RF data")
    signal = {
        "event": "REPOSITION_REQUIRED",
        "reason": reason,
        "attempt": attempt + 1,
    }
    log.info("Forward reposition request: %s", signal)
    # Replace this stub with your actual interface handoff.


def wait_for_single_result(result_port: int = RESULT_PORT, timeout: float = RECV_TIMEOUT) -> Optional[dict]:
    """Utility for integrations that only need to receive one Pi result message."""
    server = ResultServer(port=result_port, timeout=timeout)
    return server.wait_for_result()


def run_scan_loop(
    result_port: int = RESULT_PORT,
    window_seconds: float = SCAN_WINDOW_SECONDS,
    on_location: Optional[Callable[[dict], None]] = None,
    on_reposition_request: Optional[Callable[[dict, int], None]] = None,
) -> Optional[dict]:
    """
    Run the Jetson communication loop.

    Each attempt:
      - start the Jetson result listener
      - send fresh GPS to the Pi
      - wait for LOCATION or REPOSITION

    Returns the LOCATION message on success, otherwise None if the time window
    expires.
    """
    if on_location is None:
        on_location = deliver_location
    if on_reposition_request is None:
        on_reposition_request = notify_reposition_requested

    deadline = time.monotonic() + window_seconds
    attempt = 0

    while time.monotonic() < deadline and attempt < MAX_SCAN_ATTEMPTS:
        remaining = deadline - time.monotonic()
        log.info("-- Scan attempt %d | %.0fs remaining --", attempt + 1, remaining)

        server = ResultServer(port=result_port, timeout=min(RECV_TIMEOUT, max(1.0, remaining)))
        holder: dict[str, Optional[dict]] = {"message": None}

        def _listen() -> None:
            holder["message"] = server.wait_for_result()

        thread = threading.Thread(target=_listen, daemon=True, name=f"jetson-result-{attempt}")
        thread.start()

        if not server.wait_until_ready():
            log.error("Result listener was not ready in time")
            return None

        if not send_gps_to_rpi():
            log.warning("GPS transmission failed on attempt %d", attempt + 1)
            attempt += 1
            continue

        thread.join(timeout=min(RECV_TIMEOUT, max(1.0, remaining)) + 5.0)
        result = holder["message"]
        if result is None:
            log.warning("No Pi result received on attempt %d", attempt + 1)
            attempt += 1
            continue

        msg_type = result.get("type")
        if msg_type == MSG_LOCATION:
            on_location(result)
            return result
        if msg_type == MSG_REPOSITION:
            on_reposition_request(result, attempt)
            attempt += 1
            continue

        log.warning("Unexpected result type from Pi: %s", msg_type)
        attempt += 1

    log.error("No confirmed location received before the scan window expired")
    return None


if __name__ == "__main__":
    outcome = run_scan_loop()
    raise SystemExit(0 if outcome else 1)
