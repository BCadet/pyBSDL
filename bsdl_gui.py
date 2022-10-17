import PySimpleGUI as sg
from bsdl_fetcher import bsdl_fetcher
import webbrowser

sg.theme('DarkAmber')   # Add a touch of color

class bsdl_gui():
    def __init__(self):
        self.fetcher = bsdl_fetcher()
        self.table_values = []
        self.table_headings = ['Name', 'Package']
        self.table_values.append(['', ''])
        self.table_cols_width = [10, 10]
        self.layout = [
            [sg.Text('IDCODE:'), sg.InputText(key='idcode', tooltip='type the IDCODE with the format prefix 0x for hexadecimal or 0b for binary'), sg.Checkbox('Ignore Version', default=True, key='ignore_version'), sg.Button('Search')],
            [sg.Table(
                expand_x=True,
                expand_y=True,
                values=self.table_values,
                headings=self.table_headings,
                col_widths=self.table_cols_width,
                auto_size_columns=False,
                justification='left',
                key='available_bsdl_list')],
            [sg.Button('View Details'), sg.Button('View BSDL'), sg.Button('Download'), sg.Button('Quit')] 
        ]
    
    def start(self):
        self.window = sg.Window('BSDL fetcher', self.layout)
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED or event == 'Quit': # if user closes window or clicks Quit
                break
            elif event == 'Search':
                try:
                    self.bsdl_list = self.fetcher.list_available_bsdl(int(values['idcode'],0), discard_version=values['ignore_version'])
                    self.window['available_bsdl_list'].update(values=self.bsdl_list)
                except:
                    print('wrong IDCODE format !')
            elif event == 'View Details':
                webbrowser.open(self.bsdl_list[values['available_bsdl_list'][0]][2])
            elif event == 'View BSDL':
                webbrowser.open(self.bsdl_list[values['available_bsdl_list'][0]][3])
            elif event == 'Download':
                bsdl_name, bsdl_file = self.fetcher.fetch_bsdl(self.bsdl_list[values['available_bsdl_list'][0]][3])
                self.fetcher.save_bsdl(bsdl_name, bsdl_file)
            else:
                print(event)

if __name__ == '__main__':
    gui = bsdl_gui()
    gui.start()