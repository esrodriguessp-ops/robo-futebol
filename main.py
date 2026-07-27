import os
import requests

# --- CHAVE OFICIAL DA API-FOOTBALL ---
API_KEY = "3b074d04sw3ac472ka26afd38dbeb3db"

# Cabeçalho corrigido para o padrão oficial da API-Football
HEADERS = {
    'x-apisports-key': API_KEY
}

def testar_conexao_oficial():
    print("\n--- TESTANDO CONEXÃO COM A API OFICIAL ---")
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"date": "2026-07-26", "league": 71, "season": 2026}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=15)
        print(f"Status HTTP: {response.status_code}")
        
        dados = response.json()
        
        # Exibe erros se houver
        if 'errors' in dados and dados['errors']:
            print(f"Erro retornado pela API: {dados['errors']}")
            return

        partidas = dados.get("response", [])
        print(f"Sucesso absoluto! Partidas encontradas: {len(partidas)}")
        
        for jogo in partidas:
            home = jogo['teams']['home']['name']
            away = jogo['teams']['away']['name']
            status = jogo['fixture']['status']['short']
            print(f"⚽ Jogo: {home} x {away} | Status: {status}")
            
            # Busca os eventos (gols)
            fid = jogo['fixture']['id']
            ev_resp = requests.get("https://v3.football.api-sports.io/fixtures/events", headers=HEADERS, params={"fixture": fid})
            eventos = ev_resp.json().get("response", [])
            gols = [e for e in eventos if e.get('type') == 'Goal']
            print(f"   -> Gols mapeados: {len(gols)}")
            for g in gols:
                print(f"      - Gol de {g['player']['name']} aos {g['time']['elapsed']}' ({g['team']['name']})")
                
    except Exception as e:
        print(f"Erro crítico: {e}")

if __name__ == "__main__":
    testar_conexao_oficial()
