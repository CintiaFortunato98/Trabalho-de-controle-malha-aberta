import csv
import matplotlib.pyplot as plt

# Nome do arquivo CSV
input_file = 'motor1_data.csv'

# Listas para armazenar os dados
times = []
errors = []
speeds = []
pwm_inputs = []

# Lê os dados do arquivo CSV
with open(input_file, 'r') as csvfile:
    csvreader = resultados3 - resultados3.csv.reader(csvfile)
    next(csvreader)  # Pula a linha de cabeçalho

    for row in csvreader:
        times.append(float(row[0]))
        errors.append(float(row[1]))
        speeds.append(int(row[2]))
        pwm_inputs.append(float(row[3]))

# Plota os dados
plt.figure(figsize=(10, 5))

plt.subplot(3, 1, 1)
plt.plot(times, errors, label='Erro')
plt.xlabel('Tempo (s)')
plt.ylabel('Erro')
plt.legend()

plt.subplot(3, 1, 2)
plt.plot(times, speeds, label='Velocidade (RPM)', color='r')
plt.xlabel('Tempo (s)')
plt.ylabel('Velocidade (RPM)')
plt.legend()

plt.subplot(3, 1, 3)
plt.plot(times, pwm_inputs, label='Input PWM', color='g')
plt.xlabel('Tempo (s)')
plt.ylabel('Input PWM')
plt.legend()

plt.tight_layout()
plt.show()
