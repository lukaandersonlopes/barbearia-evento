import streamlit as st
import pandas as pd
from datetime import datetime, date
import urllib.parse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os # IMPORTANTE: Mantido para não dar erro

# --- CONFIGURAÇÃO INICIAL (LAYOUT WIDE) ---
st.set_page_config(page_title="5 Anos Barbearia Vasques", layout="wide", page_icon="💈")

# --- CSS PERSONALIZADO (A MÁGICA DO DESIGN) ---
st.markdown("""
<style>
    /* Centraliza imagens */
    .stImage {
        display: flex;
        justify-content: center;
    }
    
    /* Estilo dos Cards de Atrações */
    .card-container {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 20px;
    }
    .card {
        background-color: #262730; /* Cor de fundo do card (cinza escuro) */
        border: 1px solid #E67E22; /* Borda laranja fina */
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        width: 32%; /* Ocupa 1/3 da linha */
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .card:hover {
        transform: scale(1.05); /* Efeito de zoom leve ao passar o mouse */
        border-color: #FF9F43;
    }
    .card-icon {
        font-size: 2rem;
        margin-bottom: 5px;
        display: block;
    }
    .card-text {
        color: #FFF;
        font-weight: bold;
        font-size: 1.1rem;
        text-transform: uppercase;
    }
    
    /* Ajuste do Banner de Data */
    .date-banner {
        background: linear-gradient(90deg, #1E1E1E 0%, #2D2D2D 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin: 25px 0;
        border-left: 5px solid #E67E22;
    }
</style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÕES DO DONO ---
NOME_PLANILHA_GOOGLE = "Barbearia 5 Anos - Dados" 
SENHA_ADMIN = "barba123"
NUMERO_BARBEIRO = "5519998057890"
PRECO_CAMISA = 45.00
DATA_EVENTO = date(2026, 7, 12)

# --- CONEXÃO COM GOOGLE SHEETS ---
def conectar_google_sheets():
    try:
        json_creds = json.loads(st.secrets["google_creds"]["conteudo_json"])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json_creds, scope)
        client = gspread.authorize(creds)
        sheet = client.open(NOME_PLANILHA_GOOGLE).sheet1
        return sheet
    except Exception as e:
        st.error(f"Erro de conexão com Google Sheets: {e}")
        st.stop()

def carregar_dados():
    try:
        sheet = conectar_google_sheets()
        dados = sheet.get_all_records()
        df = pd.DataFrame(dados)
    except:
        df = pd.DataFrame()

    colunas_padrao = ["Nome", "Telefone", "Quer_Camisa", "Tamanho_Camisa", "Data_Confirmacao", "Status_Pagamento", "Forma_Pagamento", "Parcelamento", "Valor_Ja_Pago", "Observacoes"]
    
    if df.empty: 
        return pd.DataFrame(columns=colunas_padrao)
    
    for col in colunas_padrao:
        if col not in df.columns:
            df[col] = ""

    # BLINDAGEM DE DADOS (Correção de erros numéricos)
    if "Valor_Ja_Pago" in df.columns:
        df["Valor_Ja_Pago"] = df["Valor_Ja_Pago"].astype(str).str.replace('R$', '', regex=False).str.replace(',', '.', regex=False)
        df["Valor_Ja_Pago"] = pd.to_numeric(df["Valor_Ja_Pago"], errors='coerce').fillna(0.0)
    
    return df

def salvar_novo_inscrito(novo_dado):
    sheet = conectar_google_sheets()
    linha = [novo_dado["Nome"], novo_dado["Telefone"], novo_dado["Quer_Camisa"], novo_dado["Tamanho_Camisa"], novo_dado["Data_Confirmacao"], "Pendente", "-", "-", 0.0, ""]
    sheet.append_row(linha)

def atualizar_financeiro_completo(df_editado):
    sheet = conectar_google_sheets()
    dados_lista = [df_editado.columns.tolist()] + df_editado.values.tolist()
    sheet.clear()
    sheet.update(dados_lista)

def gerar_link_whatsapp(nome, quer_camisa, tamanho):
    texto_camisa = f"e vou querer a CAMISA dos 5 Anos (Tamanho {tamanho})!" if quer_camisa == "Sim" else "sem a camisa por enquanto."
    mensagem = f"Fala Douglas! Aqui é o {nome}. Confirmo presença no dia 12/07! {texto_camisa}"
    return f"https://wa.me/{NUMERO_BARBEIRO}?text={urllib.parse.quote(mensagem)}"

# --- INTERFACE (LAYOUT CENTRALIZADO) ---
# Usamos colunas para focar o conteúdo no centro da tela (Mobile Friendly)
col_vazia_esq, col_principal, col_vazia_dir = st.columns([1, 2, 1])

with col_principal:
    # 1. LOGO (Centralizado via CSS e maior)
    if os.path.exists("logo.png"):
        st.image("logo.png", width=300) # AUMENTADO PARA 300px
    
    # 2. TÍTULOS
    st.markdown("""
        <div style='text-align: center; margin-top: 10px;'>
            <h1 style='color: #E67E22; margin: 0; font-size: 3rem; text-transform: uppercase;'>5 ANOS DE HISTÓRIA</h1>
            <h3 style='color: #888; margin-top: 5px; letter-spacing: 2px;'>BARBEARIA VASQUES</h3>
        </div>
    """, unsafe_allow_html=True)

    # 3. BANNER DE DATA (Novo Design)
    dias_restantes = (DATA_EVENTO - date.today()).days
    st.markdown(f"""
        <div class="date-banner">
            <h2 style='margin:0; font-size: 1.8rem;'>📅 DOMINGO, 12 DE JULHO</h2>
            <p style='margin:10px 0 0 0; font-size: 1rem; color: #ccc;'>Faltam <b>{dias_restantes} dias</b> para a grande resenha!</p>
        </div>
    """, unsafe_allow_html=True)

    # 4. CARDS DE ATRAÇÕES (Aqui está a grande mudança!)
    st.markdown("""
        <div class="card-container">
            <div class="card">
                <span class="card-icon">☀️</span>
                <span class="card-text">Piscina<br>Liberada</span>
            </div>
            <div class="card">
                <span class="card-icon">⚽️</span>
                <span class="card-text">Futebol<br>Society</span>
            </div>
            <div class="card">
                <span class="card-icon">🍻</span>
                <span class="card-text">Chopp<br>Gelado</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 5. MENSAGEM
    st.info("🤝 **Você faz parte dessa história!** A Barbearia Vasques conta com sua presença para celebrar essa conquista.")

    # 6. AVISO FINANCEIRO
    st.markdown("""
    <div style='background-color: #FFF3CD; padding: 15px; border-radius: 10px; border: 1px solid #FFEEBA; text-align: center; margin-bottom: 20px;'>
        <h4 style='color: #856404; margin:0 0 10px 0;'>⚠️ IMPORTANTE</h4>
        <p style='color: #856404; font-size: 16px; line-height: 1.5; margin: 0;'>
            O valor da participação depende do número de confirmados. 
            Entrarei em contato assim que tiver a confirmação de todos vocês para fazer a divisão correta do valor.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # --- ABAS ---
    aba_convite, aba_admin = st.tabs(["✅ Confirmar Presença", "🔒 Gestão & Financeiro"])

    # --- ABA 1: CONVITE ---
    with aba_convite:
        st.write("### Garanta seu lugar")
        with st.form("form_interesse"):
            nome = st.text_input("Nome Completo")
            telefone = st.text_input("WhatsApp (com DDD)")
            
            st.markdown(f"#### 👕 Camisa Comemorativa (Aprox. R$ {PRECO_CAMISA:.2f})")
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
                        novo = {"Nome": nome, "Telefone": telefone, "Quer_Camisa": status_camisa, "Tamanho_Camisa": tamanho_selecionado, "Data_Confirmacao": datetime.now().strftime("%d/%m/%Y %H:%M")}
                        salvar_novo_inscrito(novo)
                        link = gerar_link_whatsapp(nome, status_camisa, tamanho_selecionado)
                        st.success(f"Show, {nome}! Seus dados foram salvos.")
                        st.markdown(f'<a href="{link}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; width:100%; font-weight:bold; font-size:16px;">📲 AVISAR NO WHATSAPP</button></a>', unsafe_allow_html=True)
                else:
                    st.error("Preencha todos os campos!")

# --- ABA 2: FINANCEIRO (FORA DA COLUNA PARA TER ESPAÇO) ---
st.write("---")
with aba_admin:
    col_vazia, col_senha, col_vazia2 = st.columns([1, 1, 1])
    with col_senha:
        st.write("🔐 Área Restrita")
        senha = st.text_input("Senha Admin", type="password")
    
    if senha == SENHA_ADMIN:
        try:
            df = carregar_dados()
            st.success("🟢 Conectado ao Google Sheets")
            
            st.subheader("1. Definição de Preço (Rateio)")
            c1, c2, c3 = st.columns(3)
            custo_tot = c1.number_input("Custo Total (Chácara + Bebida)", value=1800.0)
            qtd = len(df)
            if qtd > 0: c3.metric("Custo por Pessoa", f"R$ {(custo_tot/qtd):.2f}")
            else: c3.warning("Sem inscritos")

            st.divider()
            
            st.subheader("2. Simulador de Parcelas")
            with st.expander("Calculadora Rápida"):
                v = st.number_input("Valor", value=100.0)
                p = st.number_input("Vezes", 1, 12, 3)
                st.metric("Parcela", f"R$ {(v/p):.2f}")

            st.divider()

            st.subheader("3. Gestão Financeira")
            recebido = df["Valor_Ja_Pago"].sum()
            m1, m2 = st.columns(2)
            m1.metric("💰 Total Recebido", f"R$ {recebido:.2f}")
            m2.metric("👥 Total Confirmados", qtd)
            
            st.caption("Qualquer alteração feita abaixo vai direto para o Google.")
            
            col_config = {
                "Nome": st.column_config.TextColumn("Nome", disabled=True),
                "Quer_Camisa": st.column_config.TextColumn("Camisa?", disabled=True, width="small"),
                "Tamanho_Camisa": st.column_config.SelectboxColumn("Tam.", options=["-", "P", "M", "G", "GG", "G1", "G2"], width="small"),
                "Status_Pagamento": st.column_config.SelectboxColumn("Status", options=["Pendente", "Em Aberto", "Quitado"], required=True, width="medium"),
                "Forma_Pagamento": st.column_config.SelectboxColumn("Forma", options=["-", "PIX", "Dinheiro", "Cartão Crédito", "Cartão Débito"], width="medium"),
                "Parcelamento": st.column_config.SelectboxColumn("Vezes", options=["-", "À Vista", "2x", "3x", "4x"], width="small"),
                "Valor_Ja_Pago": st.column_config.NumberColumn("Recebido (R$)", format="R$ %.2f", min_value=0, width="medium"),
                "Observacoes": st.column_config.TextColumn("Obs", width="large")
            }

            df_edit = st.data_editor(
                df, 
                key="editor_financeiro",
                column_config=col_config,
                num_rows="dynamic", 
                use_container_width=True, 
                hide_index=True
            )
            
            if st.button("💾 SALVAR TUDO NO GOOGLE SHEETS"):
                atualizar_financeiro_completo(df_edit)
                st.success("Salvo com sucesso!")
                st.rerun()

        except Exception as e:
            st.error(f"Erro ao carregar tabela: {e}")
