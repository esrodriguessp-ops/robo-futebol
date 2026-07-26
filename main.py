import time
import requests

# ================= CONFIGURAÇÕES =================
# Insira aqui os seus dados reais do Telegram e da API
TELEGRAM_TOKEN = "SEU_TELEGRAM_TOKEN"
CHAT_ID = "SEU_CHAT_ID"
API_FOOTBALL_KEY = "SUA_CHAVE_API_FOOTBALL"

# Configurações das Ligas (vazio = todas as ligas disponíveis)
LIGAS_PERMITIDAS = [] 
# =================================================

def enviar_telegram(mensagem):
    """Envia a mensagem de alerta para o seu Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem para o Telegram: {e}")
        return False

def buscar_jogos_ao_vivo():
    """Busca as partidas que estão acontecendo ao vivo na API-Football"""
    url = "https://v3.football.api-sports.io/fixtures"
    querystring = {"live": "all"}
    headers = {
        "x-rapidapi-host": "v3.football.api-sports.io",
        "x-rapidapi-key": API_FOOTBALL_KEY
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        if response.status_code == 200:
            return response.json().get("response", [])
        else:
            print(f"⚠️ Erro na API: Status {response.status_code}")
            return []
    except Exception as e:
        print(f"⚠️ Falha de conexão ao buscar jogos: {e}")
        return []

def main():
    print("=============================================")
    print("   ROBÔ DE OPORTUNIDADES - FAVORITO PRÉ-LIVE ")
    print("=============================================")
    print("Monitorando placar, pressão, cantos e cartões...")
    
    # Dicionário para guardar o histórico e evitar alertas duplicados por jogo
    historico_placar = {}

    while True:
        print("\n🔄 Consultando partidas ao vivo na API...")
        partidas = buscar_jogos_ao_vivo()
        print(f"📊 Partidas encontradas ao vivo agora: {len(partidas)}")

        for jogo in partidas:
            fixture_id = jogo['fixture']['id']
            status_tempo = jogo['fixture']['status']['elapsed']
            home_team = jogo['teams']['home']['name']
            away_team = jogo['teams']['away']['name']
            
            # Placar atual
            home_goals = jogo['goals']['home']
            away_goals = jogo['goals']['away']

            # Filtro básico de tempo (exemplo: monitorar até os 82 minutos)
            if status_tempo and 10 <= status_tempo <= 82:
                # Lógica de rastreio de mudança de placar e envio de alerta
                if fixture_id in historico_placar:
                    antigo_home, antigo_away = historico_placar[fixture_id]
                    
                    # Se o placar mudou desde a última varredura
                    if home_goals != antigo_home or away_goals != antigo_away:
                        print(f"GOAL! Mudança detectada em {home_team} {home_goals} x {away_goals} {away_team}")
                        
                        # Aqui você coloca a regra se o favorito sofreu gol e dispara o Telegram:
                        # mensagem = f"🚨 Alerta! O favorito sofreu gol em {home_team} x {away_team}!"
                        # enviar_telegram(mensagem)
                
                # Atualiza o histórico com o placar atual do jogo
                historico_placar[fixture_id] = (home_goals, away_goals)

        # Aguarda 1 minuto antes da próxima verificação para não estourar o limite da API
        time.sleep(60)

if __name__ == "__main__":
    main()
