import csv
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

# Datei einlesen
file_path = 'Arduino Testrun/verify_voltage.csv'

# Daten speichern
v0_values = []
pin_values = []

with open(file_path, 'r') as csvfile:
    reader = csv.reader(csvfile)
    headers = next(reader)  # Überspringe die Kopfzeile
    
    for row in reader:
        # Überspringe leere oder ungültige Zeilen
        if not row or any(cell.strip() == '' for cell in row):
            continue
        try:
            v0_values.append(float(row[0]))  # Grundwert (V0)
            pin_values.append([float(value) for value in row[1:]])  # Werte der Pins
        except ValueError:
            print(f"Ungültige Zeile übersprungen: {row}")
            continue

# Fehlerberechnung
v0_values = np.array(v0_values)
pin_values = np.array(pin_values)

print(v0_values)
# Fit-Funktion definieren
def linear_fit(x, a, b):
    return a * x + b

# Curve-Fit für alle Pins zusammen durchführen
popt, pcov = curve_fit(linear_fit, )
popt_err = np.sqrt(np.diag(pcov))
# Fit-Ergebnisse ausgeben
print(f"Fit-Ergebnisse: a = {popt[0]:.4g}, b = {popt[1]:.4g}")
print(f"Kovarianzmatrix:{popt_err}")

# Fit-Linie berechnen
fit_x = np.linspace(min(v0_values), max(v0_values), 100)
fit_y = linear_fit(fit_x, *popt)

# Fehler für jeden Pin plotten
for pin_index in range(pin_values.shape[1]):
    plt.errorbar(x=v0_values, y=pin_values[:, pin_index], xerr=0.001, yerr=(0.005 + 0.0005 * v0_values),
                linestyle='none', capsize=3)

# Fit-Linie plotten
plt.plot(fit_x, fit_y, 'r-', label=f'Gesamt-Fit $(a={popt[0]:.4f}\pm{popt_err[0]:.4f}, b={popt[1]:.4f}\pm{popt_err[1]:.4f})$')

# Diagramm beschriften
plt.title('Spannungsvergleich der Pins gegen $V_0$')
plt.xlabel('Angelegte Spannung (V)')
plt.ylabel('Abweichung der gemessenen Spannung (V)')
plt.legend()
plt.xscale('log')
plt.grid()
plt.savefig('Arduino Testrun/analyse_voltage.pdf')
plt.show