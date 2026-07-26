import os
import time
import requests
from datetime import datetime

# --- CONFIGURAÇÕES DA API E TELEGRAM ---
API_KEY = os.getenv("API_KEY", "3b074d04sw3ac472ka26afd38dbeb3db") # Sua chave atual
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "SEU_TOKEN_TELEGRAM")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "SEU_CHAT_ID")

HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

# --- LISTA DE IDs DAS PRINCIPAIS LIGAS E SUBLIGAS PERMITIDAS ---
# Inclui: Premier League, Championship, La Liga, Serie A, Bundesliga, Ligue 1, 
# Primeira Liga, Eredivisie, Brasileirão Série A e B, Argentina, Copas e Internacionais principais.
LIGAS_PERMITIDAS = {
    39, 40, 41, 42, 45,  # Inglaterra (Premier League, Championship, League One, Two, FA Cup)
    140, 141, 143,       # Espanha (La Liga, Segunda, Copa del Rey)
    135, 136, 137,       # Itália (Serie A, Serie B, Coppa Italia)
    78, 79, 81,          # Alemanha (Bundesliga, 2. Bundesliga, DFB-Pokal)
    61, 62, 65,          # França (Ligue 1, Ligue 2, Coupe de France)
    94, 95, 96, 97,      # Portugal (Liga Portugal, 2, Taça de Portugal, Taça da Liga)
    88, 89, 90,          # Holanda (Eredivisie, Eerste Divisie, KNVB Cup)
    71, 72, 73,          # Brasil (Série A, Série B, Copa do Brasil)
    128, 129, 130,       # Argentina (Liga Profesional, Primera Nacional, Copa)
    2, 3, 84,            # Internacionais (Champions League, Europa League, Conference League)
    13, 11               # Sul-Americanas (Libertadores, Sul-Americana)
}

# Dicionário para armazenar o estado anterior das partidas e evitar alertas duplicados
placar_anterior = {}

def enviar_telegram(mensagem):
    """Envia alerta para o Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': mensagem,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Erro ao enviar mensagem para o Telegram: {e}")
        return false

def monitorar_jogos():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Consultando partidas ao vivo na API...")
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"live": "all"}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=15)
        if response.status_code != 200:
            print(f"Erro na API: Status {response.status_code}")
            return
            
        dados = response.json().get("response", [])
        print(f"Partidas encontradas ao vivo agora: {len(dados)}")
        
        for jogo in dados:
            liga_id = jogo['league']['id']
            
            # FILTRO DE LIGAS: Ignora se a liga não estiver na nossa lista permitida
            if liga_id not in LIGAS_PERMITIDAS:
                continue
                
            fixture_id = jogo['fixture']['id']
            status_short = jogo['fixture']['status']['short']
            minuto = jogo['fixture']['status']['elapsed']
            
            # Filtro de tempo: apenas 1º ou 2º tempo, entre o minuto 10 e 82
            if status_short not in ['1H', '2H'] or minuto is None:
                continue
            if not (10 <= minuto <= 82):
                continue
                
            home_team = jogo['teams']['home']['name']
            away_team = jogo['teams']['away']['name']
            home_goals = jogo['goals']['home']
            away_goals = jogo['goals']['away']
            
            if home_goals is None or away_goals is None:
                continue
                
            chave_jogo = str(fixture_id)
            
            # Verifica se já temos o registro deste jogo
            if chave_jogo in placar_anterior:
                gols_h_ant, g_a_ant = placar_anterior[chave_jogo]
                
                # DETECÇÃO DE MUDANÇA DE PLACAR (Gol saiu!)
                if home_goals != g_h_ant or away_goals != g_a_ant:
                    mensagem = (
                        f"🚨 **GOL DETECTADO!** 🚨\n\n"
                        f"🏆 *{jogo['league']['name']}* ({jogo['league']['country']})\n"
                        f"⚽ **{home_team} {home_goals} x {away_goals} {away_team}**\n"
                        f"⏱️ Minuto: **{minuto}'**\n\n"
                        f"🔥 *Momento ideal para conferir a pressão e as odds!*"
                    )
                    print(f"Gol detectado em: {home_team} x {away_team} ({minuto}')")
                    enviar_telegram(mensagem)
            
            # Atualiza o placar armazenado na memória
            placar_anterior[chave_jogo] = (home_goals, away_goals)
            
    except Exception as e:
        print(f"Erro na varredura: {e}")

if __name__ == "__main__":
    print("Robô de Futebol iniciado com sucesso (Filtro de Ligas + Intervalo de 2 min).")
    while True:
        monitorar_jogos()
        # Aguarda 120 segundos (2 minutos) para a próxima consulta, economizando requisições
        time.sleep(120)
