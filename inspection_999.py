import datetime
import json
import os.path
from builtins import range

from connectMongoDB import ConnectMongoDB

loop_2000 = '2000'
loop_2100 = '2100'
loop_2110 = '2110'


def get_current_status():
    current_status = {
        "status": "new",
        "date": {
            "date": datetime.datetime.now().date().strftime("%Y%m%d"),
            "time": datetime.datetime.now().time().strftime("%H:%M:%S")
        }
    }
    return current_status


class Inspection999:
    def __init__(self, ack_file):
        self.ack_file = ack_file
        self.count, self.index = 1, 0
        self.time = datetime.datetime.now().time().strftime("%H:%M:%S")
        self.date = datetime.datetime.now().date().strftime("%Y%m%d")
        self.status_histroy = [get_current_status()]
        self.segment, self.data, self.data_element = None, None, None
        self.index_999 = {'header_section': {
            'file_name': os.path.basename(ack_file),
            "date_created": {
                "date": self.time,
                "time": self.date
            },
            "current_status": get_current_status(),
            "status_history": [get_current_status()],
        }}
        self.ack_dict = {
            'header_section': {
            'file_name': os.path.basename(ack_file),
            "date_created": {
                "date": self.time,
                "time": self.date
            },
            "current_status": get_current_status(),
            "status_history": [get_current_status()],
        }}
        self.connection = ConnectMongoDB()
        with open(self.ack_file, 'r') as acknowledgement_file:
            self.file_info = acknowledgement_file.read().strip('~').split('~')

        for i in range(len(self.file_info)):
            if self.file_info:
                self.extract_data()

    def __pop_element(self, index):
        if self.file_info:
            self.file_info.pop(index)

    def extract_data(self):
        self.data_element = self.file_info[0].split('*')
        self.index += 1
        self.segment = self.data_element.pop(0) + '-' + str(self.index)
        self.__bulid_main_dict()

    def __bulid_main_dict(self):
        self.count = 1
        self.ack_dict[self.segment] = {}
        if self.segment.split('-')[0] == 'AK1':
            self.__bulid_data_element(self.ack_dict[self.segment])
            self.__bulid_ak1_dict()

        elif self.segment.split('-')[0] == 'AK2':
            self.ack_dict[self.segment]['loop_name'] = loop_2000
            self.__bulid_data_element(self.ack_dict[self.segment])
            self.__bulid_ak2_dict()
        else:
            self.__bulid_data_element(self.ack_dict[self.segment])

    def __bulid_ak1_dict(self):
        for i in range(len(self.file_info)):
            try:
                if self.file_info[i].split('*')[0] == 'AK9':
                    data_element = self.file_info[i].split('*')
                    self.index += 1
                    self.count = 1
                    segment = data_element.pop(0) + '-' + str(self.index)
                    self.ack_dict[self.segment][segment] = {}
                    for data in data_element:
                        data_element_count = '{:02}'.format(self.count)
                        self.ack_dict[self.segment][segment][data_element_count] = data
                        self.count += 1
                    self.__pop_element(i)
                    break
            except IndexError:
                pass

    def __bulid_ak2_dict(self):
        for i in range(len(self.file_info)):
            i = 0
            try:
                if self.file_info[i].split('*')[0] == 'IK3':
                    self.data_element = self.file_info[i].split('*')
                    self.index += 1
                    segment = self.data_element.pop(0) + '-' + str(self.index)
                    self.ack_dict[self.segment][segment] = {}
                    self.ack_dict[self.segment][segment]['loop_name'] = loop_2100
                    self.__bulid_data_element(self.ack_dict[self.segment][segment])
                    self.__bulid_ik3_dict(segment)

                if self.file_info[i].split('*')[0] == 'IK5':
                    self.data_element = self.file_info[i].split('*')
                    self.index += 1
                    segment = self.data_element.pop(0) + '-' + str(self.index)
                    self.ack_dict[self.segment][segment] = {}
                    self.__bulid_data_element(self.ack_dict[self.segment][segment])
                    break
            except IndexError:
                pass

    def __bulid_ik3_dict(self, segment):
        for i in range(len(self.file_info)):
            i = 0
            try:
                if self.file_info[i].split('*')[0] == 'CTX':
                    self.data_element = self.file_info[i].split('*')
                    self.index += 1
                    sub_segment = self.data_element.pop(0) + '-' + str(self.index)
                    self.ack_dict[self.segment][segment][sub_segment] = {}
                    self.__bulid_data_element(self.ack_dict[self.segment][segment][sub_segment])

                elif self.file_info[i].split('*')[0] == 'IK4':
                    self.data_element = self.file_info[i].split('*')
                    self.index += 1
                    sub_segment = self.data_element.pop(0) + '-' + str(self.index)
                    self.ack_dict[self.segment][segment][sub_segment] = {}
                    self.ack_dict[self.segment][segment][sub_segment]['loop_name'] = loop_2110
                    self.__bulid_data_element(self.ack_dict[self.segment][segment][sub_segment])
                    self.__bulid_ik4_dict(segment, sub_segment)
                else:
                    break
            except IndexError:
                pass

    def __bulid_ik4_dict(self, segment, seg):
        for i in range(len(self.file_info)):
            i = 0
            try:
                if self.file_info[i].split('*')[0] == 'CTX':
                    self.data_element = self.file_info[i].split('*')
                    self.index += 1
                    sub_segment = self.data_element.pop(0) + '-' + str(self.index)
                    self.ack_dict[self.segment][segment][seg][sub_segment] = {}
                    self.__bulid_data_element(self.ack_dict[self.segment][segment][seg][sub_segment])
            except IndexError:
                pass

    def extract_index_data(self):
        for data in self.ack_dict:
            segment = data.split('-')[0]
            if segment == 'ISA':
                self.index_999[segment] = {}
                self.index_999[segment]['05'] = self.ack_dict[data]['05']
                self.index_999[segment]['06'] = self.ack_dict[data]['06']
                self.index_999[segment]['07'] = self.ack_dict[data]['07']
                self.index_999[segment]['08'] = self.ack_dict[data]['08']
            if segment == 'GS':
                self.index_999[segment] = {}
                self.index_999[segment]['02'] = self.ack_dict[data]['02']
                self.index_999[segment]['03'] = self.ack_dict[data]['03']
                self.index_999[segment]['06'] = self.ack_dict[data]['06']

            if segment == 'AK1':
                self.index_999[segment] = {}
                self.index_999[segment]['01'] = self.ack_dict[data]['01']
                self.index_999[segment]['02'] = self.ack_dict[data]['02']
                self.index_999[segment]['03'] = self.ack_dict[data]['03']

            if segment == 'AK2':
                self.index_999[segment] = {}
                self.index_999[segment]['01'] = self.ack_dict[data]['01']
                self.index_999[segment]['02'] = self.ack_dict[data]['02']
                self.index_999[segment]['03'] = self.ack_dict[data]['03']
        return self.index_999

    def __bulid_data_element(self, param):
        self.count = 1
        for self.data in self.data_element:
            data_element_count = '{:02}'.format(self.count)
            param[data_element_count] = self.data
            self.count += 1
        self.__pop_element(0)

    def get_ack_dict(self):
        return self.ack_dict
