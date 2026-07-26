import os
import time
import requests
from datetime import datetime

# --- CONFIGURAÇÕES DA API E TELEGRAM ---
API_KEY = os.getenv("API_KEY", "3b074d04sw3ac472ka26afd38dbeb3db")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "SEU_TOKEN_TELEGRAM")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "SEU_CHAT_ID")

HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

# --- LISTA DE IDs DAS PRINCIPAIS LIGAS E SUBLIGAS PERMITIDAS ---
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

# Dicionário para armazenar o estado anterior das partidas
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
        return False

def monitorar_jogos():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Consultando partidas ao vivo na API...")
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"live": "all"}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=15)
        if response.status_code != 200:
            print(f"Erro na API: Status {response.status_code}")
            return
            
        dados = response.json().get("response", [])
        print(f"Total de jogos ao vivo retornados pela API: {len(dados)}")
        
        for jogo in dados:
            liga_id = jogo['league']['id']
            liga_nome = jogo['league']['name']
            home_team = jogo['teams']['home']['name']
            away_team = jogo['teams']['away']['name']
            
            # FILTRO DE LIGAS: Ignora se a liga não estiver na lista permitida
            if liga_id not in LIGAS_PERMITIDAS:
                continue
                
            fixture_id = jogo['fixture']['id']
            status_short = jogo['fixture']['status']['short']
            minuto = jogo['fixture']['status']['elapsed']
            
            # Log de rastreio para você ver no Railway que o jogo monitorado foi capturado
            print(f"-> Monitorando: {home_team} x {away_team} ({liga_nome}) | Status: {status_short} | Min: {minuto}'")
            
            # Filtro de tempo: apenas 1º ou 2º tempo, entre o minuto 10 e 82
            if status_short not in ['1H', '2H'] or minuto is None:
                continue
            if not (10 <= minuto <= 82):
                continue
                
            home_goals = jogo['goals']['home']
            away_goals = jogo['goals']['away']
            
            if home_goals is None or away_goals is None:
                continue
                
            chave_jogo = str(fixture_id)
            
            # Se é a primeira vez que vemos o jogo nesta execução, salvamos o placar atual para base de comparação futura
            if chave_jogo not in placar_anterior:
                placar_anterior[chave_jogo] = (home_goals, away_goals)
                continue
                
            g_h_ant, g_a_ant = placar_anterior[chave_jogo]
            
            # DETECÇÃO DE MUDANÇA DE PLACAR (Gol saiu!)
            if home_goals != g_h_ant or away_goals != g_a_ant:
                mensagem = (
                    f"🚨 **GOL DETECTADO!** 🚨\n\n"
                    f"🏆 *{liga_nome}* ({jogo['league']['country']})\n"
                    f"⚽ **{home_team} {home_goals} x {away_goals} {away_team}**\n"
                    f"⏱️ Minuto: **{minuto}'**\n\n"
                    f"🔥 *Momento ideal para conferir a pressão e as odds!*"
                )
                print(f"*** GOL DETECTADO E ENVIADO ***: {home_team} {home_goals} x {away_goals} {away_team} ({minuto}')")
                enviar_telegram(mensagem)
            
            # Atualiza o placar armazenado na memória
            placar_anterior[chave_jogo] = (home_goals, away_goals)
            
    except Exception as e:
        print(f"Erro na varredura: {e}")

if __name__ == "__main__":
    print("Robô de Futebol iniciado com sucesso (Modo de Diagnóstico e Alerta Otimizado).")
    while True:
        monitorar_jogos()
        time.sleep(120)
