import streamlit as st
import pandas as pd
from datetime import datetime, date
import urllib.parse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="5 Anos Barbearia Vasques", layout="wide", page_icon="💈")

# --- CONFIGURAÇÕES DO DONO ---
NOME_PLANILHA_GOOGLE = "Barbearia 5 Anos - Dados" 
SENHA_ADMIN = "barba123"
NUMERO_BARBEIRO = "5519998057890"
PRECO_CAMISA = 45.00
DATA_EVENTO = date(2026, 7, 12) # Ano, Mês, Dia

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
        st.error(f"Erro de conexão: {e}")
        st.stop()

def carregar_dados():
    sheet = conectar_google_sheets()
    dados = sheet.get_all_records()
    df = pd.DataFrame(dados)
    colunas_padrao = ["Nome", "Telefone", "Quer_Camisa", "Tamanho_Camisa", "Data_Confirmacao", "Status_Pagamento", "Forma_Pagamento", "Parcelamento", "Valor_Ja_Pago", "Observacoes"]
    if df.empty: return pd.DataFrame(columns=colunas_padrao)
    
    if "Valor_Ja_Pago" in df.columns:
        df["Valor_Ja_Pago"] = df["Valor_Ja_Pago"].astype(str).str.replace('R$', '').str.replace(',', '.').replace('', '0')
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

# --- INTERFACE (VISUAL NOVO) ---

# Centralização do Layout (Truque para não ficar esticado no PC)
col_vazia_esq, col_principal, col_vazia_dir = st.columns([1, 2, 1])

with col_principal:
    # 1. LOGO (Ajustado tamanho)
    if os.path.exists("logo.png"):
        # Usei colunas internas para centralizar a imagem perfeitamente
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            st.image("logo.png", width=180) # TAMANHO REDUZIDO (Era gigante antes)
    
    # 2. TÍTULOS
    st.markdown("""
        <div style='text-align: center;'>
            <h1 style='color: #E67E22; margin-bottom: 0; font-size: 2.5rem;'>5 ANOS DE HISTÓRIA</h1>
            <h3 style='color: #555; margin-top: 5px;'>BARBEARIA VASQUES</h3>
        </div>
    """, unsafe_allow_html=True)

    # 3. BANNER DE DATA (Novo!)
    dias_restantes = (DATA_EVENTO - date.today()).days
    st.markdown(f"""
        <div style='background-color: #333; color: white; padding: 15px; border-radius: 10px; text-align: center; margin: 20px 0;'>
            <h2 style='margin:0; font-size: 1.5rem;'>📅 DOMINGO, 12 DE JULHO</h2>
            <p style='margin:5px 0 0 0; font-size: 0.9rem; color: #ddd;'>Faltam {dias_restantes} dias para a resenha!</p>
        </div>
    """, unsafe_allow_html=True)

    # 4. ÍCONES DE LAZER (Voltaram!)
    st.markdown("""
        <div style='display: flex; justify-content: space-around; text-align: center; margin-bottom: 20px; font-size: 1.1rem; color: #E67E22; font-weight: bold;'>
            <span>☀️ Piscina</span>
            <span>⚽️ Futebol</span>
            <span>🍻 Chopp Gelado</span>
        </div>
        <hr>
    """, unsafe_allow_html=True)

    # 5. MENSAGEM EMOCIONAL
    st.info("**Você faz parte dessa história!** Esses 5 anos não existiriam sem você. Vamos comemorar juntos!")

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

# --- ABA 2: FINANCEIRO (FORA DA COLUNA CENTRAL PARA TER ESPAÇO) ---
# Aqui usamos a largura total da tela para caber a tabela
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
            df_edit = st.data_editor(df, num_rows="dynamic", use_container_width=True, hide_index=True)
            
            if st.button("💾 SALVAR TUDO NO GOOGLE SHEETS"):
                atualizar_financeiro_completo(df_edit)
                st.success("Salvo com sucesso!")
                st.rerun()

        except Exception as e:
            st.error(f"Erro: {e}")
