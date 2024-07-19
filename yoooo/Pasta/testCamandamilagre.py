import serial
import csv

# Configurações da porta serial (ajuste conforme necessário)
porta_serial = "COM4"  # Exemplo de porta serial, ajuste para o seu caso
baud_rate = 115200  # Taxa de baud do Arduino, ajuste conforme necessário

# Inicializa a conexão serial
arduino = serial.Serial(porta_serial, baud_rate, timeout=1)

# Abre o arquivo CSV para escrita
with open("dados_1400pwm_CERTO.csv", mode="w", newline="") as arquivo_csv:
    csv_writer = csv.writer(arquivo_csv)
    csv_writer.writerow(["PWM", "RPM"])

    # Loop para ler e processar os dados do Arduino
    while True:
        # Lê uma linha da porta serial
        linha = arduino.readline().decode("utf-8").strip()

        # Verifica se a linha não está vazia
        if linha:
            # Divide a linha pelos caracteres vírgula para separar tempo e rpm
            tempo_str, rpm_str = linha.split(",")

            # Converte os valores para float (ou int) se necessário
            tempo = float(tempo_str)
            rpm = float(rpm_str)

            # Escreve os dados no arquivo CSV
            csv_writer.writerow([tempo, rpm])

            # Exibe os dados lidos no console (opcional)
            print(f"PWM: {tempo} , RPM: {rpm}")