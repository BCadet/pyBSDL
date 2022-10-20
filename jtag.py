#!/usr/bin/env python3
from os import environ
from pyftdi.jtag import JtagEngine
from pyftdi.ftdi import Ftdi
from pyftdi.bits import BitSequence

import bsdl
import bsdlJson
import binascii

from bsdl_fetcher import bsdl_fetcher

class BsdlSemantics:
    def map_string(self, ast):
        parser = bsdl.bsdlParser()
        ast = parser.parse(''.join(ast), "port_map")
        return ast

    def grouped_port_identification(self, ast):
        parser = bsdl.bsdlParser()
        ast = parser.parse(''.join(ast), "group_table")
        return ast

def get_bit_settings(bit_state_dict, boundary_reg):
    byte_array = list(boundary_reg)

    for bit in bit_state_dict.keys():
        # byte_index = bit // 8
        # byte = 1 << (bit % 8)
        if bit_state_dict[bit] == 1:
            byte_array[bit] = 1
        else:
            byte_array[bit] = 0
    return BitSequence(byte_array)
    # return byte_array
    # bitsequence = None
    # for byte in byte_array:
    #     if bitsequence is None:
    #         bitsequence = BitSequence(byte, length=8)
    #     else:
    #         bitsequence += BitSequence(byte, length=8)
    # return bitsequence.reverse()

class JTAG:

    class JTAGDevice():
        def __init__(self, idcode, bsdl_file, engine):
            self.idcode = idcode
            self.engine = engine
            self.load_bsdl(bsdl_file)
            self.register_size = self.json_bsdl.instruction_length

        def load_bsdl(self, bsdl_file):
            parser = bsdl.bsdlParser()
            json = parser.parse(bsdl_file, "bsdl_description", semantics=BsdlSemantics(), parseinfo=False).asjson()
            self.json_bsdl = bsdlJson.BsdlJson(json)

        def bypass(self):
            self.engine.go_idle()
            self.engine.capture_ir()
            self.engine.write_ir(BitSequence(self.json_bsdl.get_opcode('BYPASS'), length=self.register_size))

        def get_idcode(self):
            self.engine.go_idle()
            self.engine.capture_ir()
            self.engine.write_ir(BitSequence(self.json_bsdl.get_opcode('IDCODE'), length=self.register_size))
            return int.from_bytes(self.engine.read_dr(32).tobytes(), byteorder='big', signed=False)

        def write_pin(self, pin, value):
            bit_state_dict = {}
            for bit in range(0, self.json_bsdl.boundary_length):
                cell = self.json_bsdl.boundary_register[str(bit)]
                cell_spec = cell["cell_spec"]
                if cell_spec["port_id"] == pin:
                    if cell_spec["function"].upper() == "OUTPUT3":
                        disable_spec = cell["input_or_disable_spec"]
                        control_cell_number = int(disable_spec["control_cell"])
                        disable_value = int(disable_spec["disable_value"])
                        enable_value = 0 if disable_value == 1 else 1
                        bit_state_dict[control_cell_number] = enable_value
                        bit_state_dict[bit] = value

            self.engine.go_idle()
            self.engine.capture_ir()
            self.engine.write_ir(self.json_bsdl.sample_opcode)
            boundary_reg = self.engine.read_dr(self.json_bsdl.boundary_length)

            bit_settings = get_bit_settings(bit_state_dict, boundary_reg)

            self.engine.capture_ir()
            self.engine.write_ir(self.json_bsdl.get_opcode('PRELOAD'))
            self.engine.capture_dr()
            self.engine.write_dr(bit_settings)
            self.engine.capture_ir()
            self.engine.write_ir(self.json_bsdl.get_opcode('EXTEST'))
            self.engine.capture_dr()
            self.engine.write_dr(bit_settings)
    
    def __init__(self):
        self.interfaces = Ftdi.list_devices()

    def get_available_interfaces(self):
        return self.interfaces
        
    def connect(self, interface):
        self.engine = JtagEngine(frequency=10000)
        self.engine.configure(interface)

    def reset(self):
        self.devices = {}
        i = 0
        self.engine.reset()
        self.engine.change_state('shift_dr')
        idcode = self.engine._ctrl.read(32)
        while int(idcode) != 0:
            fetcher = bsdl_fetcher()
            list = fetcher.list_available_bsdl(idcode)
            bsdl_name, bsdl_file = fetcher.fetch_bsdl(list[1][3])
            self.devices[bsdl_name] = self.JTAGDevice(idcode, bsdl_file, self.engine)
            i += 1
            idcode = self.engine._ctrl.read(32)
        self.engine.change_state('update_dr')
        print('%d devices found' % i)


if __name__ == '__main__':
    from time import sleep
    jtag = JTAG()
    jtag.connect('ftdi:///' + str(jtag.interfaces[0][1]))
    jtag.reset()
    jtag.devices['CORTEXM3'].bypass()
    print('0x%08x'%jtag.devices['STM32F301_F302_LQFP64'].get_idcode())
    print('write pin')
    
    jtag.devices['STM32F301_F302_LQFP64'].write_pin('PB13', 1)
    sleep(2)
    jtag.reset()

    # while True:
    #     from time import sleep

    #     jtag.devices['STM32F301_F302_LQFP64'].write_pin('PB13', 1)
    #     sleep(0.1)
    #     jtag.devices['STM32F301_F302_LQFP64'].write_pin('PB13', 0)
    #     sleep(0.1)
    

    del jtag
