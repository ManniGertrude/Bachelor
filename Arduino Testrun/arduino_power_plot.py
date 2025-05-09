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
                ax2.plot(df['DAC_Value_lit'].values, 1000*df['vdda_curr'].values, color = 'navy', label='vdda current', marker='^', alpha=0.8)
                ax2.plot(df['DAC_Value_lit'].values, 1000*df['vddd_curr'].values, color = 'slateblue', label='vddd current', marker='p', alpha=0.8)    
                ax1.plot(df['DAC_Value_lit'].values, df['DAC_Value_exp'].values*5/4.735, color = 'crimson', label='real DAC voltage', marker='o', alpha=0.8)
                
                handles1, labels1 = ax1.get_legend_handles_labels()
                handles2, labels2 = ax2.get_legend_handles_labels()
                handles = handles1 + handles2
                labels = labels1 + labels2
                
                ax1.set_title(f'DAC value analysis and powermonitoring', color = TITLE_COLOR, fontsize=14)
                ax1.set_xlabel('set DAC voltage / ?', fontsize=12)
                ax1.set_ylabel('real DAC voltage / V', color = 'crimson', fontsize=12)
                ax2.set_ylabel('supplied current / mA', color = 'navy', fontsize = 12)

                ax1.tick_params(axis='y', labelcolor='crimson')
                ax2.tick_params(axis='y', labelcolor='navy')

                ax1.legend(handles, labels,  title = infostring, loc='upper left')
                ax1.set_ylim(0, 1.2)
                
                # fig.text(0.1, 0.92, "Run2021", fontsize=12, color=TEXT_COLOR)
                # fig.text(0.7, 0.92, 'bla bla bla', fontsize=12, color=TEXT_COLOR)
                
                ax1.grid()
                pdf.savefig(fig, bbox_inches='tight')
                plt.close(fig)
    
    timestamps.sort(reverse=True)
    shutil.copy(pdf_path, f'{output_path}/{timestamps[0]}.pdf')

infostring_t = f'temp = 5°C \n HV = -81V'
arduino_power_plot(pathtest, pathtest, infostring_t)