import matplotlib.pyplot as plt
import pandas as pd
import os
import shutil
from matplotlib.backends.backend_pdf import PdfPages



pathtest = f'{os.path.dirname(__file__)}/data'


def arduino_power_plot(path, output_path, infostring=None):
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
                
                df = pd.read_csv(f'{root}/{data_file}')
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

                ax1.legend(handles, labels,  title = infostring, loc='upper left')
                ax1.set_ylim(0, max(df['DAC_measured'].values*5/4.735)*1.05)
                
                ax1.grid()
                pdf.savefig(fig, bbox_inches='tight')
                plt.close(fig)
    
    timestamps.sort(reverse=True)
    shutil.copy(pdf_path, f'{output_path}/{timestamps[0]}.pdf')

infostring_t = f'temp = 5°C \n HV = -81V'
arduino_power_plot(pathtest, pathtest, infostring_t)