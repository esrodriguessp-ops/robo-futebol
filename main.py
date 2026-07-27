import requests

# --- SUA CHAVE DIRETA ---
API_KEY = "3b074d04sw3ac472ka26afd38dbeb3db"

def testar_com_chave_na_url():
    print("\n--- TESTANDO CONEXÃO COM CHAVE NA URL ---")
    
    # Passando a chave direto no cabeçalho E como parâmetro na URL para garantir
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {
        'x-apisports-key': API_KEY
    }
    params = {
        "date": "2026-07-26", 
        "league": 71, 
        "season": 2026,
        "key": API_KEY  # Algumas instâncias da API oficial aceitam via query param
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        print(f"Status HTTP: {response.status_code}")
        
        dados = response.json()
        print("Resposta da API:", dados)
        
        partidas = dados.get("response", [])
        print(f"Partidas encontradas: {len(partidas)}")
        
        for jogo in partidas:
            home = jogo['teams']['home']['name']
            away = jogo['teams']['away']['name']
            status = jogo['fixture']['status']['short']
            print(f"⚽ Jogo: {home} x {away} | Status: {status}")
            
    except Exception as e:
        print(f"Erro crítico: {e}")

if __name__ == "__main__":
    testar_com_chave_na_url()
