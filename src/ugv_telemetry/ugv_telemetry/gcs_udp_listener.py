#!/usr/bin/env python3
"""Quick UDP listener to verify telemetry packets from telemetry_sub."""
import socket
import struct

PACKET_FORMAT = '<xx fffff 12x dd'
PORT = 5005


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', PORT))
    print(f'Listening for telemetry UDP on port {PORT}...\n')

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            if len(data) != 50:
                print(f'Unexpected packet size: {len(data)} bytes from {addr}')
                continue
            speed, pitch, yaw, roll, alt, lat, lon = struct.unpack(PACKET_FORMAT, data)
            print(
                f'From {addr[0]}:{addr[1]} | '
                f'Speed: {speed:.2f} ft/s | '
                f'Pitch: {pitch:.2f}° | '
                f'Yaw: {yaw:.2f}° | '
                f'Roll: {roll:.2f}° | '
                f'Alt: {alt:.2f} ft | '
                f'Lat: {lat:.6f} | '
                f'Lon: {lon:.6f}'
            )
    except KeyboardInterrupt:
        print('\nShutting down listener.')
    finally:
        sock.close()


if __name__ == '__main__':
    main()
