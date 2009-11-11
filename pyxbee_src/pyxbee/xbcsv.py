import csv
import firmware as fw

def load(file_name, firmware=None):
    if firmware is None:
        firmware=fw.Firmware()
    with open(file_name) as f:
        csv_file=csv.DictReader(f)
    
    for data in csv_file:
        firmware.setCommand(firmware.Command(
                                     name=data['name'],
                                     at=data['at'],
                                     category=firmware.Category(name=data['category']),
                                     input=data['input'],
                                     description=data['description'],
                                     default=data['default']
                                     ))
    return firmware