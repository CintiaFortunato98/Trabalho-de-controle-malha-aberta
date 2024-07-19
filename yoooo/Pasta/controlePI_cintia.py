import serial
import matplotlib.pyplot as plt
import csv
import numpy as np

# Configurações da porta serial (ajuste conforme necessário)
porta_serial = 'COM4'  # Porta que o Arduino está conectado
baud_rate = 9600

resultados = {'tempo': [], 'erro': [], 'velocidade': []}

# Inicializa a conexão serial com timeout
ser = serial.Serial(porta_serial, baud_rate, timeout=1)

# Loop para ler os resultados da porta serial
while len(resultados['tempo']) < 3000:
    # Verifica se há resultados disponíveis na porta serial
    if ser.in_waiting > 0:
        try:
            # Lê uma linha da porta serial
            line_data = ser.readline().decode('utf-8').strip()
            
            # Divide a linha de resultados em tempo, erro e velocidade
            leitura = line_data.split(',')
            if len(leitura) == 3:
                resultados['tempo'].append(float(leitura[0]))
                resultados['erro'].append(float(leitura[1]))
                resultados['velocidade'].append(float(leitura[2]))
        except ValueError:
            # Se não puder converter para float, ignora a linha
            pass
        except IndexError:
            # Se não houver elementos suficientes na linha, ignora a linha
            pass
    else:
        print("Aguardando resultados...")

# Remove as 5 primeiras amostras, se necessário
resultados['tempo'] = resultados['tempo'][5:]
resultados['erro'] = resultados['erro'][5:]
resultados['velocidade'] = resultados['velocidade'][5:]

# Fecha a conexão serial
ser.close()

print(resultados)

# Nome do arquivo CSV
nome_arquivo = 'resultados3 - resultados4.csv.csv'

# Escreve os resultados no arquivo CSV
with open(nome_arquivo, mode='w', newline='') as arquivo_csv:
    escritor_csv = csv.writer(arquivo_csv)
    
    # Escreve os cabeçalhos
    escritor_csv.writerow(resultados.keys())
    
    # Escreve as linhas de resultados
    linhas = zip(*resultados.values())
    escritor_csv.writerows(linhas)

print(f'Dados exportados com sucesso para {nome_arquivo}')

# Leitura dos resultados do arquivo CSV (se necessário)
tempo = []
erro = []
velocidade = []

with open(nome_arquivo, mode='r') as arquivo_csv:
    leitor_csv = csv.reader(arquivo_csv)
    next(leitor_csv)  # Pula o cabeçalho
    for linha in leitor_csv:
        tempo.append(float(linha[0]))
        erro.append(float(linha[1]))
        velocidade.append(float(linha[2]))

# Plotagem dos resultados
plt.figure(figsize=(10, 5))
plt.plot(tempo, erro, label='erro')
plt.plot(tempo, velocidade, label='velocidade')

# Configurações do gráfico
plt.xlabel('tempo')
plt.ylabel('Valores')
plt.title('Gráfico de tempo vs erro e velocidade')
plt.legend()
plt.xticks(np.arange(min(tempo), max(tempo)+1, 1))  # Ajusta os ticks do eixo x de 1 em 1
plt.grid(True)

# Mostra o gráfico
plt.show()
