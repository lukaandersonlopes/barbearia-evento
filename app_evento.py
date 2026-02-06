import streamlit as st
import pandas as pd
import os  # <--- O IMPORT QUE FALTAVA VOLTOU AQUI
from datetime import datetime
import urllib.parse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="5 Anos - Financeiro", layout="wide", page_icon="💈")

# --- CONFIGURAÇÕES DO DONO ---
# O NOME DA PLANILHA TEM QUE SER EXATO AO QUE ESTÁ NO GOOGLE
NOME_PLANILHA_GOOGLE = 'Barbearia 5 Anos - Dados' 
SENHA_ADMIN = "barba123"
NUMERO_BARBEIRO = "5519998057890"
PRECO_CAMISA = 45.00

# --- CONEXÃO COM GOOGLE SHEETS (O COFRE) ---
def conectar_google_sheets():
    # Pega a chave que salvamos nos Secrets do Streamlit
    try:
        # Carrega o JSON que salvamos como texto nos Secrets
        credenciais_dict = json.loads(st.secrets["GCP_KEY"])
        
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credenciais_dict, scope)
        client = gspread.authorize(creds)
        
        # Tenta abrir a planilha
        sheet = client.open(NOME_PLANILHA_GOOGLE).sheet1
        return sheet
    except Exception as e:
        st.error(f"Erro ao conectar no Google Sheets: {e}")
        st.stop()

# --- FUNÇÕES (BACKEND BLINDADO) ---
def carregar_dados():
    sheet = conectar_google_sheets()
    try:
        dados = sheet.get_all_records() # Baixa tudo da nuvem
    except:
        dados = []
    
    colunas_padrao = [
        "Nome", "Telefone", "Quer_Camisa", "Tamanho_Camisa", "Data_Confirmacao", 
        "Status_Pagamento", "Forma_Pagamento", "Parcelamento", "Valor_Ja_Pago", "Observacoes"
    ]
    
    if not dados:
        return pd.DataFrame(columns=colunas_padrao)
    
    df = pd.DataFrame(dados)
    
    # Garante colunas faltantes
    for col in colunas_padrao:
        if col not in df.columns:
            df[col] = ""

    # Faxina de Dados
    df["Valor_Ja_Pago"] = pd.to_numeric(df["Valor_Ja_Pago"], errors='coerce').fillna(0.0)
    df["Status_Pagamento"] = df["Status_Pagamento"].fillna("Pendente").replace("", "Pendente")
    df["Forma_Pagamento"] = df["Forma_Pagamento"].fillna("-").replace("", "-")
    df["Parcelamento"] = df["Parcelamento"].fillna("-").replace("", "-")
    df["Observacoes"] = df["Observacoes"].fillna("")
    df["Tamanho_Camisa"] = df["Tamanho_Camisa"].fillna("-").replace("", "-")
    
    return df

def salvar_novo_inscrito(novo_dado):
    sheet = conectar_google_sheets()
    
    # Prepara a linha na ordem correta das colunas (Importante para o Google Sheets)
    # Ordem: Nome, Telefone, Quer_Camisa, Tamanho_Camisa, Data_Confirmacao, Status, Forma, Parcelamento, Valor, Obs
    linha = [
        novo_dado["Nome"],
        novo_dado["Telefone"],
        novo_dado["Quer_Camisa"],
        novo_dado.get("Tamanho_Camisa", "-"),
        novo_dado["Data_Confirmacao"],
        "Pendente", # Status Pagamento
        "-",        # Forma Pagamento
        "-",        # Parcelamento
        0.0,        # Valor Ja Pago
        ""          # Observacoes
    ]
    
    # Se for o primeiro registro, cria o cabeçalho antes
    registros = sheet.get_all_records()
    if not registros:
        cabecalho = [
            "Nome", "Telefone", "Quer_Camisa", "Tamanho_Camisa", "Data_Confirmacao", 
            "Status_Pagamento", "Forma_Pagamento", "Parcelamento", "Valor_Ja_Pago", "Observacoes"
        ]
        sheet.append_row(cabecalho)
        
    sheet.append_row(linha) # Adiciona na nuvem

def atualizar_financeiro_completo(df_novo):
    sheet = conectar_google_sheets()
    sheet.clear() # Limpa a planilha velha
    
    # Prepara os dados para subir (Cabeçalho + Dados)
    lista_dados = [df_novo.columns.values.tolist()] + df_novo.values.tolist()
    sheet.update(lista_dados) # Sobe a nova

def gerar_link_whatsapp(nome, quer_camisa, tamanho):
    if quer_camisa == "Sim":
        texto_camisa = f"e vou querer a CAMISA dos 5 Anos (Tamanho {tamanho})!"
    else:
        texto_camisa = "sem a camisa por enquanto."
        
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

st.info("**Você faz parte dessa história!** Esses 5 anos não existiriam sem você. Vamos comemorar!")

st.markdown("""
<div style='background-color: #FFF3CD; padding: 15px; border-radius: 10px; border: 1px solid #FFEEBA; text-align: center; margin-bottom: 20px;'>
    <h4 style='color: #856404; margin:0; margin-bottom: 10px;'>⚠️ IMPORTANTE</h4>
    <p style='color: #856404; font-size: 16px; line-height: 1.5; margin: 0;'>
        O valor da participação depende do número de confirmados. 
        Entrarei em contato assim que tiver a confirmação de todos vocês para fazer a divisão correta do valor.
    </p>
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
        
        tamanho_selecionado = "-"
        if opcao_camisa == "Sim, quero a camisa!":
            st.markdown("**Selecione o tamanho (Obrigatório):**")
            tamanho_selecionado = st.selectbox("Qual o tamanho?", ["-", "P", "M", "G", "GG", "G1", "G2"], index=0)
        
        if st.form_submit_button("Confirmar Presença"):
            if nome and telefone and opcao_camisa:
                status_camisa = "Sim" if "Sim" in opcao_camisa else "Não"
                
                if status_camisa == "Sim" and tamanho_selecionado == "-":
                     st.error("⚠️ ATENÇÃO: Escolha o tamanho da camisa!")
                else:
                    novo_registro = {
                        "Nome": nome, 
                        "Telefone": telefone, 
                        "Quer_Camisa": status_camisa, 
                        "Tamanho_Camisa": tamanho_selecionado, 
                        "Data_Confirmacao": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    try:
                        salvar_novo_inscrito(novo_registro)
                        link_zap = gerar_link_whatsapp(nome, status_camisa, tamanho_selecionado)
                        st.success(f"Show, {nome}! Salvo na Nuvem com sucesso.")
                        st.markdown(f'<a href="{link_zap}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; width:100%; font-weight:bold;">📲 AVISAR NO WHATSAPP</button></a>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}. Avise o administrador.")
            else:
                st.error("Preencha todos os campos obrigatórios!")

# --- ABA 2: FINANCEIRO E GESTÃO ---
with aba_admin:
    st.write("🔐 Acesso Restrito")
    senha = st.text_input("Senha Admin", type="password")
    
    if senha == SENHA_ADMIN:
        try:
            df = carregar_dados()
        except Exception as e:
            st.error("Conecte a planilha do Google corretamente nos Secrets!")
            st.stop()
            
        st.divider()
        st.caption("✅ Sistema Conectado ao Google Sheets (Dados Seguros)")
        
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

        st.subheader("2. Simulador de Parcelamento")
        with st.expander("🧮 Abrir Calculadora de Parcelas"):
            c1, c2, c3 = st.columns(3)
            val_total = c1.number_input("Valor a cobrar (R$)", value=100.0)
            qtd_parc = c2.number_input("Qtd Parcelas", min_value=1, max_value=12, value=3)
            val_parc = val_total / qtd_parc
            c3.metric(f"Valor da Parcela ({qtd_parc}x)", f"R$ {val_parc:.2f}")

        st.divider()

        st.subheader("3. Controle de Pagamentos")
        
        total_recebido = df["Valor_Ja_Pago"].sum()
        pagantes_quitados = len(df[df["Status_Pagamento"] == "Quitado"])
        
        m1, m2, m3 = st.columns(3)
        m1.metric("💰 Total em Caixa", f"R$ {total_recebido:.2f}")
        m2.metric("✅ Pessoas Quitadas", pagantes_quitados)
        m3.metric("📝 Total na Lista", total_pessoas)

        st.write("### Lista de Convidados & Financeiro (Google Sheets)")
        st.caption("Edite abaixo e clique em SALVAR para atualizar a planilha oficial.")
        
        df_editavel = st.data_editor(
            df,
            key="editor_financeiro",
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Nome": st.column_config.TextColumn("Nome", disabled=True),
                "Quer_Camisa": st.column_config.TextColumn("Camisa?", disabled=True, width="small"),
                "Tamanho_Camisa": st.column_config.SelectboxColumn("Tam.", options=["-", "P", "M", "G", "GG", "G1", "G2"], width="small"),
                "Status_Pagamento": st.column_config.SelectboxColumn("Status", options=["Pendente", "Em Aberto", "Quitado"], required=True, width="medium"),
                "Forma_Pagamento": st.column_config.SelectboxColumn("Forma", options=["-", "PIX", "Dinheiro", "Cartão Crédito", "Cartão Débito"], width="medium"),
                "Parcelamento": st.column_config.SelectboxColumn("Vezes", options=["-", "À Vista", "2x", "3x", "4x"], width="small"),
                "Valor_Ja_Pago": st.column_config.NumberColumn("Recebido (R$)", format="R$ %.2f", min_value=0, width="medium"),
                "Observacoes": st.column_config.TextColumn("Obs", width="large")
            },
            hide_index=True
        )

        if st.button("💾 SALVAR DADOS NO GOOGLE SHEETS"):
            with st.spinner("Salvando na nuvem..."):
                atualizar_financeiro_completo(df_editavel)
            st.success("Planilha Google atualizada com sucesso!")
            st.rerun()

    else:
        if senha: st.error("Senha incorreta")
