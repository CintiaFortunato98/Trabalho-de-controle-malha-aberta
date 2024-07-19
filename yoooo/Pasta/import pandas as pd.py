import pandas as pd
import matplotlib.pyplot as plt

# Carregar os dados do arquivo CSV
data = pd.read_csv('dados_motor.csv')

# Plotar a resposta do sistema
plt.figure()
plt.plot(data['Time'], data['Position'], label='Resposta do Sistema')
plt.axhline(y=TARGET_POSITION, color='r', linestyle='--', label='Posição Alvo')
plt.xlabel('Tempo (ms)')
plt.ylabel('Posição')
plt.legend()
plt.title('Resposta do Motor')
plt.show()

# Calcular o overshoot
peak_position = data['Position'].max()
overshoot = ((peak_position - TARGET_POSITION) / TARGET_POSITION) * 100

print(f'Overshoot: {overshoot:.2f}%')
