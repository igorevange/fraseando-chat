import streamlit as st
from supabase import create_client, Client
import datetime

# ==========================================
# CONFIGURAÇÃO DA PÁGINA (Precisa ser o primeiro comando)
# ==========================================
st.set_page_config(page_title="Chat do Casal", page_icon="💬", layout="centered")

# Estilização básica para o visual escuro e tags de tempo
st.markdown("""
<style>
    .stApp { background-color: #121212; color: #FFFFFF; }
    .keyword-tag { font-size: 11px; font-style: italic; color: #FFB7B2; display: block; margin-top: 4px; }
    .time-tag { font-size: 10px; color: #888888; float: right; margin-top: 4px; }
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
st.markdown(f"### 💬 Chat Privado • *Palavra do Dia:* **{st.session_state.palavra}**")

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
        st.sidebar.error(f"Erro ao ler histórico: {str(e)}")
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
# CARREGAMENTO E EXIBIÇÃO DO HISTÓRICO
# ==========================================
lista_mensagens = carregar()

if lista_mensagens:
    for m in lista_mensagens:
        msg_usuario = m.get("usuario")
        
        # 1. Define o ÍCONE e o NOME real de quem ESCREVEU a mensagem no banco
        if msg_usuario == "be":
            avatar_icone = "🦇"
            nome_exibicao = "Bê" if user == "be" else "Meu Amor (Bê)"
        elif msg_usuario == "macaquinha":
            avatar_icone = "🐵"
            nome_exibicao = "Macaquinha" if user == "macaquinha" else "Minha Macaquinha 💜"
        else:
            avatar_icone = "👤"
            nome_exibicao = msg_usuario

        # 2. Define o LADO da tela baseado em QUEM ESTÁ OLHANDO o app agora
        # Se a mensagem do banco for igual ao usuário logado -> Direita ("user")
        # Se for do parceiro -> Esquerda ("assistant")
        if msg_usuario == user:
            lado_tela = "user"
        else:
            lado_tela = "assistant"

        # Tratamento do horário
        hora_formatada = ""
        criado_em = m.get("created_at")
        if criado_em and "T" in criado_em:
            try:
                hora_formatada = criado_em.split("T")[1][:5]
            except:
                hora_formatada = ""

        palavra_salva = m.get('palavra_do_dia', '---')
        texto_mensagem = m.get('mensagem', '')

        if texto_mensagem:
            # Forçamos o lado_tela para o alinhamento correto e o avatar fixo de quem enviou
            with st.chat_message(lado_tela, avatar=avatar_icone):
                st.markdown(f"**{nome_exibicao}**")
                st.write(texto_mensagem)
                st.markdown(f'<span class="keyword-tag">🔑 Palavra: {palavra_salva}</span> <span class="time-tag">{hora_formatada}</span>', unsafe_allow_html=True)
else:
    st.info("Nenhuma mensagem enviada ainda. Seja o primeiro a quebrar o gelo com a palavra do dia!")

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
            if palavra_atual in msg_input.lower():
                if salvar(msg_input):
                    st.rerun()
            else:
                st.error("Sua frase não contém a palavra do dia! Tente novamente.")
