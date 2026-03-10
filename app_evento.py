import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import urllib.parse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
import base64
import streamlit.components.v1 as components

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="5 Anos Barbearia Vasques", layout="centered", page_icon="💈")

# --- CSS PERSONALIZADO ---
st.markdown("""
<style>
    .card-container {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    .card {
        background-color: #262730;
        border: 1px solid #E67E22;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        width: 100px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .card:hover {
        transform: scale(1.05);
        border-color: #FF9F43;
    }
    .card-icon {
        font-size: 2rem;
        display: block;
        margin-bottom: 5px;
    }
    .card-text {
        color: #FFF;
        font-weight: bold;
        font-size: 0.8rem;
        text-transform: uppercase;
    }
    .date-banner {
        background: linear-gradient(90deg, #1E1E1E 0%, #2D2D2D 100%);
        color: white;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin: 20px 0;
        border-left: 5px solid #E67E22;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÕES DO DONO ---
NOME_PLANILHA_GOOGLE = "Barbearia 5 Anos - Dados" 
SENHA_ADMIN = "barba123"
NUMERO_BARBEIRO = "5519998057890"
PRECO_CAMISA = 45.00
DATA_EVENTO = date(2026, 7, 11)

# --- FUNÇÃO PARA CENTRALIZAR IMAGEM ---
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

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
    
    if df.empty: return pd.DataFrame(columns=colunas_padrao)
    
    for col in colunas_padrao:
        if col not in df.columns: df[col] = ""

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
    mensagem = f"Fala Douglas! Aqui é o {nome}. Confirmo presença no dia 11/07! {texto_camisa}"
    return f"https://wa.me/{NUMERO_BARBEIRO}?text={urllib.parse.quote(mensagem)}"

# --- CONTROLE DE SESSÃO (EVITAR DUPLICADOS) ---
if 'inscricao_feita' not in st.session_state:
    st.session_state['inscricao_feita'] = False
    st.session_state['nome_salvo'] = ""
    st.session_state['link_zap'] = ""

# --- INTERFACE ---

# 1. LOGO
if os.path.exists("logo.png"):
    img_base64 = get_base64_image("logo.png")
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; margin-bottom: 10px;">
            <img src="data:image/png;base64,{img_base64}" width="220" style="border-radius: 10px;">
        </div>
        """, 
        unsafe_allow_html=True
    )

# 2. TÍTULOS
st.markdown("""
    <div style='text-align: center;'>
        <h1 style='color: #E67E22; margin: 0; font-size: 2.2rem; text-transform: uppercase;'>5 ANOS DE HISTÓRIA</h1>
        <h3 style='color: #888; margin-top: 5px; letter-spacing: 2px; font-size: 0.9rem;'>BARBEARIA VASQUES</h3>
    </div>
""", unsafe_allow_html=True)

# 3. BANNER DE DATA
dias_restantes = (DATA_EVENTO - date.today()).days

if dias_restantes > 0:
    texto_contador = f"<p style='margin:5px 0 0 0; font-size: 0.9rem; color: #ccc;'>Faltam <b>{dias_restantes} dias</b> para a grande resenha!</p>"
elif dias_restantes == 0:
    texto_contador = f"<p style='margin:5px 0 0 0; font-size: 1.1rem; color: #E67E22;'>🔥 <b>É HOJE!</b> Vamos celebrar juntos os 5 anos da Barbearia Vasques!</p>"
else:
    texto_contador = f"<p style='margin:5px 0 0 0; font-size: 0.9rem; color: #ccc;'>🎉 <b>O evento já rolou!</b> Obrigado a todos que participaram.</p>"

st.markdown(f"""
    <div class="date-banner">
        <h2 style='margin:0; font-size: 1.5rem;'>📅 SÁBADO, 11 DE JULHO</h2>
        {texto_contador}
    </div>
""", unsafe_allow_html=True)

# 4. CARDS DE ATRAÇÕES
st.markdown("""
    <div class="card-container">
        <div class="card">
            <span class="card-icon">☀️</span>
            <span class="card-text">Piscina<br>Liberada</span>
        </div>
        <div class="card">
            <span class="card-icon">⚽️</span>
            <span class="card-text">Futebol</span>
        </div>
        <div class="card">
            <span class="card-icon">🍻</span>
            <span class="card-text">Chopp<br>Gelado</span>
        </div>
    </div>
""", unsafe_allow_html=True)

st.info("🤝 **Você faz parte dessa história!** Contamos com sua presença.")

# 5. AVISO
st.markdown("""
<div style='background-color: #FFF3CD; padding: 15px; border-radius: 10px; border: 1px solid #FFEEBA; text-align: center; margin-bottom: 20px;'>
    <h4 style='color: #856404; margin:0 0 10px 0;'>⚠️ IMPORTANTE</h4>
    <p style='color: #856404; font-size: 14px; line-height: 1.5; margin: 0;'>
        O valor da participação depende do número de confirmados. 
        Entrarei em contato para fazer a divisão correta.
    </p>
</div>
""", unsafe_allow_html=True)

# --- ABAS ---
aba_convite, aba_admin = st.tabs(["✅ Confirmar Presença", "🔒 Gestão & Financeiro"])

# --- ABA 1: CONVITE ---
with aba_convite:
    # Se o cara ainda não se inscreveu, mostra o formulário
    if not st.session_state['inscricao_feita']:
        st.write("### Garanta seu lugar")
        with st.form("form_interesse", clear_on_submit=True):
            nome = st.text_input("Nome Completo")
            # Adicionado máscara visual e limite de caracteres
            telefone = st.text_input("WhatsApp (com DDD)", max_chars=15, placeholder="(11) 99999-9999")
            
            st.markdown(f"#### 👕 Camisa Comemorativa (Aprox. R$ {PRECO_CAMISA:.2f})")
            opcao_camisa = st.radio("Deseja a camisa?", ["Sim, quero a camisa!", "Não, apenas o evento."], index=None)
            
            tamanho_selecionado = None
            if opcao_camisa == "Sim, quero a camisa!":
                st.markdown("**Selecione o tamanho (Obrigatório):**")
                tamanho_selecionado = st.selectbox("Qual o tamanho?", ["P", "M", "G", "GG", "G1", "G2"], index=None, placeholder="Escolha um tamanho...")
            
            if st.form_submit_button("Confirmar Presença"):
                if nome and telefone and opcao_camisa:
                    status_camisa = "Sim" if "Sim" in opcao_camisa else "Não"
                    if status_camisa == "Sim" and tamanho_selecionado is None:
                         st.error("⚠️ ATENÇÃO: Escolha o tamanho da camisa!")
                    else:
                        tamanho_final = tamanho_selecionado if tamanho_selecionado else "-"
                        novo = {"Nome": nome, "Telefone": telefone, "Quer_Camisa": status_camisa, "Tamanho_Camisa": tamanho_final, "Data_Confirmacao": datetime.now().strftime("%d/%m/%Y %H:%M")}
                        
                        # Spinner de carregamento elegante
                        with st.spinner('Salvando sua confirmação na lista...'):
                            salvar_novo_inscrito(novo)
                            
                        # Salva na memória que deu certo e atualiza a tela
                        st.session_state['inscricao_feita'] = True
                        st.session_state['nome_salvo'] = nome
                        st.session_state['link_zap'] = gerar_link_whatsapp(nome, status_camisa, tamanho_final)
                        st.rerun()
                else:
                    st.error("Preencha todos os campos!")
                    
    # Se ele já se inscreveu, esconde o formulário e mostra só o sucesso
    else:
        st.balloons()
        st.success(f"Show, {st.session_state['nome_salvo']}! Seus dados foram salvos com sucesso na nossa lista.")
        st.markdown(f'<a href="{st.session_state["link_zap"]}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; width:100%; font-weight:bold; font-size:16px;">📲 AVISAR NO WHATSAPP</button></a>', unsafe_allow_html=True)
        
        # Botão caso ele queira inscrever outra pessoa no mesmo celular
        if st.button("Inscrever outra pessoa"):
            st.session_state['inscricao_feita'] = False
            st.rerun()


# --- ABA 2: FINANCEIRO ---
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

            st.data_editor(df, key="editor_financeiro", column_config=col_config, num_rows="dynamic", use_container_width=True, hide_index=True)
            
            if st.button("💾 SALVAR TUDO NO GOOGLE SHEETS"):
                atualizar_financeiro_completo(st.session_state["editor_financeiro"])
                st.success("Salvo com sucesso!")
                st.rerun()

        except Exception as e:
            st.error(f"Erro ao carregar tabela: {e}")

# --- RODAPÉ COM O MAPA ---
st.write("---")
st.subheader("📍 COMO CHEGAR?")
st.caption("Recanto dos Colibris, Rua 5 Quadra B Lote 06")

mapa_html = """
<iframe src="https://www.google.com/maps/embed?pb=!1m17!1m12!1m3!1d3698.0020605543564!2d-47.47379682471459!3d-22.04951667986774!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m2!1m1!2zMjLCsDAyJzU4LjMiUyA0N8KwMjgnMTYuNCJX!5e0!3m2!1spt-BR!2sbr!4v1770915445016!5m2!1spt-BR!2sbr" width="100%" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
"""
components.html(mapa_html, height=450)
