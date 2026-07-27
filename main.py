import os
import requests

API_KEY = os.getenv("API_KEY", "3b074d04sw3ac472ka26afd38dbeb3db")
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

def diagnostico():
    print("\n--- DIAGNÓSTICO DE ACESSO DA API ---")
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"date": "2026-07-26"}
    
    response = requests.get(url, headers=HEADERS, params=params, timeout=15)
    print(f"Status HTTP: {response.status_code}")
    
    dados = response.json().get("response", [])
    print(f"Total de jogos no mundo encontrados para hoje: {len(dados)}")
    
    if len(dados) > 0:
        print("\nExemplos de ligas disponíveis na sua chave:")
        ligas_encontradas = set()
        for j in dados[:20]: # Mostra os primeiros 20
            l_id = j['league']['id']
            l_name = j['league']['name']
            country = j['league']['country']
            ligas_encontradas.add(f"ID {l_id}: {l_name} ({country})")
        
        for l in sorted(ligas_encontradas):
            print(f" - {l}")
    else:
        print("A API retornou zero jogos para hoje no mundo todo. O plano da API pode estar bloqueado ou expirado.")

if __name__ == "__main__":
    diagnostico()
