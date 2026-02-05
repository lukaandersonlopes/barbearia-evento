import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="5 Anos - Barbearia Vasques", layout="centered", page_icon="💈")

# --- CONFIGURAÇÕES DO DONO (EDITE AQUI) ---
ARQUIVO_DADOS = 'lista_interessados.csv'
SENHA_ADMIN = "barba123"
NUMERO_BARBEIRO = "5519998057890" # SEU NÚMERO AQUI
PRECO_CAMISA = 45.00

# --- FUNÇÕES (BACKEND) ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return pd.DataFrame(columns=["Nome", "Telefone", "Quer_Camisa", "Data_Confirmacao"])
    return pd.read_csv(ARQUIVO_DADOS)

def salvar_dados(novo_dado):
    df = carregar_dados()
    df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)
    df.to_csv(ARQUIVO_DADOS, index=False)

def gerar_link_whatsapp(nome, quer_camisa):
    texto_camisa = "e vou querer a CAMISA dos 5 Anos!" if quer_camisa == "Sim" else "sem a camisa por enquanto."
    mensagem = f"Fala Douglas! Aqui é o {nome}. Recebi o convite dos 5 ANOS e confirmo minha presença! {texto_camisa}"
    mensagem_encoded = urllib.parse.quote(mensagem)
    return f"https://wa.me/{NUMERO_BARBEIRO}?text={mensagem_encoded}"

# --- INTERFACE (FRONTEND) ---

# --- CABEÇALHO (HEADER) PERSONALIZADO ---
# Truque de colunas para centralizar o logo e deixá-lo maior
col_esq, col_centro, col_dir = st.columns([1, 8, 1])

with col_centro:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True) # Deixa o logo grande e responsivo
    
    # Título centralizado com HTML para ficar bonito
    st.markdown("""
        <h1 style='text-align: center; color: #E67E22; margin-bottom: 0;'>
            COMEMORAÇÃO DE 5 ANOS
        </h1>
        <h3 style='text-align: center; color: #555;'>
            BARBEARIA VASQUES
        </h3>
        <hr>
    """, unsafe_allow_html=True)

# Mensagem Emocional (Atualizada com os 5 anos)
st.info("""
**Você faz parte dessa história!** Se você recebeu este convite, saiba que é fundamental na nossa caminhada. 
Esses 5 anos de Barbearia Vasques não existiriam sem a sua confiança. 
Obrigado por estar com a gente. Vamos comemorar!
""")

st.markdown("""
<div style="text-align: center; font-size: 1.2rem; margin-bottom: 20px;">
    <b>☀️ Piscina • ⚽️ Futebol • 🍻 Chopp Gelado</b>
</div>
""", unsafe_allow_html=True)

st.caption("O valor do rateio (divisão de custos) será definido com base no número de confirmados. Quanto mais gente, melhor!")

aba_convite, aba_admin = st.tabs(["✅ Confirmar Presença", "🔒 Área Administrativa"])

# --- ABA 1: CONVITE E INTERESSE ---
with aba_convite:
    st.write("### Garanta seu lugar na festa")
    st.write("Preencha abaixo para confirmar sua intenção de ir.")
    
    with st.form("form_interesse"):
        nome = st.text_input("Nome Completo")
        telefone = st.text_input("WhatsApp (com DDD)")
        
        st.write("---")
        st.markdown(f"#### 👕 Camisa Comemorativa 5 Anos (Aprox. R$ {PRECO_CAMISA},00)")
        
        opcao_camisa = st.radio(
            "Você deseja encomendar a camisa personalizada?",
            ["Sim, quero a camisa!", "Não, apenas o evento."],
            index=None, 
            help="O valor da camisa é a parte do valor do rateio da chácara."
        )
        
        st.write("")
        enviado = st.form_submit_button("Confirmar Presença")
        
        if enviado:
            if nome and telefone and opcao_camisa:
                status_camisa = "Sim" if "Sim" in opcao_camisa else "Não"
                
                # Salva os dados
                novo_registro = {
                    "Nome": nome,
                    "Telefone": telefone,
                    "Quer_Camisa": status_camisa,
                    "Data_Confirmacao": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                salvar_dados(novo_registro)
                
                # Gera Link do Zap
                link_zap = gerar_link_whatsapp(nome, status_camisa)
                
                st.success(f"Show, {nome}! Parabéns por fazer parte desses 5 anos.")
                st.markdown(f"""
                    <a href="{link_zap}" target="_blank">
                        <button style="
                            background-color:#25D366; 
                            color:white; 
                            border:none; 
                            padding:15px 32px; 
                            text-align:center; 
                            text-decoration:none; 
                            display:inline-block; 
                            font-size:16px; 
                            margin:4px 2px; 
                            cursor:pointer; 
                            border-radius:8px; 
                            font-weight:bold;
                            width:100%;">
                            📲 ENVIAR CONFIRMAÇÃO NO ZAP DO DOUGLAS
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
                st.caption("É obrigatório clicar no botão acima para avisar o barbeiro.")
                
            else:
                st.error("Por favor, preencha todos os campos.")

# --- ABA 2: CALCULADORA DO ORGANIZADOR ---
with aba_admin:
    st.write("Acesso Restrito à Organização")
    senha = st.text_input("Senha de Acesso", type="password")
    
    if senha == SENHA_ADMIN:
        df = carregar_dados()
        st.divider()
        st.subheader("Painel Financeiro - 5 Anos")
        
        if not df.empty:
            total_pessoas = len(df)
            total_camisas = len(df[df["Quer_Camisa"] == "Sim"])
            
            # Métricas
            col1, col2 = st.columns(2)
            col1.metric("Total Confirmados", total_pessoas)
            col2.metric("Camisas Pedidas", total_camisas)
            
            st.write("---")
            st.write("### 🧮 Simulador de Rateio")
            
            custo_chacara = st.number_input("Custo da Chácara (R$)", value=1500.0)
            custo_bebida = st.number_input("Custo Bebida/Extras (R$)", value=300.0)
            custo_total_festa = custo_chacara + custo_bebida
            
            if total_pessoas > 0:
                custo_por_cabeca = custo_total_festa / total_pessoas
                
                st.success(f"Custo Total: R$ {custo_total_festa:.2f}")
                
                st.markdown(f"""
                ### Valor SUGERIDO por pessoa:
                # R$ {custo_por_cabeca:.2f}
                <small>(Sem contar a camisa)</small>
                """, unsafe_allow_html=True)
                
            else:
                st.warning("Aguardando confirmações para calcular...")
            
            st.divider()
            st.write("### Lista Completa")
            st.dataframe(df)
        else:
            st.info("A lista está vazia.")

