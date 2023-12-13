import argparse
import struct

from enum import Enum
from collections import Counter
from pathlib import Path
from scapy.all import *


class DESCRIPTOR_TYPE(Enum):
    DEVICE = 0x01
    CONFIGURATION = 0x02
    STRING = 0x03
    INTERFACE = 0x04
    ENDPOINT = 0x05
    DEVICE_QUALIFIER = 0x06
    INTERFACE_ASSOCIATION = 0x0b
    HID = 0x21
    HID_REPORT = 0x22
    VIDEO_CONTROL_INTERFACE = 0x24
    VIDEO_CONTROL_ENDPOINT = 0x25
    VIDEO_STILL_IMAGE_FRAME = 0x26
    SUPER_SPEED_ENDPOINT_COMPANION = 0x30


class INTERFACE_PROTOCOL(Enum):
    UNKNOWN = 0x00
    KEYBOARD = 0x01
    MOUSE = 0x02
    BULK_ONLY_TRANSPORT = 0x50
    UNKNOWN_2 = 0xff


class TRANSFER_TYPE(Enum):
    ISOCHRONOUS = 0x00
    INTERRUPT = 0x01
    CONTROL = 0x02
    BULK = 0x03


class EVENT_TYPE(Enum):
    SUBMIT = ord('S')  # Transfer begins
    COMPLETE = ord('C')  # Transfer completes
    ERROR = ord('E')


class DIRECTION(Enum):
    OUT = 0x00
    IN = 0x01


class REQUEST_TYPE(Enum):
    GET_STATUS = 0x00
    CLEAR_FEATURE = 0x01
    SET_FEATURE = 0x03
    SET_ADDRESS = 0x05
    GET_DESCRIPTOR = 0x06
    GET_CONFIGURATION = 0x08
    SET_REPORT = 0x09
    SET_IDLE = 0x0A
    SET_INTERFACE = 0x0B


class USB_URB:
    def __init__(self, urb_id, transfer_type, endpoint_address, device_address, bus_id, data_len, direction, extra_data):
        self.id = urb_id
        self.transfer_type = TRANSFER_TYPE(transfer_type)
        self.endpoint_number = endpoint_address & 0x7F
        self.device_address = device_address
        self.bus_id = bus_id
        self.data_len = data_len
        self.direction = direction
        self.extra_data = extra_data
    
    def has_hid_data(self):
        return (self.data_len > 0 and
                self.transfer_type == TRANSFER_TYPE.INTERRUPT and
                self.direction == DIRECTION.IN)

    def get_address(self):
        return f'{self.bus_id}.{self.device_address}.{self.endpoint_number}'


class USB_URB_1(USB_URB):
    def __init__(self, packet):
        (self.header_len,
        self.irp_id,
        self.usbd_status,
        self.function,
        self.irp_info,
        self.bus_id,
        self.device_address,
        self.endpoint_address,
        self.transfer_type,
        self.data_len) = struct.unpack('<HQIHBHHBBI', packet[:27])
        if self.header_len == 28:
            self.control_stage = packet[27]

        self.direction = DIRECTION(self.irp_info & 0x01)
        self.setup_data = packet[self.header_len:]

        super().__init__(
            self.irp_id,
            self.transfer_type,
            self.endpoint_address,
            self.device_address,
            self.bus_id,
            self.data_len,
            self.direction,
            packet[self.header_len:]
        )


class USB_URB_2(USB_URB):
    def __init__(self, packet):
        (self.urb_id,
        self.urb_type,
        self.transfer_type,
        self.endpoint_address,
        self.device_address,
        self.bus_id,
        self.setup_flag,
        self.data_flag,
        self.urb_ts_sec,
        self.urb_ts_usec,
        self.urb_status,
        self.urb_len,
        self.data_len,
        self.setup_data,
        self.interval,
        self.start_frame,
        self.copy_of_transfer_flags,
        self.iso_numdesc) = struct.unpack('<QBBBBHBBQIIIIQIIII', packet[:64])

        self.direction = DIRECTION(self.endpoint_address & 0x80 >> 7)
        self.urb_type = EVENT_TYPE(self.urb_type)
        self.setup_data_relevant = self.setup_flag == 0
        self.data_present = self.data_flag == 0
        self.setup_data = struct.pack('<Q', self.setup_data)

        super().__init__(
            self.urb_id,
            self.transfer_type,
            self.endpoint_address,
            self.device_address,
            self.bus_id,
            self.data_len,
            self.direction,
            packet[64:]
        )

    def __str__(self):
        out = ''
        out += f'URB id: {hex(self.urb_id)}\n'
        out += f'URB type: {self.urb_type}\n'
        out += f'URB transfer type: {self.transfer_type}\n'
        out += f'Endpoint: {self.endpoint_address}\n'
        out += f'\tDirection: {self.direction}\n'
        out += f'\tEndpoint number: {self.endpoint_number}\n'
        out += f'Device: {self.device_address}\n'
        out += f'URB bus id: {self.bus_id}\n'
        out += f'Device setup request: {"not" if not self.setup_data_relevant else ""} relevant ({self.setup_flag})\n'
        out += f'Data: {"not" if not self.data_present else ""} present ({self.data_flag})\n'
        out += f'URB timestamp: {self.urb_ts_sec}.{self.urb_ts_usec}\n'
        out += f'URB status: {self.urb_status}\n'
        out += f'URB length: {self.urb_len}\n'
        out += f'Data length: {self.data_len}\n'
        if not self.setup_data_relevant:
            out += f'Unused Setup Header\n'
        out += f'Interval: {self.interval}\n'
        out += f'Start frame: {self.start_frame}\n'
        out += f'Copy of transfer flags: {"0x" + hex(self.copy_of_transfer_flags)[2:].zfill(8)}\n'
        out += f'Number of ISO descriptors: {self.iso_numdesc}\n'
        if self.data_len > 0:
            out += f'Extra data: {self.extra_data.hex()}\n'
        return out


def get_devices(packets: [USB_URB]) -> dict:
    devices = {}
    descriptor_requests = []
    for packet in packets:
        if packet.transfer_type != TRANSFER_TYPE.CONTROL:
            continue
        
        if packet.direction == DIRECTION.OUT:
            # Get descriptor requests
            bRequest = REQUEST_TYPE(packet.setup_data[1])
            if bRequest != REQUEST_TYPE.GET_DESCRIPTOR:
                continue
            
            try:
                bDescriptorType = DESCRIPTOR_TYPE(packet.setup_data[3])
            except ValueError:
                continue

            if bDescriptorType != DESCRIPTOR_TYPE.CONFIGURATION:
                continue
            descriptor_requests.append(packet.id)
            continue

        # Get descriptor responses
        if packet.id not in descriptor_requests:
            continue
        descriptor_requests.remove(packet.id)

        i = 0
        current_device = None
        while i < packet.data_len:
            bLength = packet.extra_data[i]
            bDescriptorType = DESCRIPTOR_TYPE(packet.extra_data[i + 1])

            if bDescriptorType == DESCRIPTOR_TYPE.INTERFACE:
                current_device = INTERFACE_PROTOCOL(packet.extra_data[i + 7])
            elif bDescriptorType == DESCRIPTOR_TYPE.ENDPOINT:
                bEndpointNumber = packet.extra_data[i + 2] & 0x7F
                addr = f'{packet.bus_id}.{packet.device_address}.{bEndpointNumber}'
                devices[addr] = {
                    'device': current_device.name.lower(),
                    'data': []
                }
            i += bLength

    return devices


def extract_hid_data(packets: [USB_URB], devices: dict) -> dict:
    for packet in packets:
        if not packet.has_hid_data():
            continue

        addr = packet.get_address()
        if addr not in devices:
            devices[addr] = {
                'device': 'unknown',
                'data': []
            }
        devices[addr]['data'].append(packet.extra_data)

    return {addr: info for addr, info in devices.items() if len(info['data']) > 0}


def extract_data(filename: str) -> dict:
    try:
        pcap = rdpcap(filename)
    except Scapy_Exception:
        print('File is not in PCAP format, assuming raw hex data..')
        try:
            with open(filename) as f:
                return {
                    '0.0.0': {
                        'device': 'unknown',
                        'data': [bytes.fromhex(line) for line in f]
                    }
                }
        except ValueError:
            print('File is not in hex format, exiting...')
            exit()

    usb_packets = []
    for packet in pcap:
        data = bytes(packet)
        try:
            if len(data) >= 64:
                try:
                    usb_packets.append(USB_URB_2(data))
                except ValueError:
                    usb_packets.append(USB_URB_1(data))
            else:
                usb_packets.append(USB_URB_1(data))
        except ValueError:
            continue

    devices = get_devices(usb_packets)
    return extract_hid_data(usb_packets, devices)


def write_results(hid_data: dict, output_folder: str):
    out = Path(output_folder)
    if not out.exists():
        out.mkdir()
    elif not out.is_dir():
        print(f'Output path {output_folder} exists but is not a directory, exiting...')
        exit()

    for addr, info in hid_data.items():
        print(f'Found HID data for {info["device"]} device at {addr}, writing to {output_folder}...')
        with open(f'{output_folder}/{info["device"]}-{addr}.txt', 'w') as f:
            for line in info['data']:
                f.write(line.hex() + '\n')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Extract and/or pre-process HID data',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('file', help='input file (pcap or hex data)')
    parser.add_argument('-o', '--output', default='output', help='output folder (default \'%(default)s\')')
    return parser.parse_args()


def main():
    args = parse_args()
    hid_data = extract_data(args.file)
    write_results(hid_data, args.output)


if __name__ == '__main__':
    main()
