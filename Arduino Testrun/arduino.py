import serial
from datetime import datetime
import numpy as np
import json

ser_1 = serial.Serial('/dev/ttyACM0', 9600, timeout=2)
ser_2 = serial.Serial('/dev/ttyACM2', 9600, timeout=2)


def arduino():
    """
    Read a line from the serial port, sorts the data, and returns a dictionary with the data as raw data and their mean values.
    """

    counter = 0

    keys = ['VNFoll', 'IPFoll', 'IBLRes', 'VN', 'VN_2', 'IPLoad', 'INFB',
    'IPBigFine', 'IBLRes', 'VNCompFine', 'VNComp', 'IPBiasRec', 'VNBiasRec', 
    'vnlvds', 'vnlvdsdel', 'vppump', 'vpvco', 'vnvco', 'vpdcl', 'vndcl','qon']
    data_dict = {keys[i] : [0, []] for i in range(len(keys))}
  
    while counter < 4:
        ser_1.reset_input_buffer()
        ser_2.reset_input_buffer()

        line_1 = ser_1.readline().decode('utf-8').strip()
        line_2 = ser_2.readline().decode('utf-8').strip()

        if line_1[11:15] == 'LEFT' and line_2[11:15] == 'RIGH':
            values_L = line_1.split(',')
            values_R = line_2.split(',')
        elif line_1[11:15] == 'RIGH' and line_2[11:15] == 'LEFT':
            values_L = line_2.split(',')
            values_R = line_1.split(',')
        else:
            print("Invalid data received")
            continue

        all_values = values_L[1:9] + values_R[1:9]
        counter += 1
        for i in range(16):
            werte = list(map(float, all_values[i].split(':'))) 
            data_dict[keys[i]][1].extend(werte)  
        

        data_dict['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # calculate mean values and store them in the first element of each list
    for i in range(16):
        data_dict[keys[i]][0] = float(np.mean(data_dict[keys[i]][1]))
    return data_dict
        
try:
    print(arduino())
    # safe as a json file
    with open('data.json', 'w') as file:
        json.dump(arduino(), file, indent=4)
except KeyboardInterrupt:
    print("Program interrupted by user.")
except serial.SerialException as error:
    print(f"Serial error: {error}")
except Exception as exception:
    print(f"An error occurred: {exception}")
finally:
    ser_1.close()
    ser_2.close()


