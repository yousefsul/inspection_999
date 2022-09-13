import json

import bson.json_util

from connectMongoDB import ConnectMongoDB


class Bindation:
    def __init__(self, ack_index, ack_dict):
        self.ack_index = ack_index
        self.ack_dict = ack_dict
        self.trans_src_id = None
        self.transaction_type = self.ack_index.get('AK2').get('01')
        self.indexs, self.index = None, None
        self.connection = ConnectMongoDB()
        self.__find_and_bind()
        print(self.ack_index)
        print(self.ack_dict)

    def __find_and_bind(self):
        self.connection.connect_to_index_collection()
        self.connection.connect_to_837_collection()
        self.connection.connect_to_ack_collection()
        self.indexs = self.connection.get_indexs(self.transaction_type)
        for self.index in self.indexs:
            if not self.__check_isa():
                continue
            if not self.__check_gs():
                continue
            if not self.__check_st():
                continue

            self.trans_src_id = self.index.get('837_index').get('header_section').get('trans_src_id')
            self.ack_index['header_section']['trans_src_id'] = self.trans_src_id
            self.ack_dict['header_section']['trans_src_id'] = self.trans_src_id
            self.__insert_ack_data()
            self.__add_update_index()
            self.__add_update_837()

    def __check_isa(self):
        return \
            self.index.get('837_index').get('ISA').get('05').strip() == self.ack_index.get('ISA').get('07').strip() \
            and \
            self.index.get('837_index').get('ISA').get('06').strip() == self.ack_index.get('ISA').get('08').strip() \
            and \
            self.index.get('837_index').get('ISA').get('07').strip() == self.ack_index.get('ISA').get('05').strip() \
            and self.index.get('837_index').get('ISA').get('08').strip() == self.ack_index.get('ISA').get('06').strip()

    def __check_gs(self):
        return \
            self.ack_index.get('GS').get('02').strip() == self.index.get('837_index').get('GS').get('03').strip()\
            and\
            self.ack_index.get('GS').get('03').strip() == self.index.get('837_index').get('GS').get('02').strip()\
            and\
            self.ack_index.get('AK1').get('01').strip() == self.index.get('837_index').get('GS').get('01').strip()

    def __check_st(self):
        return self.ack_index.get('AK2').get('01').strip() == self.index.get('837_index').get('ST').get('01')

    def __add_update_index(self):
        self.connection.add_999_index(self.index.get('_id'), self.ack_index)
        self.connection.update_index_history_status_collection(self.index.get('_id'))
        self.connection.update_index_current_status(self.index.get('_id'))

    def __add_update_837(self):
        self.connection.update_837_history_status_collection(
            self.index.get('837_index').get('header_section').get('_id'))
        self.connection.update_837_current_status(self.index.get('837_index').get('header_section').get('_id'))

    def __insert_ack_data(self):
        self.connection.connect_to_ack_collection()
        self.connection.insert_to_ack_collection(self.ack_dict)
