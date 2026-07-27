import os
import requests

API_KEY = os.getenv("API_KEY", "3b074d04sw3ac472ka26afd38dbeb3db")

HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

def executar_backtest():
    print("\n==================================================")
    print("INICIANDO BACKTEST DOS JOGOS DO BRASILEIRÃO - HOJE")
    print("==================================================")
    
    # Busca todas as partidas do Brasileirão (League 71) para a data de hoje (2026-07-26)
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"date": "2026-07-26", "league": 71, "season": 2026}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=15)
        if response.status_code != 200:
            print(f"Erro na API: Status {response.status_code} - {response.text}")
            return
            
        dados = response.json().get("response", [])
        print(f"Total de partidas do Brasileirão encontradas hoje: {len(dados)}\n")
        
        if len(dados) == 0:
            print("A API retornou zero partidas para esta data/liga com esses parâmetros.")
            return

        for jogo in dados:
            fixture_id = jogo['fixture']['id']
            home_team = jogo['teams']['home']['name']
            away_team = jogo['teams']['away']['name']
            status = jogo['fixture']['status']['short']
            
            print(f"⚽ Jogo: {home_team} x {away_team} [Status: {status}] (ID: {fixture_id})")
            
            # Busca os eventos (gols) oficiais de cada partida
            url_events = "https://v3.football.api-sports.io/fixtures/events"
            resp_events = requests.get(url_events, headers=HEADERS, params={"fixture": fixture_id}, timeout=10)
            
            if resp_events.status_code == 200:
                eventos = resp_events.json().get("response", [])
                gols = [ev for ev in eventos if ev.get('type') == 'Goal' and ev.get('detail') in ['Normal Goal', 'Penalty', 'Own Goal']]
                
                if len(gols) == 0:
                    print("   -> Nenhum gol registrado ou eventos vazios para este jogo.\n")
                else:
                    for g in gols:
                        minuto = g['time']['elapsed']
                        jogador = g.get('player', {}).get('name', 'Desconhecido')
                        equipe = g.get('team', {}).get('name', '')
                        
                        # Valida se estaria dentro da nossa métrica (entre 10' e 82')
                        dentro_metrica = 10 <= minuto <= 82
                        status_sinal = "🚨 [SINAL GERADO]" if dentro_metrica else "❌ [Fora da métrica de tempo]"
                        
                        print(f"   {status_sinal} Gol de {jogador} ({equipe}) aos {minuto}'")
                    print("")
            else:
                print(f"   -> Erro ao buscar eventos: {resp_events.status_code}\n")
                
        print("==================================================")
        print("FIM DO BACKTEST")
        print("==================================================")
            
    except Exception as e:
        print(f"Erro crítico no backtest: {e}")

if __name__ == "__main__":
    executar_backtest()
