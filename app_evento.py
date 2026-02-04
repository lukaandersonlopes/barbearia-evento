import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Churras da Barbearia", layout="centered", page_icon="💈")

# --- CONFIGURAÇÕES DO DONO (EDITE AQUI) ---
ARQUIVO_DADOS = 'lista_interessados.csv'
SENHA_ADMIN = "barba123"
# COLOQUE O NUMERO DO DOUGLAS ABAIXO (Mantenha o 55 e o DDD)
NUMERO_BARBEIRO = "5519998057890" 
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
    texto_camisa = "e tenho interesse na CAMISA também!" if quer_camisa == "Sim" else "sem a camisa por enquanto."
    mensagem = f"Fala Douglas! Aqui é o {nome}. Tô confirmando meu interesse no churras da barbearia {texto_camisa}"
    mensagem_encoded = urllib.parse.quote(mensagem)
    return f"https://wa.me/{NUMERO_BARBEIRO}?text={mensagem_encoded}"

# --- INTERFACE (FRONTEND) ---

st.title("💈 Churras & Resenha da Barbearia")
st.markdown("### ☀️ Piscina, Futebol e aquele Chopp Gelado!")
st.info("ℹ️ **Como vai funcionar:** Estamos organizando a galera. O valor do rateio (divisão dos custos) vai depender de quantos confirmarem. Confirme abaixo para entrar na lista!")

aba_convite, aba_admin = st.tabs(["📝 Lista de Interesse", "📊 Área do Douglas (Admin)"])

# --- ABA 1: CONVITE E INTERESSE ---
with aba_convite:
    st.write("---")
    st.write("### Quem vamos?")
    st.write("O plano: Aluguel da chácara + Chopp/Refri inclusos.")
    st.caption("*Obs: Cada um leva seu kit churrasco (sua carne de preferência).*")
    
    with st.form("form_interesse"):
        nome = st.text_input("Seu Nome ou Apelido")
        telefone = st.text_input("Seu WhatsApp")
        
        st.write("---")
        st.write("👕 **Camisa Oficial do Evento**")
        st.write(f"Quer garantir a peita personalizada da barbearia? (Aprox. R$ {PRECO_CAMISA},00)")
        opcao_camisa = st.checkbox("Sim, eu quero a camisa!")
        
        enviado = st.form_submit_button("✅ Confirmar Interesse")
        
        if enviado:
            if nome and telefone:
                status_camisa = "Sim" if opcao_camisa else "Não"
                
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
                
                st.success(f"Boa, {nome}! Você está na lista.")
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
                st.caption("Clique acima para avisar o Douglas e entrar na Lista de Transmissão.")
                
            else:
                st.error("Preencha nome e telefone, pô!")

# --- ABA 2: CALCULADORA DO ORGANIZADOR ---
with aba_admin:
    st.write("🔐 Acesso Restrito")
    senha = st.text_input("Senha", type="password")
    
    if senha == SENHA_ADMIN:
        df = carregar_dados()
        st.divider()
        st.subheader("🧮 Calculadora de Rateio")
        
        if not df.empty:
            total_pessoas = len(df)
            total_camisas = len(df[df["Quer_Camisa"] == "Sim"])
            
            # Métricas
            col1, col2 = st.columns(2)
            col1.metric("Interessados", total_pessoas)
            col2.metric("Querem Camisa", total_camisas)
            
            st.write("---")
            st.write("### Simulação de Custos")
            st.caption("Ajuste os valores abaixo para saber quanto cobrar por pessoa.")
            
            custo_chacara = st.number_input("Custo da Chácara (R$)", value=1500.0)
            custo_bebida = st.number_input("Custo Bebida/Extras (R$)", value=300.0)
            custo_total_festa = custo_chacara + custo_bebida
            
            if total_pessoas > 0:
                custo_por_cabeca = custo_total_festa / total_pessoas
                
                st.info(f"💰 Custo Total da Festa: **R$ {custo_total_festa:.2f}**")
                
                st.markdown(f"""
                ### 🎯 Valor SUGERIDO por pessoa:
                # R$ {custo_por_cabeca:.2f}
                <small>(Apenas para Chácara + Bebida)</small>
                """, unsafe_allow_html=True)
                
                st.write("---")
                st.markdown("#### Tabela de Preços para o Cliente:")
                st.text(f"🎟️ Ingresso Simples: R$ {custo_por_cabeca:.2f}")
                st.text(f"👕 Ingresso + Camisa: R$ {custo_por_cabeca + PRECO_CAMISA:.2f}")
                
            else:
                st.warning("Precisa de gente na lista para calcular o rateio!")
            
            st.divider()
            st.write("### Lista de Nomes")
            st.dataframe(df)
        else:
            st.info("Ninguém na lista ainda.")
