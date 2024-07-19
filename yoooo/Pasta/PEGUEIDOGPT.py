import pandas as pd

# Leitura do arquivo CSV
df = pd.read_csv('C:/Users/CaioSergio/Desktop/yoooo/dados_teste_rpm.csv')

# Substituição dos valores de RPM maiores que 1570 por 1500
df['RPM'] = df['RPM'].apply(lambda x: 1500 if x > 1570 else x)

# Salvar o dataframe modificado em um novo arquivo CSV
df.to_csv('arquivo_modificado.csv', index=False)

print("Arquivo processado e salvo como 'arquivo_modificado.csv'")
