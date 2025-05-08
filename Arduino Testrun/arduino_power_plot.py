import matplotlib.pyplot as plt
import pandas as pd
import os
import shutil
from matplotlib.backends.backend_pdf import PdfPages



pathtest = f'{os.path.dirname(__file__)}/data'


def arduino_power_plot(path, output_path, Temp, HV):
    pdf_path = f'{output_path}/latest.pdf'
    with PdfPages(pdf_path) as pdf:
        timestamps = []
        for root, dirs, files in os.walk(path):
            csv_files = [file for file in files if file.endswith('.csv')]
            if len(csv_files) > 0:
                # Sort files by timestamp
                csv_files.sort(reverse=True)
                timestamps.append(csv_files[0][-19:-4])
                data_file = csv_files[0]
                
                fig, ax1 = plt.subplots()
                ax2 = ax1.twinx()
                
                df = pd.read_csv(f'{root}/{data_file}')
                ax2.scatter(df['DAC_Value_lit'], 1000*df['vdda_curr'], color = 'navy', label='vdda current', marker='^', alpha=0.8)
                ax2.scatter(df['DAC_Value_lit'], 1000*df['vddd_curr'], color = 'slateblue', label='vddd current', marker='p', alpha=0.8)    
                ax1.scatter(df['DAC_Value_lit'], df['DAC_Value_exp'], label=f'{df["dac_name"][0]} voltage', marker='X', color='r', alpha=0.8)
                
                handles1, labels1 = ax1.get_legend_handles_labels()
                handles2, labels2 = ax2.get_legend_handles_labels()
                handles = handles1 + handles2
                labels = labels1 + labels2
                
                ax1.set_xlabel('set DAC voltage [ ]', fontsize=12)
                ax2.set_ylabel('supplied current [mA]', color = 'navy', fontsize = 12)
                ax1.set_ylabel('real DAC voltage [ ]', color = 'r', fontsize=12)
                ax1.tick_params(axis='y', labelcolor='r')
                ax2.tick_params(axis='y', labelcolor='navy')
                ax1.legend(handles, labels)
                plt.legend([f'temp = {Temp}°C', f'HV = {HV}V'], loc='lower right', markerscale = 0, framealpha=0.5)
                ax1.grid()
                pdf.savefig(fig, bbox_inches='tight')
                plt.close(fig)
    timestamps.sort(reverse=True)
    shutil.copy(pdf_path, f'{output_path}/{timestamps[0]}.pdf')

arduino_power_plot(pathtest, pathtest, 1, 1)