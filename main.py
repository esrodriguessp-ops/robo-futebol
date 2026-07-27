import os
import requests

API_KEY = os.getenv("API_KEY", "3b074d04sw3ac472ka26afd38dbeb3db")
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

def teste_imediato():
    print("\n--- TESTE DE CONEXÃO E BUSCA DE DADOS ---")
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"date": "2026-07-26", "league": 71, "season": 2026}
    
    response = requests.get(url, headers=HEADERS, params=params, timeout=15)
    print(f"Status HTTP: {response.status_code}")
    
    dados = response.json().get("response", [])
    print(f"Partidas do Brasileirão encontradas hoje: {len(dados)}")
    
    for jogo in dados:
        home = jogo['teams']['home']['name']
        away = jogo['teams']['away']['name']
        status = jogo['fixture']['status']['short']
        print(f"Jogo: {home} x {away} | Status: {status}")
        
        if home == "Palmeiras" or away == "Palmeiras":
            fid = jogo['fixture']['id']
            ev_resp = requests.get("https://v3.football.api-sports.io/fixtures/events", headers=HEADERS, params={"fixture": fid})
            eventos = ev_resp.json().get("response", [])
            gols = [e for e in eventos if e.get('type') == 'Goal']
            print(f">>> Gols encontrados do Palmeiras na API: {len(gols)}")
            for g in gols:
                print(f"    - Gol de {g['player']['name']} aos {g['time']['elapsed']}' ({g['team']['name']})")

if __name__ == "__main__":
    teste_imediato()
