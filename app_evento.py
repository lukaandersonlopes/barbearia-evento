import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Aniversário da Barbearia", layout="centered")

# Nome do arquivo onde os dados serão salvos
ARQUIVO_DADOS = 'lista_convidados.csv'

# --- FUNÇÕES DE DATA SCIENCE (BACKEND) ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return pd.DataFrame(columns=["Nome", "Telefone", "Status", "Pagamento", "Data_Confirmacao"])
    return pd.read_csv(ARQUIVO_DADOS)

def salvar_dados(novo_dado):
    df = carregar_dados()
    df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)
    df.to_csv(ARQUIVO_DADOS, index=False)
    return df

# --- INTERFACE (FRONTEND) ---

# Título Principal
st.title("💈 Aniversário da Barbearia ✂️")
st.write("Estamos preparando um evento exclusivo na chácara e queremos você lá!")

# Abas para separar a visão do Cliente (Convite) da visão do Dono (Gestão)
aba_convite, aba_admin = st.tabs(["📩 Confirmar Presença", "📊 Área do Barbeiro"])

# --- ABA 1: O CONVITE (Para o cliente) ---
with aba_convite:
    st.header("Garanta seu lugar!")
    with st.form("form_confirmacao"):
        nome = st.text_input("Seu Nome Completo")
        telefone = st.text_input("Seu WhatsApp (com DDD)")
        status = st.radio("Você vai?", ["Sim, com certeza!", "Ainda não sei", "Não poderei ir"])
        
        # Botão de Enviar
        enviado = st.form_submit_button("Confirmar Agora")
        
        if enviado:
            if nome and telefone:
                # Salva o dado
                novo_registro = {
                    "Nome": nome,
                    "Telefone": telefone,
                    "Status": status,
                    "Pagamento": "Pendente", # Padrão inicial
                    "Data_Confirmacao": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                salvar_dados(novo_registro)
                st.success(f"Show, {nome}! Recebemos sua resposta.")
                if status == "Sim, com certeza!":
                    st.info("ℹ️ Chave PIX para garantir sua vaga: (00) 99999-9999 (Envie o comprovante no Zap!)")
            else:
                st.error("Por favor, preencha nome e telefone.")

# --- ABA 2: GESTÃO (Para você e o Barbeiro) ---
with aba_admin:
    st.warning("Área restrita à organização.")
    senha = st.text_input("Senha de Acesso", type="password")
    
    if senha == "barba123": # Defina a senha aqui
        df = carregar_dados()
        
        if not df.empty:
            st.divider()
            st.subheader("📈 Painel de Controle (Data Science)")
            
            # Métricas Rápidas
            col1, col2, col3 = st.columns(3)
            confirmados = df[df["Status"] == "Sim, com certeza!"].shape[0]
            pagos = df[df["Pagamento"] == "Pago"].shape[0]
            receita = pagos * 50 # Exemplo: 50 reais por pessoa
            
            col1.metric("Confirmados", confirmados)
            col2.metric("Pagos", pagos)
            col3.metric("Caixa Estimado", f"R$ {receita},00")
            
            st.divider()
            
            # Tabela Editável (Para marcar quem pagou)
            st.write("### Lista de Convidados (Edite o pagamento aqui)")
            df_editavel = st.data_editor(
                df, 
                num_rows="dynamic",
                column_config={
                    "Pagamento": st.column_config.SelectboxColumn(
                        "Status Pagamento",
                        options=["Pendente", "Pago", "Cortesia"],
                        required=True,
                    )
                }
            )
            
            # Botão para salvar alterações feitas na tabela
            if st.button("Salvar Alterações de Pagamento"):
                df_editavel.to_csv(ARQUIVO_DADOS, index=False)
                st.success("Dados atualizados com sucesso!")
                st.rerun()
                
        else:
            st.info("Nenhuma confirmação recebida ainda.")
    elif senha:
        st.error("Senha incorreta.")