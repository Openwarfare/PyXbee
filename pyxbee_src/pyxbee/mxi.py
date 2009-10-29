import firmware as fw
from datatypes import *
import validators

def parseTextField(data):
    return data

def parseInputField(data):
    field = None
    if data is not 'N':
        data=data.split(';')
        field_type=data[0]
        if field_type == 'C':
            choices=Choice()
            for value,name in enumerate(data[1:]):
                choices.add(name, value)
            field=fw.Input(
                          value=None,
                          type=choices.choice_type,
                          validator=validators.Choice(choices.choices)
                          )
        if field_type == 'E':
            range=data[1].split('-')
            field=fw.Input(
                          type=Hex,
                          validator=validators.Range(Hex(range[0]),Hex(range[1])),
                          )
        if field_type == 'S':
            if data[3] == 'HEX':
                input_type=HexString
            else:
                input_type=String
                
            field=fw.Input(
                          type=input_type,
                          validator=validators.Length(Int(data[1]),Int(data[2])),
                          )
    return field

def parseOutputField(data):
    if not data:
        return Raw()
    else:
        return data
    
xbee_parse_maps={
                 'hardware':[
                             {'name':'header','type':parseTextField},
                             {'name':'short_header','type':parseTextField},
                             {'name':'major','type':parseTextField},
                             {'name':'minor','type':parseTextField},
                             {'name':'release','type':parseTextField},
                             ],
                'software':[
                            {'name':'header','type':parseTextField},
                            {'name':'Unknown1','type':parseTextField},
                            {'name':'Unknown2','type':parseTextField},
                            {'name':'Unknown3','type':parseTextField},
                            {'name':'Unknown4','type':parseTextField},
                            ],
                'category':[
                            {'name':'header','type':parseTextField},
                            {'name':'category','type':parseTextField},
                            {'name':'description','type':parseTextField},
                            ],

                'command':[
                           {'name':'at','type':parseTextField},
                           {'name':'default','type':parseTextField},
                           {'name':'name','type':parseTextField},
                           {'name':'input','type':parseInputField},
                           {'name':'description','type':parseTextField},
                           ],

                'firmware':[
                            {'name':'product','type':parseTextField},
                            {'name':'modem','type':parseTextField},
                            {'name':'Unknown1','type':parseTextField},
                            {'name':'Unknown2','type':parseTextField},
                            {'name':'version','type':parseTextField},
                            {'name':'Unknown3','type':parseTextField},
                            {'name':'Unknown4','type':parseTextField},
                            {'name':'Unknown5','type':parseTextField},
                            {'name':'function_set','type':parseTextField},
                            ]
                }

def load(file, firmware=None):
    with open(file) as f:
        data=f.read()
    commands=parse(data, firmware)
    return commands
    
def parse(text, firmware=None):
    category=None
    if firmware is None:
        firmware=fw.Firmware()
    for line in text.splitlines():
        if line:
            #print line
            data=line[1:-1].split('][') 
            #command data
            if data[0][0:4]=='XBEE':
                data=mapData(data,xbee_parse_maps['firmware'])
                firmware.function_set=data['function_set']
                firmware.product=data['product']
                firmware.version=data['version']
                firmware.modem=data['modem']
            #hardware information
            #TODO: find a place for this data
            elif data[0]=='HARDWARE_VERSION':
                data=mapData(data,xbee_parse_maps['hardware'])
            #software information
            #TODO: find a place for this data
            elif data[0]=='SOFTWARE_COMPATABLITY':
                data=mapData(data,xbee_parse_maps['software'])
            #category information
            elif len(data[0])==1:
                data=mapData(data,xbee_parse_maps['category'])
                if data['header']=='H':
                    parent=None
                if data['header']=='L':
                    parent=category
                category=fw.Category(
                                  parent=parent,
                                  name=data['category'],
                                  description=data['description'],
                                  header=data['header']
                                  )
            #AT command information
            elif len(data[0])==2:
                data=mapData(data,xbee_parse_maps['command'])
                firmware.setCommand(fw.Command(
                                     name=data['name'],
                                     at=data['at'],
                                     category=category,
                                     input=data['input'],
                                     description=data['description'],
                                     default=data['default']
                                     ))
            else:
                print "Unknown Data"
                print "line=%s"%line
                print "data=%s"%data
    return firmware
    
def mapData(data,map):
    result={}
    for index,item in enumerate(map):
        try:
            result[item['name']]=item['type'](data[index])
        except IndexError, e:
            print('Map/Data mismatch')
            print data
            print map
    return result

def main():
    cmds=load('../firmware/XBP24_15_4_10C8.mxi')
    print cmds
if __name__=='__main__':
    main()