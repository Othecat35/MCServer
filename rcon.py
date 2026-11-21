import socket
import struct
import collections


class IncompletePacket(Exception):
    def __init__(self, minimum):
        self.minimum = minimum

Packet = collections.namedtuple("Packet", ("ident", "kind", "payload"))

rcon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def _send_packet(packet: Packet) -> None:
    global rcon_socket
    data = struct.pack("<ii", packet.ident, packet.kind) + packet.payload + b"\x00\x00"
    rcon_socket.sendall(struct.pack("<i", len(data)) + data)

def _receive_packet():
    global rcon_socket
    data = b""
    while True:
        try:
            return decode_packet(data)[0]
        except IncompletePacket as exc:
            while len(data) < exc.minimum:
                data += sock.recv(exc.minimum - len(data))


    if len(data) < 14:
        raise IncompletePacket(14)

    length = struct.unpack("<i", data[:4])[0] + 4
    if len(data) < length:
        raise IncompletePacket(length)

    ident, kind = struct.unpack("<ii", data[4:12])
    payload, padding = data[12:length-2], data[length-2:length]
    assert padding == b"\x00\x00"
    return Packet(ident, kind, payload), data[length:]



def login_rcon(rcon_password: str, rcon_ip: str = "127.0.0.1", rcon_port: int = 25575) -> :
    global rcon_socket
    rcon_socket.connect((rcon_ip, rcon_port))

def send_command(command_text: str) -> str:
    global rcon_socket
    return ""