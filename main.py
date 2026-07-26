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

placar_anterior = {}

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
    # Pega a data exata no fuso horário do Brasil para evitar conflitos de UTC do servidor
    fuso_br = ZoneInfo("America/Sao_Paulo")
    data_hoje = datetime.now(fuso_br).strftime('%Y-%m-%d')
    hora_atual = datetime.now(fuso_br).strftime('%H:%M:%S')
    
    print(f"\n[{data_hoje} {hora_atual}] Consultando jogos do dia na API...")
    
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"date": data_hoje}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=15)
        if response.status_code != 200:
            print(f"Erro na API: Status {response.status_code}")
            return
            
        dados = response.json().get("response", [])
        print(f"Total de jogos encontrados para hoje: {len(dados)}")
        
        jogos_ao_vivo = 0
        for jogo in dados:
            status_short = jogo['fixture']['status']['short']
            
            # Filtra apenas os jogos que estão rolando AO VIVO
            if status_short not in ['1H', 'HT', '2H', 'ET', 'P']:
                continue
                
            jogos_ao_vivo += 1
            liga_id = jogo['league']['id']
            liga_nome = jogo['league']['name']
            home_team = jogo['teams']['home']['name']
            away_team = jogo['teams']['away']['name']
            
            # FILTRO DE LIGAS
            if liga_id not in LIGAS_PERMITIDAS:
                continue
                
            minuto = jogo['fixture']['status']['elapsed']
            print(f"-> AO VIVO NA LIGA PERMITIDA: {home_team} x {away_team} ({liga_nome}) | Min: {minuto}'")
            
            if minuto is None or not (10 <= minuto <= 82):
                continue
                
            home_goals = jogo['goals']['home']
            away_goals = jogo['goals']['away']
            
            if home_goals is None or away_goals is None:
                continue
                
            fixture_id = jogo['fixture']['id']
            chave_jogo = str(fixture_id)
            
            if chave_jogo not in placar_anterior:
                placar_anterior[chave_jogo] = (home_goals, away_goals)
                continue
                
            g_h_ant, g_a_ant = placar_anterior[chave_jogo]
            
            # DETECÇÃO DE GOL
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
            
            placar_anterior[chave_jogo] = (home_goals, away_goals)
            
        print(f"Jogos ao vivo no total geral agora: {jogos_ao_vivo}")
            
    except Exception as e:
        print(f"Erro na varredura: {e}")

if __name__ == "__main__":
    print("Robô de Futebol iniciado com sucesso (Fuso Horário Corrigido).")
    while True:
        monitorar_jogos()
        time.sleep(120)
