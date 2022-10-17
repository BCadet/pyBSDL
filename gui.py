import PySimpleGUI as sg
from jtag import *
from bsdl_fetcher import bsdl_fetcher

sg.theme('DarkAmber')   # Add a touch of color

jtag = JTAG()
fetcher = bsdl_fetcher()

# All the stuff inside your window.
layout = [  [sg.Listbox(['1','2','3'], size=(40,10), key='interfaces', enable_events=True), sg.Button('connect')],
            [sg.Button('Cancel')] ]

# Create the Window
window = sg.Window('JTAG Boundary Scan', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    if event == 'connect':
        jtag.connect()
        jtag.ennumerate()
        interfaces = jtag.devices
        window['interfaces'].update(value=interfaces[0], values=interfaces)
    if event == 'interfaces':
        print('click')
        jtag.interface_url = 'ftdi://' + window['interfaces'].get()[0]

window.close()