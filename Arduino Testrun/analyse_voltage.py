import matplotlib.pyplot as plt
import numpy as np
import scipy.odr as odr
from sklearn.metrics import r2_score
import pandas as pd
import os

def lin(Params, x):
    return Params[0] * x + Params[1]

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
    datax.append([column]*16)
    datay.append(data[column].values*4.737/5)
    datayerr.append(np.std(data[column].values)*4.737/5)
    plt.errorbar([column]*16, data[column].values*4.737/5, xerr=0.0005*column + 0.005, yerr=np.std(data[column].values)*4.737/5 , capsize=3, linestyle='None',  fmt='.', label=f'{column} V')

lin_values = np.linspace(0, 5, 10000)
odr_model = odr.Model(lin)
odr_data = odr.RealData(datax, datay, sx=0.0005*np.array(datax) + 0.005, sy=np.std(datay)*np.ones(len(datax)))
odr_fit = odr.ODR(odr_data, odr_model, beta0=[1., 0.])
odr_out = odr_fit.run()
print(odr_out.beta, odr_out.sd_beta)
print(type(odr_out.beta))
chi2 = np.sum(((lin(odr_out.beta, datax) - datay) / datayerr) ** 2)

plt.legend()
plt.plot(lin_values, lin_values, label='Theorie', color='red')
plt.plot(lin_values, lin(odr_out.beta, lin_values), label='fittet data', color='black', linestyle='--', alpha=0.8)
plt.xlabel('set value [V]', fontsize=12)
plt.ylabel('measured value [V]', fontsize=12)
plt.grid()
plt.savefig(f'{path}/analyse_voltage_lin.pdf')
plt.xscale('log')
plt.grid()
plt.savefig('ArdiTesti/analyse_voltage.pdf')
plt.show
