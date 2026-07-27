import os
import requests

API_KEY = os.getenv("API_KEY", "3b074d04sw3ac472ka26afd38dbeb3db")
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

def teste_com_temporada():
    print("\n--- TESTE DE BUSCA COM TEMPORADA 2026 ---")
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"date": "2026-07-26", "league": 71, "season": 2026}
    
    response = requests.get(url, headers=HEADERS, params=params, timeout=15)
    print(f"Status HTTP: {response.status_code}")
    
    dados = response.json().get("response", [])
    print(f"Total de jogos do Brasileirão encontrados: {len(dados)}")
    
    if len(dados) > 0:
        for jogo in dados:
            home = jogo['teams']['home']['name']
            away = jogo['teams']['away']['name']
            status = jogo['fixture']['status']['short']
            print(f"⚽ Jogo: {home} x {away} | Status: {status}")
            
            # Busca os eventos para testar os gols
            fid = jogo['fixture']['id']
            ev_resp = requests.get("https://v3.football.api-sports.io/fixtures/events", headers=HEADERS, params={"fixture": fid})
            eventos = ev_resp.json().get("response", [])
            gols = [e for e in eventos if e.get('type'] == 'Goal']
            print(f"   -> Gols na API para este jogo: {len(gols)}")
            for g in gols:
                print(f"      - Gol de {g['player']['name']} aos {g['time']['elapsed']}' ({g['team']['name']})")
    else:
        print("Ainda retornou 0. Vamos validar a resposta crua da API.")
        print(response.json())

if __name__ == "__main__":
    teste_com_temporada()
