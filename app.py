import streamlit as st
from supabase import create_client, Client
import datetime

# ==========================================
# CONFIGURAÇÃO DA PÁGINA (Precisa ser o primeiro comando)
# ==========================================
st.set_page_config(page_title="Chat do Casal", page_icon="💬", layout="centered")

# Estilização em CSS para o visual do Chat (Cores escuras e Bolhas)
st.markdown("""
<style>
    .stApp { background-color: #121212; color: #FFFFFF; }
    .chat-container { display: flex; flex-direction: column; gap: 10px; padding: 10px; }
    .bubble { padding: 12px 16px; border-radius: 20px; max-width: 75%; font-size: 16px; margin-bottom: 2px; word-wrap: break-word; }
    .user-bubble { background-color: #5A1D27; color: #FFFFFF; align-self: flex-end; border-bottom-right-radius: 2px; }
    .partner-bubble { background-color: #2A2A2A; color: #E0E0E0; align-self: flex-start; border-bottom-left-radius: 2px; }
    .metadata { font-size: 11px; color: #888888; margin-top: 4px; display: block; text-align: right; }
    .partner-bubble .metadata { text-align: left; }
    .keyword-tag { font-size: 11px; font-style: italic; color: #FFB7B2; display: block; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CONEXÃO COM O SUPABASE (Puxando dos Secrets)
# ==========================================
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# ==========================================
# FUNÇÃO DA PALAVRA DO DIA
# ==========================================
def palavra_do_dia():
    # Lista fixa de palavras para cada dia da semana
    palavras = ["espelho", "café", "abraço", "sorriso", "destino", "bilhete", "luar"]
    dia_ano = datetime.datetime.now().timetuple().tm_yday
    indice = dia_ano % len(palavras)
    return palavras[indice]

# Salva a palavra do dia no estado do app
st.session_state.palavra = palavra_do_dia()

# ==========================================
# SISTEMA DE LOGIN
# ==========================================
if "user" not in st.session_state:
    st.markdown("## 💬 Chat Privado")
    
    user_input = st.text_input("Código de Acesso", type="password")
    
    if st.button("Entrar"):
        if user_input in ["amor1", "amor2"]:
            st.session_state.user = user_input
            st.rerun()
        else:
            st.error("Código inválido!")
    st.stop()

# Se chegou aqui, o usuário está logado
user = st.session_state.user

# ==========================================
# CABEÇALHO DO APP
# ==========================================
st.markdown(f"### 💬 Chat Privado • *Palavra do Dia:* **{st.session_state.palavra}**")

# ==========================================
# FUNÇÕES DO BANCO DE DADOS
# ==========================================
def carregar():
    try:
        res = supabase.table("mensagens").select("*").order("created_at", ascending=True).limit(50).execute()
        if hasattr(res, 'data'):
            return res.data
        elif isinstance(res, dict) and 'data' in res:
            return res['data']
        return []
    except Exception as e:
        return []

def salvar(texto):
    try:
        palavra = st.session_state.get('palavra', 'Não definida')
        
        # Faz o insert de forma direta e segura
        supabase.table("mensagens").insert({
            "usuario": user,
            "mensagem": texto,
            "palavra_do_dia": palavra
        }).execute()
        return True
    except Exception as e:
        # Mostra o erro real na tela caso o Supabase recuse por algum motivo
        st.error(f"Erro ao falar com o banco: {str(e)}")
        return False

# ==========================================
# CARREGAMENTO E EXIBIÇÃO DO HISTÓRICO
# ==========================================
msgs = carregar()

st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for m in msgs:
    if m["usuario"] == user:
        classe_bolha = "user-bubble"
        identificador = "Você"
    else:
        classe_bolha = "partner-bubble"
        identificador = "Amor"
        
    hora_formatada = ""
    if "created_at" in m and m["created_at"]:
        try:
            hora_formatada = m["created_at"].split("T")[1][:5]
        except:
            hora_formatada = ""

    palavra_salva = m.get('palavra_do_dia', '---')
    texto_mensagem = m.get('mensagem', '')

    html_bolha = f"""
    <div class="bubble {classe_bolha}">
        {texto_mensagem}
        <span class="keyword-tag">🔑 Palavra: {palavra_salva}</span>
        <span class="metadata">{identificador} • {hora_formatada}</span>
    </div>
    """
    st.markdown(html_bolha, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# ÁREA DE ENVIO DE MENSAGENS
# ==========================================
st.markdown("---")

with st.form(key="formulario_chat", clear_on_submit=True):
    msg_input = st.text_input("Digite sua mensagem:", placeholder="Sua frase precisa conter a palavra do dia de hoje...")
    botao_enviar = st.form_submit_button(label="Enviar Mensagem")

    if botao_enviar:
        if msg_input.strip() == "":
            st.warning("Por favor, digite uma mensagem antes de enviar.")
        else:
            palavra_atual = st.session_state.palavra.lower()
            
            # Correção do erro de digitação: trocado 'palabra_atual' por 'palavra_atual'
            if palavra_atual in msg_input.lower():
                if salvar(msg_input):
                    st.rerun()
            else:
                st.error("Sua frase não contém a palavra do dia! Tente novamente.")
