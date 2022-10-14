#!/usr/bin/env python3
from os import environ
from pyftdi.jtag import JtagEngine, JtagTool
from pyftdi.ftdi import Ftdi
from pyftdi.bits import BitSequence

import requests
from bs4 import BeautifulSoup

class JTAG:
    def __init__(self):
        self.interfaces = Ftdi.list_devices()
        print(self.interfaces)
        

    def connect(self):
        self.engine = JtagEngine(frequency=10000)
        self.engine.configure(self.interface_url)
        self.engine.reset()

    def ennumerate(self):
        self.devices = []
        i = 0
        self.engine.change_state('shift_dr')
        idcode = self.engine._ctrl.read(32)
        while int(idcode) != 0:
            device = {}
            device['IDCODE'] = idcode
            self.devices.append(device)
            print('idcode detected 0x%08X' % int(idcode))
            i += 1
            idcode = self.engine._ctrl.read(32)
        self.engine.change_state('update_dr')
        print('%d devices found' % i)

    def get_bsdl(self):
        bsdl_site = 'https://bsdl.info/'
        bsdl_search = bsdl_site + 'list.htm?search='
        for device in self.devices:
            unversioned = '0000' + format(int(device['IDCODE']), '032b')[4:]
            print(unversioned)
            page = requests.get(bsdl_search + unversioned)
            soup = BeautifulSoup(page.content, 'html.parser')
            panel = soup.select('div.panel')
            table = panel[0].select('table')
            entries = table[0].select('tbody')[0].select('tr')
            # for entry in entries:
            entry = entries[0]
            name = entry.find('a').getText().strip()
            view_link = entry.select('a.button')[0].get('href')
            print('name ' + name + ' link ' + bsdl_site + view_link)
            page = requests.get(bsdl_site + view_link)
            soup = BeautifulSoup(page.content, 'html.parser')
            code = soup.select('code')[0].getText()
            print(code)

# 00001011101000000000010001110111
# 01001011101000000000010001110111

if __name__ == '__main__':
    jtag = JTAG()
    jtag.ennumerate()
    jtag.get_bsdl()
    # jtag.change_state('shift_dr')
    # idcode = jtag._ctrl.read(32)
    # idcode2 = jtag._ctrl.read(32)
    # idcode3 = jtag._ctrl.read(32)
    # jtag.change_state('update_dr')
    # print("IDCODE = 0x%08X" % int(idcode))
    # print("IDCODE2 = 0x%08X" % int(idcode2))
    # print("IDCODE3 = 0x%08X" % int(idcode3))

    # jtag.capture_ir()
    # jtag.write_ir(BitSequence('1111111111', msb=True, length=10))
    # jtag.write_ir(JTAG_INSTR['BYPASS'])
    # tool.detect_register_size()
    # jtag.write_ir(JTAG_INSTR['IDCODE'])
    # print("IDCODE = 0x%08X" %tool.idcode())
    # jtag.write_ir(JTAG_INSTR['BYPASS'])
    # jtag.write_ir(JTAG_INSTR['BYPASS'])
    # jtag.capture_ir()
    # tool.detect_register_size()

    # jtag.write_ir(JTAG_INSTR['IDCODE'])
    # print("IDCODE = 0x%08X" %tool.idcode())
    # jtag.write_ir(JTAG_INSTR['IDCODE_ST'])
    # print("IDCODE = 0x%08X" %(tool.idcode()))
    # print("IDCODE = 0x%08X" %tool.idcode())
    del jtag

# JTAG_INSTR = {'SAMPLE': BitSequence('000000010', msb=True, length=9),
#               'PRELOAD': BitSequence('000000010', msb=True, length=9),
#               'IDCODE': BitSequence('000001110', msb=True, length=9),
#               'BYPASS': BitSequence('111111111', msb=True, length=9),
#               'IDCODE_ST': BitSequence('00001', msb=True, length=9)}


# class JtagTestCase():

#     def setUp(self):
#         url = environ.get('FTDI_DEVICE', 'ftdi://ftdi:232h/1')
#         self.jtag = JtagEngine(frequency=10000)
#         self.jtag.configure(url)
#         self.jtag.reset()
#         self.tool = JtagTool(self.jtag)
#         self.jtag.go_idle()

#     def tearDown(self):
#         del self.jtag

#     def test_idcode_reset(self):
#         """Read the IDCODE right after a JTAG reset"""
#         self.jtag.reset()
#         idcode = self.jtag.read_dr(32)
#         idcode2 = self.jtag.read_dr(32)
#         self.jtag.go_idle()
#         print("IDCODE (reset): 0x%x" % int(idcode))
#         print("IDCODE2 (reset): 0x%x" % int(idcode2))

#     def test_idcode_sequence(self):
#         """Read the IDCODE using the dedicated instruction"""
#         instruction = JTAG_INSTR['IDCODE_ST']
#         # instruction = JTAG_INSTR['IDCODE_ST']
#         self.jtag.write_ir(instruction)
#         idcode = self.jtag.capture_dr()
#         idcode = self.jtag.read_dr(32)
#         self.jtag.go_idle()
#         print("IDCODE (idcode): 0x%08x" % (int(idcode)))

#     def test_idcode_shift_register(self):
#         """Read the IDCODE using the dedicated instruction with
#            shift_and_update_register"""
#         instruction = JTAG_INSTR['IDCODE']
#         self.jtag.change_state('shift_ir')
#         retval = self.jtag.shift_and_update_register(instruction)
#         print("retval: 0x%x" % int(retval))
#         self.jtag.go_idle()
#         self.jtag.change_state('shift_dr')
#         idcode = self.jtag.shift_and_update_register(BitSequence('0'*32*2))
#         self.jtag.go_idle()
#         print("IDCODE (idcode): 0x%08x" % int(idcode))

#     def test_bypass_shift_register(self):
#         """Test the BYPASS instruction using shift_and_update_register"""
#         instruction = JTAG_INSTR['BYPASS']
#         self.jtag.change_state('shift_ir')
#         retval = self.jtag.shift_and_update_register(instruction)
#         print("retval: 0x%x" % int(retval))
#         self.jtag.go_idle()
#         self.jtag.change_state('shift_dr')
#         _in = BitSequence('011011110000'*2, length=24)
#         out = self.jtag.shift_and_update_register(_in)
#         self.jtag.go_idle()
#         print("BYPASS sent: %s, received: %s  (should be left shifted by one)"
#               % (_in, out))

# def detect_reg_size(tool):
#         # Freely inpired from UrJTAG
#         stm = tool._engine.state_machine
#         if not stm.state_of('shift'):
#             raise JtagError("Invalid state: %s" % stm.state())
#         if stm.state_of('capture'):
#             bs = BitSequence(False)
#             tool._engine.controller.write_tms(bs)
#             stm.handle_events(bs)
#         MAX_REG_LEN = 1024
#         PATTERN_LEN = 2
#         stuck = None
#         for length in range(1, MAX_REG_LEN):
#             print("Testing for length %d" % length)
#             zero = BitSequence(length=length)
#             inj = BitSequence(length=length+PATTERN_LEN)
#             inj.inc()
#             ok = False
#             for _ in range(1, 1 << PATTERN_LEN):
#                 ok = False
#                 tool._engine.write(zero, False)
#                 print('write ' + str(zero))
#                 rcv = tool._engine.shift_register(inj)
#                 try:
#                     tdo = rcv.invariant()
#                     print('tdo ' + str(tdo))
#                 except ValueError:
#                     tdo = None
#                 if stuck is None:
#                     stuck = tdo
#                 if stuck != tdo:
#                     stuck = None
#                 rcv >>= length
#                 print('rcv ' + str(rcv))
#                 print('inj ' + str(inj))
#                 if rcv == inj:
#                     ok = True
#                 else:
#                     break
#                 inj.inc()
#             if ok:
#                 print("Register detected length: %d" % length)
#                 return length
#         if stuck is not None:
#             raise JtagError('TDO seems to be stuck')
#         raise JtagError('Unable to detect register length')

# jtag = JtagTestCase()
# jtag.setUp()
# jtag.test_idcode_reset()
# jtag.test_idcode_sequence()
# # jtag.test_idcode_shift_register()
# # jtag.test_bypass_shift_register()
# from pyftdi.jtag import *
# jtag.jtag.capture_ir()
# detect_reg_size(jtag.tool)