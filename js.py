from RCSnew import RCSServer,RobotData
import binascii

def main():
    shared = RobotData()
    a = RCSServer(shared,host='0.0.0.0', port=23311)
    report_data = {
        'act_name': '1', 
        'act_id': '1', 
        'act_parameter': {
            'MaterialID': '1', 
            'count': 12, 
            'startAddress': [{'location': 'R06', 
                                'number': '1', 
                                'count': 12, 
                                'stateList': 'full'}],
            'endAddress': [{'location': 'R13', 
                                'number': '1', 
                                'count': 0, 
                                'stateList': 'full'}], 
            'palletInformation': []}, 
    }
    a1 = a.build_packet(1,2200,report_data)
    hex_str = binascii.hexlify(a1).decode().upper()
    pretty = ' '.join(hex_str[i:i + 2] for i in range(0, len(hex_str), 2))
    print(pretty)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Main Error:" + str(e.args))