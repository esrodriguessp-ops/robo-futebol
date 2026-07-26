import time
import requests

# --- CONFIGURAÇÕES DO TELEGRAM ---
TOKEN_BOT = "8833822861:AAGnUGKAYuzsw75RBycjyVq1buJU--HGwsE"
CHAT_ID = "8979157542"

# --- CONFIGURAÇÕES DA API DE FUTEBOL (API-FOOTBALL) ---
API_FUTEBOL_KEY = "3b974d04ae3ac4721a26afd38dbeb2db"
URL_API = "https://v3.football.api-sports.io/fixtures?live=all"

HEADERS = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-apisports-key": API_FUTEBOL_KEY,
}

LIGAS_PERMITIDAS = []


def enviar_alerta_telegram(mensagem):
  url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
  payload = {
      "chat_id": CHAT_ID,
      "text": mensagem,
      "parse_mode": "Markdown",
  }

  try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
      print(
          "[SUCESSO] Alerta com estatísticas de cantos e cartões enviado para o"
          " Telegram!"
      )
      return True
    else:
      print(f"[ERRO] Falha no Telegram. Código do erro: {response.status_code}")
      return False
  except Exception as e:
    print(f"[ERRO] Erro de conexão no Telegram: {e}")
    return False


def descobrir_favorito_pre_live(fixture_id):
  """Busca as odds de PRÉ-LIVE (início do jogo) para definir quem é o favorito real."""
  url_pre_live_odds = (
      f"https://v3.football.api-sports.io/odds?fixture={fixture_id}&bookmaker=6"
  )
  try:
    resp = requests.get(url_pre_live_odds, headers=HEADERS)
    dados = resp.json()

    if "response" in dados and len(dados["response"]) > 0:
      bookmakers = dados["response"][0]["bookmakers"]
      odd_home = 999.0
      odd_away = 999.0

      for bm in bookmakers:
        for bet in bm["bets"]:
          if bet["id"] == 1:  # Mercado Match Winner (1X2)
            for val in bet["values"]:
              if val["value"] == "Home":
                odd_home = float(val["odd"])
              elif val["value"] == "Away":
                odd_away = float(val["odd"])

      if odd_home < odd_away:
        return "home"
      elif odd_away < odd_home:
        return "away"
  except Exception as e:
    print(f"[ERRO Pré-live Odds] {e}")

  return "desconhecido"


def obter_dados_partida_ao_vivo(fixture_id, favorito_alvo):
  """Busca a odd atual de Dupla Chance, escanteios e cartões da partida."""
  url_odds = (
      f"https://v3.football.api-sports.io/odds/live?fixture={fixture_id}"
  )
  url_stats = (
      f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
  )

  odd_dupla_escolhida = 0.0
  cantos_home, cantos_away = 0, 0
  cartoes_home, cartoes_away = 0, 0

  try:
    # 1. Busca a Odd de Dupla Chance Ao Vivo
    resp_odds = requests.get(url_odds, headers=HEADERS)
    dados_odds = resp_odds.json()

    if "response" in dados_odds and len(dados_odds["response"]) > 0:
      bookmakers = dados_odds["response"][0]["bookmakers"]
      for bm in bookmakers:
        for bet in bm["bets"]:
          if (
              "Double Chance" in bet.get("name", "")
              or bet.get("id") == 12
          ):
            for val in bet["values"]:
              nome_mercado = val["value"]
              cotacao = float(val["odd"])

              if favorito_alvo == "home" and nome_mercado in [
                  "Home/Draw",
                  "1X",
              ]:
                odd_dupla_escolhida = cotacao
              elif favorito_alvo == "away" and nome_mercado in [
                  "Away/Draw",
                  "X2",
              ]:
                odd_dupla_escolhida = cotacao

    # 2. Busca as Estatísticas ao Vivo (Cantos e Cartões)
    resp_stats = requests.get(url_stats, headers=HEADERS)
    dados_stats = resp_stats.json()

    if "response" in dados_stats and len(dados_stats["response"]) >= 2:
      for i, time_stats in enumerate(dados_stats["response"]):
        c_cantos = 0
        c_cartoes = 0

        for stat in time_stats["statistics"]:
          if stat["type"] == "Corner Kicks":
            val = stat["value"]
            c_cantos = int(val) if val is not None else 0
          elif stat["type"] == "Yellow Cards":
            val = stat["value"]
            c_cartoes = int(val) if val is not None else 0

        if i == 0:
          cantos_home = c_cantos
          cartoes_home = c_cartoes
        else:
          cantos_away = c_cantos
          cartoes_away = c_cartoes

  except Exception:
    pass

  return odd_dupla_escolhida, cantos_home, cantos_away, cartoes_home, cartoes_away


def monitorar_jogos_ao_vivo():
  print("==================================================")
  print("  ROBÔ DE OPORTUNIDADES - FAVORITO PRÉ-LIVE       ")
  print("==================================================")
  print("Monitorando placar, pressão, cantos e cartões...\n")

  historico_placar = {}
  jogos_alertados = set()
  favoritos_cache = {}

  while True:
    try:
      response = requests.get(URL_API, headers=HEADERS)
      dados = response.json()

      if "response" not in dados:
        print("[AVISO] Resposta da API fora do padrão. Tentando novamente...")
        time.sleep(60)
        continue

      partidas = dados["response"]

      for partida in partidas:
        jogo_id = partida["fixture"]["id"]
        status_long = partida["fixture"]["status"]["short"]
        liga_id = partida["league"]["id"]
        nome_liga = partida["league"]["name"]

        if status_long not in ["1H", "2H"]:
          continue

        if LIGAS_PERMITIDAS and liga_id not in LIGAS_PERMITIDAS:
          continue

        home_team = partida["teams"]["home"]["name"]
        away_team = partida["teams"]["away"]["name"]

        g_home = partida["goals"]["home"]
        g_away = partida["goals"]["away"]

        if g_home is None:
          g_home = 0
        if g_away is None:
          g_away = 0

        minuto = partida["fixture"]["status"]["elapsed"]
        if minuto is None:
          minuto = 0

        if minuto < 10 or minuto > 82:
          if jogo_id not in historico_placar:
            historico_placar[jogo_id] = {"home": g_home, "away": g_away}
          continue

        if jogo_id not in favoritos_cache:
          favoritos_cache[jogo_id] = descobrir_favorito_pre_live(jogo_id)

        favorito = favoritos_cache[jogo_id]

        if jogo_id in historico_placar:
          placar_antigo = historico_placar[jogo_id]
          antigo_home = placar_antigo["home"]
          antigo_away = placar_antigo["away"]

          if antigo_home != g_home or antigo_away != g_away:

            favorito_esta_perdendo = False
            favorito_esta_empatando = False
            cenario_texto = ""

            if favorito == "home":
              if g_home < g_away:
                favorito_esta_perdendo = True
                cenario_texto = (
                    f"O favorito pré-live mandante ({home_team}) está"
                    " perdendo!"
                )
              elif g_home == g_away:
                favorito_esta_empatando = True
                cenario_texto = (
                    f"O favorito pré-live mandante ({home_team}) sofreu o"
                    " empate!"
                )
            elif favorito == "away":
              if g_away < g_home:
                favorito_esta_perdendo = True
                cenario_texto = (
                    f"O favorito pré-live visitante ({away_team}) está"
                    " perdendo!"
                )
              elif g_home == g_away:
                favorito_esta_empatando = True
                cenario_texto = (
                    f"O favorito pré-live visitante ({away_team}) sofreu o"
                    " empate!"
                )

            if favorito_esta_perdendo or favorito_esta_empatando:

              if jogo_id in jogos_alertados:
                historico_placar[jogo_id] = {"home": g_home, "away": g_away}
                continue

              odd_dupla, c_home, c_away, cart_home, cart_away = (
                  obter_dados_partida_ao_vivo(jogo_id, favorito)
              )

              if favorito == "home":
                home_formatado = f"🔵 *{home_team}* (Favorito Pré-Live)"
                away_formatado = f"🔴 {away_team} (Defendendo)"
              elif favorito == "away":
                home_formatado = f"🔴 {home_team} (Defendendo)"
                away_formatado = f"🔵 *{away_team}* (Favorito Pré-Live)"
              else:
                home_formatado = f"{home_team}"
                away_formatado = f"{away_team}"

              link_jogo = "https://www.betano.com/live/futebol/"

              mensagem = (
                  f"🛡️ *ALERTA DE PRESSÃO E OPORTUNIDADE* 🛡️\n\n"
                  f"🏆 *Liga:* {nome_liga}\n"
                  f"⚽ *Partida:* {home_formatado} vs {away_formatado}\n"
                  f"⏱ *Tempo:* {minuto}º minuto\n"
                  f"📊 *Placar Atual:* {g_home} x {g_away}\n"
                  f"🚩 *Escanteios:* {c_home} (Mandante) x {c_away}"
                  f" (Visitante)\n"
                  f"🟨 *Cartões Amarelos:* {cart_home} x {cart_away}\n"
                  f"📈 *Odd Dupla Chance (Favorito):* `{odd_dupla}`\n"
                  f"🔥 *Cenário:* {cenario_texto}\n\n"
                  f"👉 *Acessar Jogos Ao Vivo na Betano:*\n{link_jogo}"
              )

              print(
                  f"[ENVIANDO TELEGRAM] {home_team} vs {away_team} aos"
                  f" {minuto}'"
              )
              enviar_alerta_telegram(mensagem)

              jogos_alertados.add(jogo_id)
              time.sleep(10)

        historico_placar[jogo_id] = {"home": g_home, "away": g_away}

    except Exception as e:
      print(f"[ERRO NO LOOP] {e}")

    time.sleep(60)


if __name__ == "__main__":
  monitorar_jogos_ao_vivo()
