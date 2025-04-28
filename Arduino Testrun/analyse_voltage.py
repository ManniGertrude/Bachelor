import csv
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

# Datei einlesen
file_path = 'ArdiTesti/verify_voltage.csv'

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
errors = abs(pin_values - v0_values[:, None])  # Abweichung von V0

# Kombiniere die Daten aller Pins für den Curve-Fit
combined_v0 = np.repeat(v0_values, pin_values.shape[1])  # Wiederhole V0 für jeden Pin
combined_errors = errors.flatten()  # Flache die Fehlerdaten zu einem 1D-Array ab

# Fit-Funktion definieren
def linear_fit(x, a, b):
    return a * x + b

# Curve-Fit für alle Pins zusammen durchführen
popt, pcov = curve_fit(linear_fit, combined_v0, combined_errors)

# Fit-Ergebnisse ausgeben
print(f"Fit-Ergebnisse: a = {popt[0]:.4g}, b = {popt[1]:.4g}")
print(f"Kovarianzmatrix:{np.sqrt(np.diag(pcov))}")

# Fit-Linie berechnen
fit_x = np.linspace(min(v0_values), max(v0_values), 100)
fit_y = linear_fit(fit_x, *popt)

# Grafische Darstellung
plt.figure(figsize=(12, 8))

# Fehler für jeden Pin plotten
for pin_index in range(errors.shape[1]):
    plt.errorbar(x=v0_values, y=errors[:, pin_index], xerr=0.001, yerr=(0.005 + 0.0005 * v0_values),
                 label=f'Pin A{pin_index}', linestyle='none', capsize=3)

# Fit-Linie plotten
plt.plot(fit_x, fit_y, 'r-', label=f'Gesamt-Fit (a={popt[0]:.3f}, b={popt[1]:.3f})')

# Diagramm beschriften
plt.title('Spannungsvergleich der Pins gegen $V_0$')
plt.xlabel('Angelegte Spannung (V)')
plt.ylabel('Abweichung der gemessenen Spannung (V)')
plt.legend()
plt.xscale('log')
plt.grid()
plt.savefig('ArdiTesti/analyse_voltage.pdf')
plt.show