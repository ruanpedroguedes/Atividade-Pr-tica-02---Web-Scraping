import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os

# Estilo dos gráficos
plt.style.use('ggplot')
sns.set(style="whitegrid")

# Criar diretório
if not os.path.exists('dados_cotacoes'):
    os.makedirs('dados_cotacoes')

# Período dos últimos 30 dias
data_fim = datetime.now().strftime('%m-%d-%Y')
data_inicio = (datetime.now() - timedelta(days=30)).strftime('%m-%d-%Y')

# Moedas
moedas = {
    'USD': 'Dólar Americano',
    'EUR': 'Euro',
    'GBP': 'Libra Esterlina',
    'JPY': 'Iene Japonês',
    'ARS': 'Peso Argentino'
}

# Dicionário para os dados
dados_cotacoes = {}

# Consulta à API
for codigo, nome in moedas.items():
    print(f"Consultando {nome} ({codigo})...")
    url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@moeda='{codigo}'&@dataInicial='{data_inicio}'&@dataFinalCotacao='{data_fim}'&$top=100&$format=json"

    response = requests.get(url)

    if response.status_code == 200:
        dados = response.json()
        if 'value' in dados and dados['value']:
            cotacoes = []
            for item in dados['value']:
                cotacoes.append({
                    'data': item['dataHoraCotacao'],
                    'cotacao_compra': item['cotacaoCompra'],
                    'cotacao_venda': item['cotacaoVenda']
                })
            dados_cotacoes[codigo] = {
                'nome': nome,
                'cotacoes': cotacoes
            }
            print(f"  ✓ Obtidas {len(cotacoes)} cotações.")
        else:
            print("  ✗ Nenhum dado encontrado.")
    else:
        print(f"  ✗ Erro {response.status_code}")

for codigo, dados in dados_cotacoes.items():
    if dados['cotacoes']:
        df = pd.DataFrame(dados['cotacoes'])
        df['data'] = pd.to_datetime(df['data'])
        df = df.sort_values('data')

        caminho_csv = f'dados_cotacoes/cotacao_{codigo}.csv'
        df.to_csv(caminho_csv, index=False, encoding='utf-8-sig')

        print(f"  ✓ Arquivo '{caminho_csv}' criado com sucesso!")

plt.figure(figsize=(14, 8))
for codigo, dados in dados_cotacoes.items():
    if dados['cotacoes']:
        df = pd.DataFrame(dados['cotacoes'])
        df['data'] = pd.to_datetime(df['data'])
        df = df.sort_values('data')
        plt.plot(df['data'], df['cotacao_venda'], label=f"{dados['nome']} ({codigo})")

plt.title('Cotação de Moedas - Últimos 30 dias', fontsize=16)
plt.xlabel('Data')
plt.ylabel('Valor em R$')
plt.legend()
plt.grid(True)
plt.tight_layout()

arquivo_grafico = 'dados_cotacoes/grafico_todas_moedas.png'
plt.savefig(arquivo_grafico, dpi=300)
print(f"  ✓ Gráfico '{arquivo_grafico}' criado com sucesso!")

for codigo, dados in dados_cotacoes.items():
    if dados['cotacoes']:
        plt.figure(figsize=(12, 6))
        df = pd.DataFrame(dados['cotacoes'])
        df['data'] = pd.to_datetime(df['data'])
        df = df.sort_values('data')
        plt.plot(df['data'], df['cotacao_compra'], label='Compra', color='green')
        plt.plot(df['data'], df['cotacao_venda'], label='Venda', color='red')

        plt.title(f'Cotação do {dados["nome"]} ({codigo})', fontsize=16)
        plt.xlabel('Data')
        plt.ylabel('Valor em R$')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        arquivo = f'dados_cotacoes/grafico_{codigo}.png'
        plt.savefig(arquivo, dpi=300)
        print(f"  ✓ Gráfico '{arquivo}' criado com sucesso!")

plt.figure(figsize=(12, 7))

variacoes = []
nomes = []

for codigo, dados in dados_cotacoes.items():
    if dados['cotacoes'] and len(dados['cotacoes']) >= 2:
        df = pd.DataFrame(dados['cotacoes'])
        df['data'] = pd.to_datetime(df['data'])
        df = df.sort_values('data')

        inicio = df.iloc[0]['cotacao_venda']
        fim = df.iloc[-1]['cotacao_venda']
        variacao_pct = ((fim - inicio) / inicio) * 100

        variacoes.append(variacao_pct)
        nomes.append(f"{dados['nome']} ({codigo})")

cores = ['green' if var >= 0 else 'red' for var in variacoes]
plt.bar(nomes, variacoes, color=cores)
plt.axhline(0, color='black', linestyle='--', alpha=0.4)

for i, v in enumerate(variacoes):
    plt.text(i, v + (0.5 if v >= 0 else -1.5), f"{v:.2f}%", ha='center')

plt.title('Variação Percentual das Moedas', fontsize=16)
plt.ylabel('Variação (%)')
plt.tight_layout()

arquivo = 'dados_cotacoes/grafico_variacao_percentual.png'
plt.savefig(arquivo, dpi=300)
print(f"  ✓ Gráfico '{arquivo}' criado com sucesso!")
