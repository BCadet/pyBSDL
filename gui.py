import PySimpleGUI as sg

from jtag import *

sg.theme('DarkAmber')   # Add a touch of color

jtag = JTAG()

deviceList = []

# All the stuff inside your window.
layout = [  [sg.Button('ennumerate'), sg.Button('Cancel')],
            [sg.Combo([], size=(12,20), key='deviceList')] ]

# Create the Window
window = sg.Window('JTAG Boundary Scan', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    if event == 'ennumerate':
        jtag.ennumerate()
        deviceList = jtag.devices
        window['deviceList'].update(value=deviceList[0], values=deviceList)

window.close()