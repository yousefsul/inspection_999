import datetime
import json
import os.path
from builtins import range, print

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
        self.count = 1
        self.c = 0
        self.index = 0
        self.time = datetime.datetime.now().time().strftime("%H:%M:%S")
        self.date = datetime.datetime.now().date().strftime("%Y%m%d")
        self.status_histroy = [get_current_status()]
        self.segment = None
        self.data = None
        self.data_element = None
        self.info_999 = {}
        self.final_segment = {'header_section': {
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

        print(json.dumps(self.final_segment, indent=4))
        self.connection.connect_to_test_999_collection()
        self.connection.insert_to_test_999_collection(self.final_segment)

    def __pop_element(self, ind):
        if self.file_info:
            self.file_info.pop(ind)

    def extract_data(self):
        self.data_element = self.file_info[0].split('*')
        self.index += 1
        self.segment = self.data_element.pop(0) + '-' + str(self.index)
        self.__bulid_main_dict()

    def __bulid_main_dict(self):
        self.count = 1
        self.final_segment[self.segment] = {}
        if self.segment.split('-')[0] == 'AK1':
            for self.data in self.data_element:
                data_element_count = '{:02}'.format(self.count)
                self.final_segment[self.segment][data_element_count] = self.data
                self.count += 1
            self.__pop_element(0)
            self.__bulid_ak1_dict()

        elif self.segment.split('-')[0] == 'AK2':
            self.final_segment[self.segment]['loop_name'] = loop_2000
            for self.data in self.data_element:
                data_element_count = '{:02}'.format(self.count)
                self.final_segment[self.segment][data_element_count] = self.data
                self.count += 1
            self.__pop_element(0)
            self.__bulid_ak2_dict()

        else:
            for self.data in self.data_element:
                data_element_count = '{:02}'.format(self.count)
                self.final_segment[self.segment][data_element_count] = self.data
                self.count += 1
            self.__pop_element(0)

    def __bulid_ak1_dict(self):
        for i in range(len(self.file_info)):
            try:
                if self.file_info[i].split('*')[0] == 'AK9':
                    data_element = self.file_info[i].split('*')
                    self.index += 1
                    self.count = 1
                    segment = data_element.pop(0) + '-' + str(self.index)
                    self.final_segment[self.segment][segment] = {}
                    for data in data_element:
                        data_element_count = '{:02}'.format(self.count)
                        self.final_segment[self.segment][segment][data_element_count] = data
                        self.count += 1
                    self.__pop_element(i)
                    break
            except IndexError:
                pass

    def __bulid_ak2_dict(self):
        for i in range(len(self.file_info)):
            try:
                if self.file_info[i].split('*')[0] == 'IK3':
                    data_element = self.file_info[i].split('*')
                    self.index += 1
                    segment = data_element.pop(0) + '-' + str(self.index)
                    self.final_segment[self.segment][segment] = {}
                    self.final_segment[self.segment][segment]['loop_name'] = loop_2100
                    self.count = 1
                    for data in data_element:
                        data_element_count = '{:02}'.format(self.count)
                        self.final_segment[self.segment][segment][data_element_count] = data
                        self.count += 1
                    self.file_info.pop(i)
                    self.__bulid_ik3_dict(segment)
                    while self.c > 0:
                        self.__pop_element(0)
                        self.c -= 1

                elif self.file_info[i].split('*')[0] == 'IK5':
                    data_element = self.file_info[i].split('*')
                    self.index += 1
                    segment = data_element.pop(0) + '-' + str(self.index)
                    self.final_segment[self.segment][segment] = {}
                    self.count = 1
                    for data in data_element:
                        data_element_count = '{:02}'.format(self.count)
                        self.final_segment[self.segment][segment][data_element_count] = data
                        self.count += 1
                    self.file_info.pop(i)
            except IndexError:
                pass

    def __bulid_ik3_dict(self, segment):
        for i in range(len(self.file_info)):
            if self.file_info[i].split('*')[0] == 'CTX':
                self.c += 1
                data_element = self.file_info[i].split('*')
                self.index += 1
                sub_seg = data_element.pop(0) + '-' + str(self.index)
                self.final_segment[self.segment][segment][sub_seg] = {}
                self.count = 1
                for data in data_element:
                    data_element_count = '{:02}'.format(self.count)
                    self.final_segment[self.segment][segment][sub_seg][data_element_count] = data
                    self.count += 1

            elif self.file_info[i].split('*')[0] == 'IK4':
                self.c += 1
                data_element = self.file_info[i].split('*')
                self.index += 1
                sub_seg = data_element.pop(0) + '-' + str(self.index)
                self.final_segment[self.segment][segment][sub_seg] = {}
                self.final_segment[self.segment][segment][sub_seg]['loop_name'] = loop_2110
                self.count = 1
                for data in data_element:
                    data_element_count = '{:02}'.format(self.count)
                    self.final_segment[self.segment][segment][sub_seg][data_element_count] = data
                    self.count += 1
                self.__bulid_ik4_dict(segment, sub_seg, i)
            else:
                break

    def __bulid_ik4_dict(self, segment, seg, i):
        if self.file_info[i + 1].split('*')[0] == 'CTX':
            data_element = self.file_info[i + 1].split('*')
            self.index += 1
            sub_seg = data_element.pop(0) + '-' + str(self.index)
            self.final_segment[self.segment][segment][seg][sub_seg] = {}
            self.count = 1
            for data in data_element:
                data_element_count = '{:02}'.format(self.count)
                self.final_segment[self.segment][segment][seg][sub_seg][data_element_count] = data
                self.count += 1
            self.__pop_element(i + 1)

    def extract_index_data(self):
        self.info_999 = {'header_section': {
            'file_name': os.path.basename(self.final_segment.get('header_section').get('file_name')),
            "date_created": {
                "date": self.time,
                "time": self.date
            },
            "current_status": get_current_status(),
            "status_history": [get_current_status()],
        }}
        for data in self.final_segment:
            segment = data.split('-')[0]
            if segment == 'ISA':
                self.info_999[segment] = {}
                self.info_999[segment]['06'] = self.final_segment[data]['06']
                self.info_999[segment]['08'] = self.final_segment[data]['08']
            if segment == 'GS':
                self.info_999[segment] = {}
                self.info_999[segment]['02'] = self.final_segment[data]['02']
                self.info_999[segment]['03'] = self.final_segment[data]['03']
            if segment == 'AK1':
                self.info_999[segment] = {}
                self.info_999[segment] = self.final_segment[data]
                for item in self.info_999[segment]:
                    i = item.split('-')
                    try:
                        if i[0] == 'AK9':
                            self.info_999.get(segment).pop(item)
                            break
                    except Exception as E:
                        pass

        for data in self.final_segment:
            segment = data.split('-')[0]
            if segment == 'AK2':
                self.info_999[segment] = {}
                self.info_999[segment] = self.final_segment[data]
                for item in self.info_999[segment]:
                    i = item.split('-')
                    try:
                        if i[0] == 'IK5':
                            self.info_999.get(segment).pop(item)
                            break
                    except Exception as E:
                        pass

                for item in self.info_999[segment]:
                    i = item.split('-')
                    try:
                        if i[0] == 'IK3':
                            self.info_999.get(segment).pop(item)
                            break
                    except Exception as E:
                        pass
                break

        self.connection.connect_to_999_collection()
        self.connection.insert_to_999_collection(self.info_999)
