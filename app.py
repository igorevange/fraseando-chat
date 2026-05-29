import streamlit as st
from supabase import create_client
import datetime
import re

# =========================
# CONFIGURAÇÕES DA PÁGINA
# =========================
st.set_page_config(page_title="Chat Privado", page_icon="💬", layout="centered")

# =========================
# CONFIG SUPABASE
# =========================
@st.cache_resource
def init_connection():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

supabase = init_connection()

# =========================
# PALAVRAS (365 ciclo)
# =========================
PALAVRAS = [
    "girassol","saudade","janela","origami","café","maré","promessa","labirinto","moletom","silêncio",
    "constelação","abraço","bússola","tempestade","fotografia","chá","satélite","cobertor","eclipse","suspiro",
    "mercado","neblina","playlist","oceano","travesseiro","domingo","caminho","vento","areia","espelho",
    "caderno","caneta","floresta","lua","sol","chuva","noite","manhã","tarde","madrugada"
] * 10

PALAVRAS = PALAVRAS[:365]

def palavra_do_dia():
    return PALAVRAS[datetime.date.today().timetuple().tm_yday % len(PALAVRAS)]

# =========================
# LOGIN
# =========================
if "user" not in st.session_state:
    st.markdown("## 💬 Chat do Casal")
    user = st.text_input("Código (amor1 / amor2)", type="password")
    
    if st.button("Entrar"):
        if user in ["amor1", "amor2"]:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Código inválido")
    st.stop()

user = st.session_state.user

# =========================
# UI STYLE (APP FEEL)
# =========================
st.markdown(f"""
<style>
    /* Remove elementos padrão do Streamlit */
    header, footer, #MainMenu {{visibility: hidden !important;}}
    .stAppDeployButton {{display: none !important;}}
    
    /* Estilização do fundo e container */
    .stApp {{
        background-color: #151515;
    }}
    
    /* Customização das bolhas nativas do Streamlit */
    div[data-testid="stChatMessage"] {{
        background-color: #2A2A2A !important;
        border-radius: 14px !important;
        color: #EAEAEA !important;
        margin-bottom: 8px !important;
    }}
    
    /* Se a mensagem for minha (User) muda a cor */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatar"] p:contains("{user}")) {{
        background-color: #5A1D27 !important;
    }}
    
    /* Esconde os avatares padrão para parecer chat limpo */
    div[data-testid="stChatMessageAvatar"] {{
        display: none !important;
    }}
    
    /* Destaque da palavra do dia */
    .highlight {{
        background: #8B2E43;
        padding: 2px 6px;
        border-radius: 6px;
        font-weight: 700;
        color: #FFFFFF;
    }}

    /* Intercepta o st.error e aplica o tremor (SHAKE EFFECT) */
    div[data-testid="stNotification"] {{
        animation: shake 0.4s ease-in-out;
        border: 1px solid #C4455F !important;
        background-color: #2D1419 !important;
        color: #FFD6DE !important;
    }}

    /* Animação do tremor */
    @keyframes shake {{
        0% {{ transform: translateX(0); }}
        15% {{ transform: translateX(-8px); }}
        30% {{ transform: translateX(6px); }}
        45% {{ transform: translateX(-6px); }}
        60% {{ transform: translateX(4px); }}
        75% {{ transform: translateX(-2px); }}
        100% {{ transform: translateX(0); }}
    }}
</style>
""", unsafe_allow_html=True)

# =========================
# FUNÇÕES BANCO DE DADOS
# =========================
def carregar():
    try:
        # Puxa os dados do banco
        res = supabase.table("mensagens").select("*").order("created_at", ascending=True).limit(50).execute()
        
        # Garante que pega os dados corretamente, mesmo se a resposta vier em formatos diferentes
        if hasattr(res, 'data'):
            return res.data
        elif isinstance(res, dict) and 'data' in res:
            return res['data']
        return []
    except Exception as e:
        # Se der qualquer erro na conexão, ele não deixa o app travar
        return []

def salvar(texto):
    try:
        # Pegamos a palavra do dia com segurança
        palavra = "Não definida"
        if "palavra" in st.session_state:
            palavra = st.session_state.palavra
        elif hasattr(st, 'session_state') and 'palavra_do_dia' in dir():
            try:
                palavra = palavra_do_dia()
            except:
                pass

        # Enviamos apenas o essencial para o banco
        # O 'created_at' e o 'id' o Supabase gera sozinho automaticamente lá!
        supabase.table("mensagens").insert({
            "usuario": st.session_state.user,
            "mensagem": texto,
            "palavra_do_dia": palavra
        }).execute()
        
    except Exception as e:
        # Evita que a tela trave com erro técnico se o banco chiar
        st.error(f"Erro ao salvar mensagem no banco de dados. Verifique a tabela.")

def aplicar_highlight(text, word):
    return re.sub(f"({word})", r"<span class='highlight'>\1</span>", text, flags=re.I)

# =========================
# RENDERIZAÇÃO DA INTERFACE
# =========================

# Topbar fixa estilizada
st.markdown(f"""
<div style="background: #1E1E1E; padding: 12px; text-align: center; color: #FFD6DE; font-weight: 600; border-bottom: 1px solid #2A2A2A; border-radius: 8px; margin-bottom: 20px;">
💬 Chat Privado • Palavra do Dia: <span style="color:#FFF; background:#8B2E43; padding: 2px 8px; border-radius:4px;">{palavra_do_dia()}</span>
</div>
""", unsafe_allow_html=True)

# Carrega e exibe o histórico de mensagens
msgs = carregar()

for m in msgs:
    origem = "user" if m["usuario"] == user else "assistant"
    texto_formatado = aplicar_highlight(m["mensagem"], m.get("palavra_do_dia", palavra_do_dia()))
    time = m["created_at"][11:16] if "created_at" in m else ""
    
    with st.chat_message(origem):
        st.markdown(f"{texto_formatado} <span style='font-size: 11px; color: #9A9A9A; float: right; margin-top: 5px;'>{time}</span>", unsafe_allow_html=True)

# Input de mensagem fixo na parte inferior
if msg_input := st.chat_input("Digite sua mensagem..."):
    if palavra_do_dia().lower() not in msg_input.lower():
        st.error(f"Sua mensagem precisa conter a palavra do dia: {palavra_do_dia()}")
    else:
        salvar(msg_input)
        st.rerun()
