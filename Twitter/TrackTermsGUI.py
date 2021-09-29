import PySimpleGUI as sg
from datetime import datetime
import re
import csv
import os


class TrackTermsGUI():
    def __init__(self, look, file_track_terms_audit, path, bachslash, files):
        """
        # Class constructor or initialization method.
        # Generic GUI to choose exitence or new list of terms to track

        :param look: window setting style
        :param file_track_terms_audit: file name which contains list of terms to track
        :param path: file_track_terms_audit path
        :param bachslash: used to concatenating path
        :param files: combo list
        """
        self.look = look
        self.file_track_terms_audit = file_track_terms_audit
        self.path = path
        self.bachslash = bachslash
        self.files = files

    def open_main_window(self):
        """
        # GUI main Client window
        """
        track_terms_dic = ''
        sg.theme(self.look)

        layout = [[sg.Text('Welcome to tweeet monitor ')],
                  [sg.Text('Please enter Details ')],
                  [sg.Text('User Mail', size=(15, 1)), sg.InputText()],
                  [sg.Text('Timout', size=(15, 1)), sg.InputText('', enable_events=True, key='-DIGITS-')],
                  [sg.Text('')],
                  [sg.Text('You can select an existing list or create a new one  '),
                   sg.Combo(self.files, default_value='Select Track Terms List ', key='-COMBO1-')],
                  [sg.Text('')],
                  [sg.Button('Select Exists List'), sg.Button('Create a New List')],
                  [sg.Text('\n')],
                  [sg.Button('Start Monitor'), sg.Button('Exit')]
                  ]

        window = sg.Window('Monitor tweeter', layout)
        # Event Loop
        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED:
                exit()
            elif event == 'Select Exists List' or event == 'Create a New List' or event == 'Start Monitor':
                user_mail = values[0]
                timeout = values['-DIGITS-']
                list_dic = values['-COMBO1-']

                if self.check(user_mail) == 'Invalid Email':
                    self.info_popup_window('You Enter not valid mail ', 'Info', self.look)
                elif event == 'Select Exists List':
                    if list_dic == 'Select Track Terms List ':
                        self.info_popup_window('Track Terms List ', 'Info', self.look)
                    else:
                        file_name = self.path + self.bachslash + list_dic
                        os.system(file_name)
                        track_terms_dic = list_dic
                elif event == 'Create a New List':
                    track_terms_dic = self.open_window()
                    track_terms_dic = track_terms_dic + '.txt'
                elif event == 'Start Monitor':
                    if track_terms_dic == '':
                        self.info_popup_window('Please, Create new Dictionary or select one ', 'Info', self.look)
                    elif track_terms_dic != '':
                        file_name = self.path + self.bachslash + track_terms_dic
                        my_file = open(file_name, "r")
                        content = my_file.read()
                        content = content.split("\n")
                        content = self.cleanList(content)
                        # print(content)
                        my_file.close()
                        now = datetime.now()
                        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                        dict_list = {'User': user_mail,
                                     'Timeout': timeout,
                                     'Dictionary': list_dic,
                                     'Create Date': date_time,
                                     'track_terms_list': content
                                     }
                        header = ['user_mail', 'Timeout', 'Dictionary', 'Create Date', 'list words']
                        if os.path.isfile(self.file_track_terms_audit) == False:
                            # check if the file exsist  = if not: create file and print header to the file
                            with open(self.file_track_terms_audit, 'a', newline='\n') as file:
                                try:
                                    write = csv.writer(file)
                                    write.writerow(header)
                                    write.writerows(self.values_list)
                                    file.close()
                                except:
                                    print("Something went wrong when writing to the file")
                        else:
                            self.values_list = list(dict_list.values())
                            # print ('self.values_list   :****',self.values_list)
                            with open(self.file_track_terms_audit, 'a', newline='\n') as file:
                                try:
                                    write = csv.writer(file)
                                    self.values_list = [self.values_list]
                                    write.writerows(self.values_list)
                                    file.close()
                                except:
                                    print("Something went wrong when writing to the file")
                        print('self.values_list:', self.values_list)

                        window.close()

                        print('track_terms_dic: ', track_terms_dic)
                        print('dict_list:', dict_list)
                        return (dict_list)

            # always check for closed window
            if event in (sg.WIN_CLOSED, 'Exit'):
                break

            if event == '-LIST-' and len(values['-LIST-']):
                sg.popup('Selected ', values['-LIST-'])

            if len(values['-DIGITS-']) and values['-DIGITS-'][-1] not in ('0123456789'):
                # delete last char from input
                window['-DIGITS-'].update(values['-DIGITS-'][:-1])

        window.close()

    def cleanList(self, mylist):
        """
        # remove spaces, duplicate value and sort the list

        :param mylist: list of terms to track
        :return [list] list of terms
        """
        newlist = []
        for val in mylist:
            if val.strip() != '':
                newlist.append(val)
        myList = sorted(set(newlist))

        return newlist

    def info_popup_window(self, info, title, look):
        """
        # raise popup window

        :param info: win message info
        :param title: win title
        :param look: win look
        """
        sg.theme(self.look)
        sg.popup(info, title='hello')

    def check(self, email):
        """
        # validate given email

        :param email: email string to be validated
        :return [string]: travk terms fine name
        """

        regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
        # pass the regular expression
        # and the string in search() method
        if (re.search(regex, email)):
            return 'Valid Email'
        else:
            return 'Invalid Email'

    def open_window(self):
        """
        # Open window associated with related buttons

        :return [dictionary]: valid \invalid email
        """
        newdic = ''
        layout = [[sg.Text("Please enter a new name for your Dictionary\n\n")],
                  [sg.Text('New Dictionary name:  ', size=(15, 1)),
                   sg.InputText('', enable_events=True, key='-NEWDIC-')],
                  [sg.Text("\n\n")],
                  [sg.Button("OK"), sg.Button('Exit')]
                  ]
        window = sg.Window("Create New Dictionary", layout, modal=True)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "Exit":
                window.close()

            elif event == "OK":
                newdic = values['-NEWDIC-']
                file_name = self.path + self.bachslash + newdic + '.txt'
                print(file_name)
                if not os.path.exists(file_name):
                    with open(file_name, "w"):
                        pass
                else:
                    self.info_popup_window('The name you entered already exists ', 'Info', self.look)
                os.system(file_name)
        window.close()
        return newdic
