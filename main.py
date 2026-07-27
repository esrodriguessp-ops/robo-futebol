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

def teste_retroativo():
    fuso_br = ZoneInfo("America/Sao_Paulo")
    data_hoje = datetime.now(fuso_br).strftime('%Y-%m-%d')
    
    print(f"\n==================================================")
    print(f"[{data_hoje}] EXECUTANDO BUSCA RETROATIVA DE TESTE...")
    print(f"==================================================")
    
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"date": data_hoje}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=15)
        if response.status_code != 200:
            print(f"Erro na API: Status {response.status_code}")
            return
            
        dados = response.json().get("response", [])
        print(f"Total de partidas cadastradas hoje na API: {len(dados)}")
        
        encontrados = 0
        for jogo in dados:
            liga_id = jogo['league']['id']
            
            # Filtra apenas as ligas da nossa lista permitida
            if liga_id not in LIGAS_PERMITIDAS:
                continue
                
            encontrados += 1
            liga_nome = jogo['league']['name']
            home_team = jogo['teams']['home']['name']
            away_team = jogo['teams']['away']['name']
            home_goals = jogo['goals']['home']
            away_goals = jogo['goals']['away']
            status = jogo['fixture']['status']['short']
            minuto = jogo['fixture']['status']['elapsed']
            
            print(f"⚽ [{liga_nome}] {home_team} {home_goals} x {away_goals} {away_team} | Status: {status} (Min: {minuto})")
            
        print(f"Total de jogos encontrados nas ligas monitoradas hoje: {encontrados}")
        print(f"==================================================\n")
            
    except Exception as e:
        print(f"Erro na busca retroativa: {e}")

if __name__ == "__main__":
    # Roda o teste retroativo logo na inicialização para você ver o resultado no Railway
    teste_retroativo()
    
    # Depois continua o loop normal de monitoramento
    while True:
        print("Aguardando próximo ciclo de monitoramento ao vivo...")
        time.sleep(120)
