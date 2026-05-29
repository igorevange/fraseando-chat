import streamlit as st
from supabase import create_client, Client
import datetime
import pandas as pd

# ==========================================
# CONFIGURAÇÃO DA PÁGINA (Precisa ser o primeiro comando)
# ==========================================
st.set_page_config(page_title="Chat do Casal", page_icon="💬", layout="centered")

# Estilização limpa para o visual escuro e tags de tempo
st.markdown("""
<style>
    .stApp { background-color: #121212; color: #FFFFFF; }
    .keyword-tag { font-size: 11px; font-style: italic; color: #FFB7B2; display: block; margin-top: 4px; }
    .time-tag { font-size: 10px; color: #888888; float: right; margin-top: 4px; }
    
    /* Margem segura para a última mensagem não sumir atrás do input fixo */
    .main .block-container {
        padding-bottom: 120px !important;
    }
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
    palavras = ["espelho", "café", "abraço", "sorriso", "destino", "bilhete", "luar"]
    dia_ano = datetime.datetime.now().timetuple().tm_yday
    indice = dia_ano % len(palavras)
    return palavras[indice]

st.session_state.palavra = palavra_do_dia()

# ==========================================
# SISTEMA DE LOGIN
# ==========================================
if "user" not in st.session_state:
    st.markdown("## 💬 Chat Privado")
    user_input = st.text_input("Código de Acesso", type="password")
    if st.button("Entrar"):
        if user_input in ["be", "macaquinha"]:
            st.session_state.user = user_input
            st.rerun()
        else:
            st.error("Código inválido!")
    st.stop()

user = st.session_state.user

# ==========================================
# CABEÇALHO DO APP
# ==========================================
st.markdown(f"### 💬 Chat Privado")
st.markdown(f"### *Palavra do Dia:* **{st.session_state.palavra}**")

# ==========================================
# FUNÇÕES DO BANCO DE DADOS
# ==========================================
def carregar():
    try:
        res = supabase.table("mensagens").select("*").execute()
        dados = []
        if hasattr(res, 'data') and res.data is not None:
            dados = res.data
        elif isinstance(res, dict) and 'data' in res:
            dados = res['data']
            
        if dados:
            try:
                dados = sorted(dados, key=lambda x: x.get('created_at', ''))
            except:
                pass
        return dados
    except Exception as e:
        return []

def salvar(texto):
    try:
        palavra = st.session_state.get('palavra', 'Não definida')
        supabase.table("mensagens").insert({
            "usuario": user,
            "mensagem": texto,
            "palavra_do_dia": palavra
        }).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {str(e)}")
        return False

# ==========================================
# BLOCO DO HISTÓRICO EM TEMPO REAL (Fragment)
# ==========================================
# O decorator @st.fragment faz apenas este bloco se atualizar em segundo plano,
# buscando novas mensagens a cada 1 segundo sem travar a digitação do usuário.
@st.fragment(run_every=1.0)
def exibir_historico_tempo_real():
    lista_mensagens = carregar()

    if lista_mensagens:
        for m in lista_mensagens:
            msg_usuario = m.get("usuario")
            
            # Define o ÍCONE e o NOME de quem enviou
            if msg_usuario == "be":
                avatar_icone = "🦇"
                nome_exibicao = "Bê" if user == "be" else "Meu Bê"
            elif msg_usuario == "macaquinha":
                avatar_icone = "🐵"
                nome_exibicao = "Macaquinha" if user == "macaquinha" else "Minha Macaquinha 💜"
            else:
                avatar_icone = "👤"
                nome_exibicao = msg_usuario

            # Define o LADO da tela (user = direita, assistant = esquerda)
            if msg_usuario == user:
                lado_tela = "user"
            else:
                lado_tela = "assistant"

            # TRATAMENTO SEGURO DA DATA E HORÁRIO (Usando Pandas)
            carimbo_tempo = ""
            criado_em = m.get("created_at")
            
            if criado_em:
                try:
                    dt = pd.to_datetime(criado_em, utc=True)
                    dt_brasil = dt.tz_convert("America/Sao_Paulo")
                    carimbo_tempo = dt_brasil.strftime("%d/%m/%Y %H:%M")
                except:
                    carimbo_tempo = ""

            palavra_salva = m.get('palavra_do_dia', '---')
            texto_mensagem = m.get('mensagem', '')

            if texto_mensagem:
                with st.chat_message(lado_tela, avatar=avatar_icone):
                    st.markdown(f"**{nome_exibicao}**")
                    st.write(texto_mensagem)
                    st.markdown(f'<span class="keyword-tag">🔑 Palavra: {palavra_salva}</span> <span class="time-tag">{carimbo_tempo}</span>', unsafe_allow_html=True)
    else:
        st.info("Nenhuma mensagem enviada ainda. Seja o primeiro a quebrar o gelo com a palavra do dia!")

# Executa a caixa isolada do histórico
exibir_historico_tempo_real()

# ==========================================
# ÁREA DE ENVIO DE MENSAGENS (Fixada na base)
# ==========================================
msg_input = st.chat_input("Digite sua mensagem...")

if msg_input:
    if msg_input.strip() == "":
        st.warning("Tem que digitar alguma coisa antes de enviar né.")
    else:
        palavra_atual = st.session_state.palavra.lower()
        if palavra_atual in msg_input.lower():
            if salvar(msg_input):
                st.rerun() # Atualiza o app imediatamente ao enviar
        else:
            st.error("Seu lesado(a), tua frase não contém a palavra do dia! Tente novamente.")
