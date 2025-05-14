import serial
import numpy as np
import time
import matplotlib.pyplot as plt
import pandas as pd
import os
import shutil
from matplotlib.backends.backend_pdf import PdfPages



test_pin_mapping = {
    0: 'IPDAC',
    1: "VNDel",
    2: "VNBiasRec",
    3: "IPBiasRec",
    8: "IBLRes",
    9: "VN",
    10: "INFB",
    11: "VNFoll",
    12: "IPLoad",
    13: "VNComp"
}

def arduino(steps=25, pin_mapping=test_pin_mapping):
    """
    Read a line from the serial port, sorts the data, and returns a dictionary with the data as raw data and their mean values.
    Only processes pins specified in the pin_mapping.
    """
    ser_1 = serial.Serial('/dev/ttyACM0', 115200, timeout=2)
    ser_2 = serial.Serial('/dev/ttyACM1', 115200, timeout=2)
    counter = 0

    def read_packet(ser):
        buffer = ""
        recording = False
        while True:
            char = ser.read().decode('utf-8', errors='replace')
            if char == '<':
                buffer = ""
                recording = True
            elif char == '>':
                return buffer.strip()
            elif recording:
                buffer += char

    # Initialize the data dictionary based on the pin mapping
    data_dict = {key: [0, []] for key in pin_mapping.values()}
    time.sleep(0.05)  # wait for the serial connection to establish

    while counter < steps:
        line_1 = read_packet(ser_1)
        line_2 = read_packet(ser_2)

        if line_1[11:15] == 'LEFT' and line_2[11:15] == 'RIGH':
            values_L = line_1.split(',')
            values_R = line_2.split(',')

        elif line_1[11:15] == 'RIGH' and line_2[11:15] == 'LEFT':
            values_L = line_2.split(',')
            values_R = line_1.split(',')

        else:
            continue
        
        all_values = values_L[1:9] + values_R[1:9]
        counter += 1

        # Process only the pins specified in the pin_mapping
        for pin_index, key in pin_mapping.items():
            werte = list(map(float, all_values[pin_index].split(':')))
            data_dict[key][1].extend(werte)
    
    # Calculate mean values and store them in the first element of each list
    for key in data_dict:
        data_dict[key][0] = float(np.mean(data_dict[key][1]))
    ser_1.close()
    ser_2.close()
    return data_dict
        

def arduino_power_plot(path, output_path, infostring=None, save = True):
    TEXT_COLOR = '#07529a'
    TITLE_COLOR = '#07529a'
    pdf_path = f'{output_path}/latest.pdf'
    with PdfPages(pdf_path) as pdf:
        timestamps = []
        for root, dirs, files in os.walk(path):
            csv_files = [file for file in files if file.endswith('.csv')]
            if len(csv_files) > 0:
                csv_files.sort(reverse=True)
                timestamps.append(csv_files[0][-19:-4])
                data_file = csv_files[0]
                
                fig, ax1 = plt.subplots()
                ax2 = ax1.twinx()


                df = pd.read_csv(f'{root}/{data_file}', skipinitialspace=True)
                ax2.plot(df['DAC_set_value'].values, 1000*df['vdda_curr'].values, color = 'navy', label='vdda current', marker='o', alpha=0.8)
                ax2.plot(df['DAC_set_value'].values, 1000*df['vddd_curr'].values, color = 'slateblue', label='vddd current', marker='o', alpha=0.8)    
                ax1.plot(df['DAC_set_value'].values, df['DAC_measured'].values*5/4.735, color = 'crimson', label='DAC_measured', marker='o', alpha=0.8)
                
                handles1, labels1 = ax1.get_legend_handles_labels()
                handles2, labels2 = ax2.get_legend_handles_labels()
                handles = handles1 + handles2
                labels = labels1 + labels2
                
                ax1.set_title(f'DAC analysis: {df["DAC_name"][0]}', color = TITLE_COLOR, fontsize=14)
                ax1.set_xlabel('DAC_value / DAC', fontsize=12)
                ax1.set_ylabel('DAC_measured / V', color = 'crimson', fontsize=12)
                ax2.set_ylabel('current / mA', color = 'navy', fontsize = 12)

                ax1.tick_params(axis='y', labelcolor='crimson')
                ax2.tick_params(axis='y', labelcolor='navy')

                ax1.legend(handles, labels,  title = infostring)
                ax1.set_ylim(0, max(df['DAC_measured'].values*5/4.735)*1.05)
                
                ax1.grid()
                pdf.savefig(fig, bbox_inches='tight')
                plt.close(fig)
    
    timestamps.sort(reverse=True)
    if save == True:
        shutil.copy(pdf_path, f'{output_path}/DAC_scan_{timestamps[0]}.pdf')


def read_hw(hw, channel1 = 1, channel2 = 2):
    hw.select_channel(channel1)
    hmc_volt_vdda = float(hw.read_voltage())
    hmc_curr_vdda = float(hw.read_current())
    hw.select_channel(channel2)
    hmc_volt_vddd = float(hw.read_voltage())
    hmc_curr_vddd = float(hw.read_current())
    return [hmc_volt_vdda, hmc_curr_vdda], [hmc_volt_vddd, hmc_curr_vddd]


def read_hw_mean(hw, channel1=1, channel2=2, n = 24):
    """
    Read a line from the serial port, sorts the data, and returns a dictionary with the mean values.
    """
    hw_inputs = ['vddd_volt', 'vddd_curr', 'vddd_powr','vdda_volt', 'vdda_curr', 'vdda_powr']
    hw_data_dict = {hw_inputs[i] : [] for i in range(len(hw_inputs))}
    for i in range(n):
        vdda, vddd = read_hw(hw, channel1, channel2)
        hw_data_dict['vdda_volt'].append(vdda[0])
        hw_data_dict['vdda_curr'].append(vdda[1])
        hw_data_dict['vddd_volt'].append(vddd[0])
        hw_data_dict['vddd_curr'].append(vddd[1])
        hw_data_dict['vdda_powr'].append(vdda[0]*vdda[1])
        hw_data_dict['vddd_powr'].append(vddd[0]*vddd[1])
    for i in range(len(hw_inputs)):
        hw_data_dict[hw_inputs[i]] = float(np.mean(hw_data_dict[hw_inputs[i]])) 
    return hw_data_dict

def DAC_comparison_plot(path):
    keys = ['IPDAC', 'VNDel', 'VNBiasRec', 'IPBiasRec', 'IBLRes', 'VN', 'INFB', 'VNFoll', 'IPLoad', 'VNComp']
    data_dict = {key:[[],[],[],[],[]] for key in keys}
    
    for root, dirs, files in os.walk(path):
        if root[-9:] == "dac_power":
            measurement = os.path.basename(os.path.dirname(root[:-10]))
            for lower_root, lower_dirs, lower_files in os.walk(root):
                key = os.path.basename(lower_root)
                csv_files = [file for file in lower_files if file.endswith('.csv')]
                if len(csv_files) != 0:
                    df = pd.read_csv(f'{lower_root}/{csv_files[-1]}', skipinitialspace=True)
                    data_dict[key][0].append(df['DAC_measured'].values*5/4.735)
                    data_dict[key][1].append(df['DAC_set_value'].values)
                    data_dict[key][2].append(df['vdda_curr'].values)
                    data_dict[key][3].append(df['vddd_curr'].values)
                    data_dict[key][4].append(measurement)
    
    
    pdf_path = f'{path}/DAC_comparison.pdf'
    with PdfPages(pdf_path) as pdf:
        for key in keys:
            fig, ax = plt.subplots()
            for i in range(len(data_dict[key][0])):
                ax.errorbar(data_dict[key][1][i], data_dict[key][0][i], yerr=0.005 + 0.001*data_dict[key][0][i], marker='.', label = data_dict[key][4][i])	
            ax.set_ylim(np.min(data_dict[key][0])-0.1, np.max(data_dict[key][0])+0.1)
            ax.set_title(f'DAC analysis: {key}', fontsize = 30)
            ax.set_xlabel('DAC_value / DAC', ha='right', x=1)
            ax.set_ylabel('DAC_measured / V', ha='right', y=1)
            ax.grid()
            ax.minorticks_on()
            # handles, labels = plt.gca().get_legend_handles_labels()
            # order = [3,0,1,2]
            # ax.legend([handles[idx] for idx in order],[labels[idx] for idx in order], loc='best')
            pdf.savefig(fig)
            plt.close(fig)
            
    

try:
    test_path = f'{os.path.dirname(__file__)}/output_data/tid/Max/'
    start = time.time()
    DAC_comparison_plot(test_path)
    end = time.time()
    print(f"Time taken: {end - start:.4g} seconds")






except KeyboardInterrupt:
    print("Program interrupted by user.")
except serial.SerialException as error:
    print(f"Serial error: {error}")
except Exception as exception:
    print(f"An error occurred: {exception}")



