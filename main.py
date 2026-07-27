import os
import requests

# --- CHAVE E CONFIGURAÇÕES FIXAS (Blindado contra falha do Railway) ---
API_KEY = "3b074d04sw3ac472ka26afd38dbeb3db"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "SEU_TOKEN_TELEGRAM")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "SEU_CHAT_ID")

HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

def testar_conexao_e_jogos():
    print("\n--- TESTANDO CONEXÃO COM A API-FOOTBALL ---")
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"date": "2026-07-26", "league": 71, "season": 2026}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=15)
        print(f"Status HTTP da Resposta: {response.status_code}")
        
        dados = response.json()
        
        # Se houver erro de chave, exibe claramente
        if 'errors' in dados and dados['errors']:
            print(f"Erro retornado pela API: {dados['errors']}")
            return

        partidas = dados.get("response", [])
        print(f"Sucesso! Partidas do Brasileirão encontradas hoje: {len(partidas)}")
        
        for jogo in partidas:
            home = jogo['teams']['home']['name']
            away = jogo['teams']['away']['name']
            status = jogo['fixture']['status']['short']
            print(f"⚽ Jogo: {home} x {away} | Status: {status}")
            
            # Testa os eventos (gols) do jogo
            fid = jogo['fixture']['id']
            ev_resp = requests.get("https://v3.football.api-sports.io/fixtures/events", headers=HEADERS, params={"fixture": fid})
            eventos = ev_resp.json().get("response", [])
            gols = [e for e in eventos if e.get('type') == 'Goal']
            print(f"   -> Gols mapeados pela API: {len(gols)}")
            for g in gols:
                print(f"      - Gol de {g['player']['name']} aos {g['time']['elapsed']}' ({g['team']['name']})")
                
    except Exception as e:
        print(f"Erro crítico na requisição: {e}")

if __name__ == "__main__":
    testar_conexao_e_jogos()
