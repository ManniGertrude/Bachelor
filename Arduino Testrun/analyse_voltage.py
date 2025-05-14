import matplotlib.pyplot as plt
import numpy as np
import scipy.odr as odr
from sklearn.metrics import r2_score
import pandas as pd
import os

def lin(Params, x):
    return Params[0] * np.array(x) + Params[1]

plt.subplot()

# Datei einlesen
path = os.path.dirname(__file__)
file_path = f'{path}/verify_voltage.csv'

data = pd.read_csv(file_path, delimiter=',', header=0, decimal='.', index_col=0)
data = data.dropna()


data = data.T
datax = []
datay = []
datayerr = []
for column in data.columns:
    # # prints mean and std for latex table
    # print(f'{column} & {np.mean(data[column])*4.737/5:.4f} $\\pm$ {np.std(data[column].values*4.737/5):.2g} & {100*(abs(column - np.mean(data[column])*4.737/5)/column):.2g} & {max(data[column]) - min(data[column]):.3f}\\\\')
    
    # # prints raw data for latex table
    # values = []
    # for i in range(len(data[column])):
    #     values.append(f"{data[column][i]}")
    #     values.append("&")
    # values_string = " ".join(values[:-1])
    # print(f"{values_string} \\\\")
    # print([column]*16, data[column].values)
    
    # plots the data
    datax.extend([column]*16) 
    datay.extend(data[column].values*4.737/5)
    datayerr.extend([np.std(data[column].values) * 4.737 / 5] * 16)
    plt.errorbar([column]*16, data[column].values*4.737/5, xerr=0.0005*column + 0.005, yerr=np.std(data[column].values)*4.737/5 , capsize=3, linestyle='None',  fmt='.', label=f'{column} V')

lin_values = np.linspace(0, 5, 10000)
odr_model = odr.Model(lin)
odr_data = odr.RealData(datax, datay, sx=0.0005*np.array(datax) + 0.005, sy=datayerr)
odr_fit = odr.ODR(odr_data, odr_model, beta0=[1., 0.])
odr_out = odr_fit.run()
print(odr_out.beta)
print(odr_out.sd_beta)

chi2 = sum((datay - lin(odr_out.beta, datax))**2 / np.power(datayerr, 2))	
chi2_red = chi2 / (len(datay) - len(odr_out.beta))
print(f'chi2_red: {chi2:.3f}')
print(f'chi2_red: {chi2_red:.3f}')

plt.plot(lin_values, lin(odr_out.beta, lin_values), label='fittet data: $\chi^2_{red} = $' + f'{chi2_red:.3f}', color='black', linestyle='--', alpha=0.8)
plt.legend(framealpha = 0, fontsize=10, loc='upper left')
plt.title('Arduino voltage verification', fontsize=14)
plt.xlabel('voltage_measured / V', fontsize=12)
plt.ylabel('voltage_set / V', fontsize=12)
plt.grid()
plt.savefig(f'{path}/analyse_voltage_lin.pdf')
plt.xscale('log')
plt.yscale('log')
plt.grid(True)
plt.savefig(f'{path}/analyse_voltage_log.pdf', bbox_inches='tight')
plt.show
