import glob

from inspection_999 import Inspection999

if __name__ == '__main__':
    ack_files = glob.glob(pathname='999/*.999')
    for ack_file in ack_files:
        inspection_ack_file = Inspection999(ack_file)
        inspection_ack_file.extract_index_data()
