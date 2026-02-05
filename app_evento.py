import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="5 Anos - Financeiro", layout="wide", page_icon="💈") 
# Mudei layout para "wide" para caber a tabela financeira

# --- CONFIGURAÇÕES DO DONO (EDITE AQUI) ---
ARQUIVO_DADOS = 'lista_interessados.csv'
SENHA_ADMIN = "barba123"
NUMERO_BARBEIRO = "5519999999999" # SEU NÚMERO AQUI
PRECO_CAMISA = 45.00

# --- FUNÇÕES (BACKEND) ---
def carregar_dados():
    # Colunas padrão que o sistema precisa
    colunas_padrao = [
        "Nome", "Telefone", "Quer_Camisa", "Data_Confirmacao", 
        "Status_Pagamento", "Forma_Pagamento", "Parcelamento", "Valor_Ja_Pago", "Observacoes"
    ]
    
    if not os.path.exists(ARQUIVO_DADOS):
        return pd.DataFrame(columns=colunas_padrao)
    
    df = pd.read_csv(ARQUIVO_DADOS)
    
    # Verifica se faltam colunas novas (caso venha de uma versão anterior) e cria elas
    for col in colunas_padrao:
        if col not in df.columns:
            df[col] = "" # Cria a coluna vazia
            if col == "Valor_Ja_Pago":
                df[col] = 0.0 # Garante que seja número
                
    return df

def atualizar_lista_completa(df_novo):
    df_novo.to_csv(ARQUIVO_DADOS, index=False)

def salvar_novo_inscrito(novo_dado):
    df = carregar_dados()
    # Adiciona campos vazios de pagamento para o novo inscrito
    novo_dado["Status_Pagamento"] = "Pendente"
    novo_dado["Forma_Pagamento"] = "-"
    novo_dado["Parcelamento"] = "-"
    novo_dado["Valor_Ja_Pago"] = 0.0
    novo_dado["Observacoes"] = ""
    
    df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)
    df.to_csv(ARQUIVO_DADOS, index=False)

def gerar_link_whatsapp(nome, quer_camisa):
    texto_camisa = "e vou querer a CAMISA dos 5 Anos!" if quer_camisa == "Sim" else "sem a camisa por enquanto."
    mensagem = f"Fala Douglas! Aqui é o {nome}. Recebi o convite dos 5 ANOS e confirmo minha presença! {texto_camisa}"
    mensagem_encoded = urllib.parse.quote(mensagem)
    return f"https://wa.me/{NUMERO_BARBEIRO}?text={mensagem_encoded}"

# --- INTERFACE (FRONTEND) ---

# --- CABEÇALHO ---
col_esq, col_centro, col_dir = st.columns([1, 6, 1])
with col_centro:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    st.markdown("<h1 style='text-align: center; color: #E67E22; margin: 0;'>COMEMORAÇÃO DE 5 ANOS</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #555;'>BARBEARIA VASQUES</h3><hr>", unsafe_allow_html=True)

# Aviso Público
st.info("**Você faz parte dessa história!** Esses 5 anos não existiriam sem você. Vamos comemorar!")

# Destaque Rateio
st.markdown("""
<div style='background-color: #FFF3CD; padding: 10px; border-radius: 10px; border: 1px solid #FFEEBA; text-align: center; margin-bottom: 20px;'>
    <h4 style='color: #856404; margin:0;'>💰 IMPORTANTE: O valor do rateio depende do número de confirmados.</h4>
</div>
""", unsafe_allow_html=True)

aba_convite, aba_admin = st.tabs(["✅ Confirmar Presença", "🔒 Gestão & Financeiro"])

# --- ABA 1: CONVITE ---
with aba_convite:
    st.write("### Garanta seu lugar")
    with st.form("form_interesse"):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome Completo")
        telefone = col2.text_input("WhatsApp")
        
        preco_formatado = f"{PRECO_CAMISA:.2f}".replace(".", ",")
        st.markdown(f"#### 👕 Camisa Comemorativa (Aprox. R$ {preco_formatado})")
        opcao_camisa = st.radio("Deseja a camisa?", ["Sim, quero a camisa!", "Não, apenas o evento."], index=None)
        
        if st.form_submit_button("Confirmar Presença"):
            if nome and telefone and opcao_camisa:
                status_camisa = "Sim" if "Sim" in opcao_camisa else "Não"
                novo_registro = {
                    "Nome": nome, 
                    "Telefone": telefone, 
                    "Quer_Camisa": status_camisa, 
                    "Data_Confirmacao": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                salvar_novo_inscrito(novo_registro)
                link_zap = gerar_link_whatsapp(nome, status_camisa)
                st.success(f"Show, {nome}! Registrado.")
                st.markdown(f'<a href="{link_zap}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; width:100%; font-weight:bold;">📲 AVISAR NO WHATSAPP</button></a>', unsafe_allow_html=True)
            else:
                st.error("Preencha tudo!")

# --- ABA 2: FINANCEIRO E GESTÃO ---
with aba_admin:
    st.write("🔐 Acesso Restrito")
    senha = st.text_input("Senha Admin", type="password")
    
    if senha == SENHA_ADMIN:
        df = carregar_dados()
        st.divider()
        
        # --- BLOCO 1: CALCULADORA DE RATEIO ---
        st.subheader("1. Definição de Preço (Rateio)")
        col_custo1, col_custo2, col_result = st.columns(3)
        custo_chacara = col_custo1.number_input("Custo Chácara", value=1500.0)
        custo_bebida = col_custo2.number_input("Custo Bebida/Extra", value=300.0)
        
        total_pessoas = len(df)
        if total_pessoas > 0:
            custo_cabeca = (custo_chacara + custo_bebida) / total_pessoas
            col_result.metric("Custo Sugerido (Pessoa)", f"R$ {custo_cabeca:.2f}")
        else:
            col_result.warning("Sem inscritos")

        st.divider()

        # --- BLOCO 2: SIMULADOR DE PARCELAS ---
        st.subheader("2. Simulador de Parcelamento (Balcão)")
        with st.expander("🧮 Abrir Calculadora de Parcelas"):
            c1, c2, c3 = st.columns(3)
            val_total = c1.number_input("Valor a cobrar (R$)", value=100.0)
            qtd_parc = c2.number_input("Qtd Parcelas", min_value=1, max_value=12, value=3)
            val_parc = val_total / qtd_parc
            c3.metric(f"Valor da Parcela ({qtd_parc}x)", f"R$ {val_parc:.2f}")
            st.caption("Use isso para combinar com o cliente na hora.")

        st.divider()

        # --- BLOCO 3: FLUXO DE CAIXA (TABELA) ---
        st.subheader("3. Controle de Pagamentos")
        
        # Métricas Financeiras
        total_recebido = df["Valor_Ja_Pago"].sum()
        pagantes_quitados = len(df[df["Status_Pagamento"] == "Quitado"])
        
        m1, m2, m3 = st.columns(3)
        m1.metric("💰 Total em Caixa", f"R$ {total_recebido:.2f}")
        m2.metric("✅ Pessoas Quitadas", pagantes_quitados)
        m3.metric("📝 Total na Lista", total_pessoas)

        st.write("### Lista de Convidados & Financeiro")
        st.info("Edite os pagamentos abaixo e clique em SALVAR no final.")
        
        # Tabela Super Editável
        df_editavel = st.data_editor(
            df,
            key="editor_financeiro",
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Nome": st.column_config.TextColumn("Nome", disabled=True), # Nome travado pra evitar erro
                "Quer_Camisa": st.column_config.TextColumn("Camisa?", disabled=True, width="small"),
                
                "Status_Pagamento": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Pendente", "Em Aberto", "Quitado"],
                    required=True,
                    width="medium"
                ),
                "Forma_Pagamento": st.column_config.SelectboxColumn(
                    "Forma",
                    options=["-", "PIX", "Dinheiro", "Cartão Crédito", "Cartão Débito"],
                    width="medium"
                ),
                "Parcelamento": st.column_config.SelectboxColumn(
                    "Vezes",
                    options=["-", "À Vista", "2x", "3x", "4x"],
                    width="small"
                ),
                "Valor_Ja_Pago": st.column_config.NumberColumn(
                    "Recebido (R$)",
                    format="R$ %.2f",
                    min_value=0,
                    width="medium"
                ),
                "Observacoes": st.column_config.TextColumn(
                    "Obs (Ex: Pagou 1/3)",
                    width="large"
                )
            },
            hide_index=True
        )

        if st.button("💾 SALVAR DADOS FINANCEIROS"):
            atualizar_lista_completa(df_editavel)
            st.success("Financeiro Atualizado com Sucesso!")
            st.rerun()

    else:
        if senha: st.error("Senha incorreta")
