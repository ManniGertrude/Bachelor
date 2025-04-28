# This script reads voltage values from two Arduino devices connected via serial ports.
# It collects the values from each pin and saves them into a CSV file.
# The script waits for the user to press Enter before reading the next value, allowing for manual control over the data collection process.
import serial
import csv
import time

ser_L = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser_R = serial.Serial('/dev/ttyACM1', 9600, timeout=1)

try:
    # Ignoriere die erste Zeile von jedem Arduino (Arduino-ID)
    ser_L.readline()
    ser_R.readline()

    with open('ArdiTesti/temp_daten.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12", "A13", "A14", "A15"])
        
        collected_values = []  # Liste zum Sammeln der Werte
        pin_index = 0  # Start mit dem ersten Pin
        while True:
            input("Drücke Enter, um den nächsten Wert zu speichern...")  # Warten auf Knopfdruck (Enter-Taste)
            
            # Leere den Eingabepuffer, um nur die neuesten Daten zu lesen
            ser_L.reset_input_buffer()
            ser_R.reset_input_buffer()
            time.sleep(0.1)  # Kurze Pause, um sicherzustellen, dass die neuesten Daten bereit sind
            
            line_L = ser_L.readline().decode('utf-8').strip()
            line_R = ser_R.readline().decode('utf-8').strip()
            
            if line_L and line_R:
                # Split die Werte
                values_L = line_L.split(',')
                values_R = line_R.split(',')
                combined_values = values_L + values_R
                
                # Nur den aktuellen Pin-Wert speichern
                if len(combined_values) != 16 and pin_index < 16:
                    print(f"Nur {len(combined_values)} Werte wurden übermittelt.")
                elif pin_index < len(combined_values):
                    collected_values.append(combined_values[pin_index])  # Wert zur Liste hinzufügen
                    print(f"Gespeicherter Wert für Pin A{pin_index}: {combined_values[pin_index]} V")
                    print(combined_values)
                    pin_index += 1  # Zum nächsten Pin wechseln
                else:
                    print("Alle Pins wurden bereits gespeichert.")
                    break


        # Schreibe alle gesammelten Werte in einer Zeile in die CSV-Datei
        writer.writerow(collected_values)
except KeyboardInterrupt:
    print("Programm durch Benutzer beendet.")
finally:
    ser_L.close()
    ser_R.close()