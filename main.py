import glob
import json
import shutil
from inspection_999 import Inspection999
from bindation import Bindation
from connectMongoDB import ConnectMongoDB

if __name__ == '__main__':
    ack_files = glob.glob(pathname='999/*.999')

    for ack_file in ack_files:
        inspection_ack_file = Inspection999(ack_file)
        ack_file_dict = inspection_ack_file.get_ack_dict()
        ack_file_index = inspection_ack_file.extract_index_data()
        # c = ConnectMongoDB()
        # c.connect_to_ack_collection()
        # c.insert_to_ack_collection(ack_file_dict)
        bindation = Bindation(ack_file_index, ack_file_dict)
        shutil.move(ack_file, 'inspected')
