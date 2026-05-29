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
# FUNÇÃO DA PALAVRA DO DIA (366 Palavras para o Ano Bissexto)
# ==========================================
def palavra_do_dia():
    palavras = [
        "espelho", "café", "abraço", "sorriso", "destino", "bilhete", "luar", "pipoca", "Cinema", "Almofada",
        "coberta", "chocolate", "cafuné", "sussurro", "segredo", "canção", "viagem", "parque", "sorvete", "beijo",
        "nuvem", "estrela", "sol", "chuva", "vento", "mar", "praia", "concha", "Farol", "barco",
        "bússola", "mapa", "tesouro", "chave", "cadeado", "carta", "carimbo", "fotografia", "quadro", "moldura",
        "jardim", "flor", "pétala", "perfume", "aroma", "tempero", "receita", "panela", "jantar", "vela",
        "fogo", "lareira", "faísca", "calor", "inverno", "outono", "primavera", "verão", "sol do dia", "amanhecer",
        "entardecer", "crepúsculo", "noite", "madrugada", "relógio", "tempo", "calendário", "agenda", "plano", "sonho",
        "desejo", "promessa", "aliança", "anel", "colar", "pulseira", "brinco", "espelho", "pente", "escova",
        "toalha", "banho", "espuma", "bolha", "sabonete", "shampoo", "creme", "perfume", "roupa", "casaco",
        "meia", "sapato", "chinelo", "pijama", "cama", "lençol", "travesseiro", "colchão", "quarto", "sala",
        "cozinha", "varanda", "quintal", "portão", "janela", "cortina", "tapete", "sofá", "poltrona", "estante",
        "livro", "página", "capítulo", "história", "conto", "poesia", "verso", "rima", "música", "nota",
        "acorde", "ritmo", "dança", "passo", "baile", "festa", "balão", "confete", "bolo", "doce",
        "bala", "chiclete", "pirulito", "gelatina", "pudim", "torta", "mousse", "sorvete", "picolé", "fruta",
        "maçã", "banana", "morango", "uva", "laranja", "limão", "abacaxi", "melancia", "melão", "pêssego",
        "ameixa", "cereja", "framboesa", "amora", "mirtilo", "kiwi", "manga", "maracujá", "goiaba", "caju",
        "coco", "castanha", "noz", "amêndoa", "amendoim", "pipoca", "biscoito", "bolacha", "pão", "torrada",
        "manteiga", "requeijão", "queijo", "presunto", "ovo", "omelete", "tapioca", "cereal", "leite", "Iogurte",
        "suco", "chá", "café", "chocolate", "achocolatado", "água", "refrigerante", "cerveja", "vinho", "champanhe",
        "coquetel", "gelo", "limão", "hortelã", "canela", "cravo", "baunilha", "mel", "açúcar", "adoçante",
        "sal", "pimenta", "azeite", "vinagre", "alho", "cebola", "tomate", "alface", "cenoura", "batata",
        "arroz", "feijão", "macarrão", "carne", "frango", "peixe", "camarão", "sushi", "pizza", "hambúrguer",
        "pastel", "coxinha", "pão de queijo", "empada", "folhado", "croissant", "waffle", "panqueca", "crepe", "churros",
        "pipoca", "algodão doce", "maçã do amor", "carrossel", "montanha russa", "roda gigante", "parque", "circo", "teatro", "show",
        "concerto", "museu", "exposição", "galeria", "arte", "pintura", "escultura", "desenho", "esboço", "grafite",
        "mural", "parede", "teto", "chão", "tapete", "almofada", "pufe", "rede", "balanço", "cadeira",
        "mesa", "balcão", "armário", "gaveta", "prateleira", "cabide", "espelho", "quadro", "relógio", "luminária",
        "lustre", "abajur", "vela", "castiçal", "fósforo", "isqueiro", "lanterna", "farol", "poste", "luz",
        "sombra", "reflexo", "brilho", "faísca", "chama", "fogo", "fumaça", "cinza", "carvão", "lenha",
        "lareira", "aquecedor", "ventilador", "ar condicionado", "clima", "tempo", "previsão", "nuvem", "céu", "azul",
        "branco", "preto", "cinza", "vermelho", "rosa", "azul marinho", "verde", "amarelo", "laranja", "roxo",
        "violeta", "lilás", "marrom", "bege", "dourado", "prateado", "bronze", "arco-íris", "prisma", "lente",
        "óculos", "olhar", "olho", "cílio", "sobrancelha", "testa", "bochecha", "nariz", "boca", "lábio",
        "dente", "língua", "queixo", "pescoço", "ombro", "braço", "cotovelo", "pulso", "mão", "dedo",
        "unha", "palma", "peito", "coração", "batida", "pulso", "respiração", "fôlego", "suspiro", "risada",
        "gargalhada", "sorriso", "covinha", "olhar", "piscada", "aceno", "gesto", "toque", "carinho", "cafuné",
        "massagem", "abraço", "aperto", "beijo", "estalo", "mordida", "cócegas", "brincadeira", "susto", "surpresa",
        "presente", "embrulho", "laço", "fita", "papel", "cartão", "mensagem", "notificação", "ligação", "conversa",
        "papo", "áudio", "vídeo", "foto", "selfie", "lembrança", "memória", "passado", "presente do dia", "futuro"
    ]
    
    # O tm_yday vai de 1 até 366 em anos bissextos
    dia_ano = datetime.datetime.now().timetuple().tm_yday
    
    # Usamos o operador % para garantir que o índice sempre caia num intervalo válido da lista
    indice = (dia_ano - 1) % len(palavras)
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
# BLOCO DO HISTÓRICO EM ABAS DIÁRIAS (Fragment)
# ==========================================
@st.fragment(run_every=1.0)
def exibir_historico_tempo_real():
    lista_mensagens = carregar()
    
    # Pega o dia de hoje no formato de data brasileiro
    data_hoje_str = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%d/%m/%Y")

    if lista_mensagens:
        # Agrupa as mensagens com base no dia em que foram enviadas
        mensagens_por_dia = {}
        
        for m in lista_mensagens:
            criado_em = m.get("created_at")
            if criado_em:
                try:
                    dt_br = pd.to_datetime(criado_em, utc=True).tz_convert("America/Sao_Paulo")
                    data_formatada = dt_br.strftime("%d/%m/%Y")
                except:
                    data_formatada = "Outros"
            else:
                data_formatada = "Outros"
                
            if data_formatada not in mensagens_por_dia:
                mensagens_por_dia[data_formatada] = []
            mensagens_por_dia[data_formatada].append(m)

        # Ordena os dias passados em formato decrescente (mais recentes primeiro)
        dias_passados = sorted(
            [dia for dia in mensagens_por_dia.keys() if dia != data_hoje_str], 
            key=lambda x: pd.to_datetime(x, format="%d/%m/%Y"), 
            reverse=True
        )
        
        # Cria as abas. A aba "📅 Hoje" sempre encabeça a lista à esquerda
        titulos_abas = ["Hoje"] + dias_passados
        abas_criadas = st.tabs(titulos_abas)

        # Renderizador interno de bolhas de mensagem
        def renderizar_mensagens(lista):
            for m in lista:
                msg_usuario = m.get("usuario")
                
                if msg_usuario == "be":
                    avatar_icone = "🦇"
                    nome_exibicao = "Bê" if user == "be" else "Meu Bê"
                elif msg_usuario == "macaquinha":
                    avatar_icone = "🐵"
                    nome_exibicao = "Macaquinha" if user == "macaquinha" else "Minha Macaquinha 💜"
                else:
                    avatar_icone = "👤"
                    nome_exibicao = msg_usuario

                lado_tela = "user" if msg_usuario == user else "assistant"

                carimbo_tempo = ""
                criado_em_msg = m.get("created_at")
                if criado_em_msg:
                    try:
                        dt = pd.to_datetime(criado_em_msg, utc=True)
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

        # Popula a Aba "📅 Hoje"
        with abas_criadas[0]:
            mensagens_hoje = mensagens_por_dia.get(data_hoje_str, [])
            if mensagens_hoje:
                renderizar_mensagens(mensagens_hoje)
            else:
                st.info("Nenhuma mensagem enviada hoje ainda. Comece a conversar na barra abaixo!")

        # Popula as Abas dos dias anteriores (em ordem decrescente)
        for idx, dia in enumerate(dias_passados):
            with abas_criadas[idx + 1]:
                renderizar_mensagens(mensagens_por_dia[dia])
    else:
        st.info("Nenhuma mensagem enviada ainda. Seja o(a) primeiro(a) a quebrar o gelo com a palavra do dia!")

# Executa o histórico em abas dinâmicas
exibir_historico_tempo_real()

# ==========================================
# ÁREA DE ENVIO DE MENSAGENS (Fixada na base)
# ==========================================
msg_input = st.chat_input("Digite sua mensagem...")

if msg_input:
    palavra_atual = st.session_state.palavra.lower()
    mensagem_limpa = msg_input.strip().lower()
    
    # 1ª VALIDAÇÃO: Se a mensagem for EXATAMENTE a palavra do dia sozinha
    if mensagem_limpa == palavra_atual:
        st.warning(f'Cadê a criatividade? Só "{msg_input.strip()}", é sério?')
        
    # 2ª VALIDAÇÃO: Se a palavra do dia está contida no meio de uma frase maior
    elif palavra_atual in mensagem_limpa:
        if salvar(msg_input):
            st.rerun() 
            
    # 3ª VALIDAÇÃO: Se não digitou a palavra de jeito nenhum
    else:
        st.error("Oh lesado(a), tua frase não contém a palavra do dia! Tente novamente.")
