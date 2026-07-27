import os
import time
import requests

# --- CONFIGURAÇÕES DA API E TELEGRAM ---
API_KEY = os.getenv("API_KEY", "3b074d04sw3ac472ka26afd38dbeb3db")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "SEU_TOKEN_TELEGRAM")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "SEU_CHAT_ID")

HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

# IDs das principais ligas para teste e monitoramento
LIGAS_PERMITIDAS = {39, 40, 140, 135, 78, 61, 71, 72, 73, 128, 2, 3}

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
        print(f"Erro no Telegram: {e}")
        return False

def monitorar_jogos():
    print("\nExecutando varredura na API...")
    
    # Usando o endpoint live direto com tratamento universal
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"live": "all"}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=15)
        print(f"Status HTTP da API: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Erro retornado pela API: {response.text}")
            return
            
        dados = response.json().get("response", [])
        print(f"Total bruto retornado pela API (live=all): {len(dados)}")
        
        if len(dados) == 0:
            print("Nenhum jogo ao vivo no momento global da API.")
            return

        for jogo in dados:
            liga_id = jogo['league']['id']
            liga_nome = jogo['league']['name']
            home_team = jogo['teams']['home']['name']
            away_team = jogo['teams']['away']['name']
            status_short = jogo['fixture']['status']['short']
            minuto = jogo['fixture']['status']['elapsed']
            
            print(f"Partida achada: {home_team} x {away_team} | Liga ID: {liga_id} | Status: {status_short} | Min: {minuto}")
            
            if liga_id not in LIGAS_PERMITIDAS:
                continue
                
            if status_short not in ['1H', '2H', 'HT']:
                continue
                
            fixture_id = jogo['fixture']['id']
            home_goals = jogo['goals']['home']
            away_goals = jogo['goals']['away']
            
            if home_goals is None or away_goals is None:
                continue

            # Consulta os eventos do jogo para pegar o gol exato
            url_events = "https://v3.football.api-sports.io/fixtures/events"
            resp_events = requests.get(url_events, headers=HEADERS, params={"fixture": fixture_id}, timeout=10)
            
            if resp_events.status_code == 200:
                eventos = resp_events.json().get("response", [])
                for ev in eventos:
                    if ev.get('type') == 'Goal' and ev.get('detail') in ['Normal Goal', 'Penalty', 'Own Goal']:
                        minuto_gol = ev['time']['elapsed']
                        jogador = ev.get('player', {}).get('name', 'Desconhecido')
                        equipe_gol = ev.get('team', {}).get('name', '')
                        
                        chave_gol = f"{fixture_id}_{minuto_gol}_{jogador}"
                        
                        if 10 <= minuto_gol <= 82 and chave_gol not in gols_enviados:
                            gols_enviados.add(chave_gol)
                            
                            msg = (
                                f"🚨 **GOL DETECTADO!** 🚨\n\n"
                                f"🏆 *{liga_nome}*\n"
                                f"⚽ **{home_team} {home_goals} x {away_goals} {away_team}**\n"
                                f"👤 Autor: *{jogador}* ({equipe_gol})\n"
                                f"⏱️ Minuto: **{minuto_gol}'**"
                            )
                            print(f"*** ENVIANDO PARA O TELEGRAM ***: {home_team} x {away_team} aos {minuto_gol}'")
                            enviar_telegram(msg)
                            
    except Exception as e:
        print(f"Erro crítico na execução: {e}")

if __name__ == "__main__":
    print("Robô limpo iniciado com sucesso.")
    while True:
        monitorar_jogos()
        time.sleep(120)
