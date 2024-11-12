import streamlit as st
import pandas as pd
from pandas.tseries.offsets import BMonthEnd

# Credenciais de login
CORRECT_USERNAME = "Legatus123"
CORRECT_PASSWORD = "Legatus123"

# Função de login
def login():
    st.title("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
            st.session_state["logged_in"] = True
        else:
            st.error("Usuário ou senha incorretos.")

# Funções de Cálculo para as Opções de Hedge e Swap/NDF

# Cálculo para crédito com hedge
def calcular_com_hedge(valor, taxa_juros, prazo_meses):
    return valor * (1 + (taxa_juros / 12)) ** prazo_meses

# Cálculo para crédito sem hedge (ajustado para incluir taxa de câmbio)
def calcular_sem_hedge(valor, taxa_juros, prazo_meses, taxa_cambio):
    return valor * (1 + (taxa_juros / 12)) ** prazo_meses * taxa_cambio

# Cálculo de swap com taxa de swap específica
def calcular_com_swap(valor, taxa_swap, prazo_meses):
    return valor * (1 + (taxa_swap / 12)) ** prazo_meses

# Cálculo de NDF com taxa específica de NDF
def calcular_com_ndf(valor, taxa_ndf, prazo_meses):
    return valor * (1 + (taxa_ndf / 12)) ** prazo_meses

# Função para calcular a data do próximo pagamento em dias úteis com base na frequência de pagamento
def calcular_proxima_data(data_inicial, frequencia):
    frequencias = {
        'Mensal': 1,
        'Bimestral': 2,
        'Trimestral': 3,
        'Semestral': 6,
        'Anual': 12
    }
    meses = frequencias[frequencia]
    return data_inicial + BMonthEnd() * meses

# Função para gerar o cronograma de pagamentos com base na frequência e em dias úteis
def gerar_cronograma(valor, taxa_juros_mensal, prazo_meses, data_inicial, frequencia):
    saldo_devedor = valor
    cronograma = []

    # Número de períodos de pagamento de acordo com a frequência selecionada
    num_pagamentos = prazo_meses // (12 // {'Mensal': 12, 'Bimestral': 6, 'Trimestral': 4, 'Semestral': 2, 'Anual': 1}[frequencia])
    amortizacao = valor / num_pagamentos

    for periodo in range(1, num_pagamentos + 1):
        juros_periodo = saldo_devedor * taxa_juros_mensal
        pagamento_total = juros_periodo + amortizacao
        saldo_devedor -= amortizacao

        cronograma.append({
            'Período': periodo,
            'Data de Pagamento': data_inicial,
            'Saldo Devedor Inicial': saldo_devedor + amortizacao,
            'Juros do Período': juros_periodo,
            'Amortização': amortizacao,
            'Pagamento Total': pagamento_total,
            'Saldo Devedor Final': saldo_devedor
        })
        
        # Calcular a próxima data de pagamento
        data_inicial = calcular_proxima_data(data_inicial, frequencia)
    
    return pd.DataFrame(cronograma)

# Tela principal do aplicativo
def main():
    st.title('Simulador de Crédito 4131 com Opções de Hedge e Swap/NDF e Cronograma de Pagamentos')

    # Entrada de Dados pelo Usuário
    st.sidebar.header('Parâmetros de Entrada')
    valor = st.sidebar.number_input('Valor do Crédito (R$)', min_value=0.0, value=1000.0, step=100.0)
    taxa_juros = st.sidebar.number_input('Taxa de Juros Anual (%)', min_value=0.0, value=5.0, step=0.1) / 100
    prazo_meses = st.sidebar.number_input('Prazo (em meses)', min_value=1, value=12, step=1)
    data_inicial = st.sidebar.date_input('Data Inicial do Crédito')
    frequencia = st.sidebar.selectbox('Frequência de Pagamento', ['Mensal', 'Bimestral', 'Trimestral', 'Semestral', 'Anual'])
    taxa_cambio = st.sidebar.number_input('Taxa de Câmbio', min_value=0.0, value=5.0, step=0.1)
    taxa_swap = st.sidebar.number_input('Taxa Swap (%)', min_value=0.0, value=3.0, step=0.1) / 100
    taxa_ndf = st.sidebar.number_input('Taxa NDF (%)', min_value=0.0, value=2.0, step=0.1) / 100

    # Seleção do Tipo de Simulação
    opcao_calculo = st.selectbox('Escolha o Tipo de Simulação', ('Com Hedge', 'Sem Hedge', 'Com Swap', 'Com NDF'))

    # Realização dos Cálculos com Base na Opção Selecionada
    taxa_juros_mensal = taxa_juros / 12  # Converter taxa anual para mensal
    if opcao_calculo == 'Com Hedge':
        resultado = calcular_com_hedge(valor, taxa_juros, prazo_meses)
        st.write(f'Resultado da simulação com hedge: R$ {resultado:,.2f}')
        cronograma = gerar_cronograma(valor, taxa_juros_mensal, prazo_meses, pd.to_datetime(data_inicial), frequencia)

    elif opcao_calculo == 'Sem Hedge':
        resultado = calcular_sem_hedge(valor, taxa_juros, prazo_meses, taxa_cambio)
        st.write(f'Resultado da simulação sem hedge: R$ {resultado:,.2f}')
        cronograma = gerar_cronograma(valor, taxa_juros_mensal, prazo_meses, pd.to_datetime(data_inicial), frequencia)

    elif opcao_calculo == 'Com Swap':
        taxa_swap_mensal = taxa_swap / 12  # Converter taxa swap anual para mensal
        resultado = calcular_com_swap(valor, taxa_swap, prazo_meses)
        st.write(f'Resultado da simulação com swap: R$ {resultado:,.2f}')
        cronograma = gerar_cronograma(valor, taxa_swap_mensal, prazo_meses, pd.to_datetime(data_inicial), frequencia)

    elif opcao_calculo == 'Com NDF':
        taxa_ndf_mensal = taxa_ndf / 12  # Converter taxa NDF anual para mensal
        resultado = calcular_com_ndf(valor, taxa_ndf, prazo_meses)
        st.write(f'Resultado da simulação com NDF: R$ {resultado:,.2f}')
        cronograma = gerar_cronograma(valor, taxa_ndf_mensal, prazo_meses, pd.to_datetime(data_inicial), frequencia)

    # Exibição do Cronograma de Pagamentos
    st.header('Cronograma de Pagamentos')
    st.write(cronograma)

# Controle de estado para o login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Exibir a tela de login ou a tela principal com base no estado de login
if st.session_state["logged_in"]:
    main()
else:
    login()
