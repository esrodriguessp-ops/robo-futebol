import os
import time
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

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
    39, 40, 41, 42, 45,  # Inglaterra
    140, 141, 143,       # Espanha
    135, 136, 137,       # Itália
    78, 79, 81,          # Alemanha
    61, 62, 65,          # França
    94, 95, 96, 97,      # Portugal
    88, 89, 90,          # Holanda
    71, 72, 73,          # Brasil (Série A, Série B, Copa do Brasil)
    128, 129, 130,       # Argentina
    2, 3, 84,            # Internacionais
    13, 11               # Sul-Americanas
}

# Armazena os IDs dos gols já enviados para evitar duplicidade
gols_enviados = set()

def enviar_telegram(mensagem):
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
    fuso_br = ZoneInfo("America/Sao_Paulo")
    hora_atual = datetime.now(fuso_br).strftime('%H:%M:%S')
    
    print(f"\n[{hora_atual}] Consultando partidas ao vivo na API...")
    
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"live": "all"}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=15)
        if response.status_code != 200:
            print(f"Erro na API: Status {response.status_code}")
            return
            
        dados = response.json().get("response", [])
        print(f"Total de jogos ao vivo retornados pela API: {len(dados)}")
        
        jogos_monitorados = 0
        for jogo in dados:
            liga_id = jogo['league']['id']
            
            if liga_id not in LIGAS_PERMITIDAS:
                continue
                
            jogos_monitorados += 1
            fixture_id = jogo['fixture']['id']
            liga_nome = jogo['league']['name']
            home_team = jogo['teams']['home']['name']
            away_team = jogo['teams']['away']['name']
            status_short = jogo['fixture']['status']['short']
            minuto = jogo['fixture']['status']['elapsed']
            
            print(f"-> AO VIVO NA LIGA: {home_team} x {away_team} ({liga_nome}) | Status: {status_short} | Min: {minuto}'")
            
            if status_short not in ['1H', '2H'] or minuto is None:
                continue
            if not (10 <= minuto <= 82):
                continue
                
            home_goals = jogo['goals']['home']
            away_goals = jogo['goals']['away']
            
            if home_goals is None or away_goals is None:
                continue

            # BUSCA OS EVENTOS OFICIAIS DO JOGO (Garantia contra atraso de placar geral)
            url_events = "https://v3.football.api-sports.io/fixtures/events"
            params_events = {"fixture": fixture_id}
            resp_events = requests.get(url_events, headers=HEADERS, params=params_events, timeout=10)
            
            if resp_events.status_code == 200:
                eventos = resp_events.json().get("response", [])
                for ev in eventos:
                    if ev.get('type') == 'Goal' and ev.get('detail') in ['Normal Goal', 'Penalty', 'Own Goal']:
                        minuto_gol = ev['time']['elapsed']
                        jogador = ev['player']['name']
                        equipe_gol = ev['team']['name']
                        
                        # Cria uma chave única para este gol específico (Ex: ID do jogo + Minuto + Jogador)
                        chave_gol = f"{fixture_id}_{minuto_gol}_{jogador}"
                        
                        # Se o gol aconteceu entre o minuto 10 e 82 e ainda não foi enviado
                        if 10 <= minuto_gol <= 82 and chave_gol not in gols_enviados:
                            gols_enviados.add(chave_gol)
                            
                            mensagem = (
                                f"🚨 **GOL DETECTADO!** 🚨\n\n"
                                f"🏆 *{liga_nome}* ({jogo['league']['country']})\n"
                                f"⚽ **{home_team} {home_goals} x {away_goals} {away_team}**\n"
                                f"👤 Autor: *{jogador}* ({equipe_gol})\n"
                                f"⏱️ Minuto do Gol: **{minuto_gol}'**\n\n"
                                f"🔥 *Momento ideal para conferir a pressão e as odds!*"
                            )
                            print(f"*** GOL DETECTADO VIA EVENTOS E ENVIADO ***: {home_team} x {away_team} | Gol de {jogador} aos {minuto_gol}'")
                            enviar_telegram(mensagem)
                            
        print(f"Jogos filtrados nas ligas permitidas agora: {jogos_monitorados}")
            
    except Exception as e:
        print(f"Erro na varredura: {e}")

if __name__ == "__main__":
    print("Robô de Futebol iniciado com sucesso (Modo Avançado com Checagem de Eventos).")
    while True:
        monitorar_jogos()
        time.sleep(120)
