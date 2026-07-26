import time
import requests

TOKEN_BOT = "8833822861:AAGnUGKAYuzsw75RBycjyVq1buJU--HGwsE"
CHAT_ID = "8979157542"

API_FUTEBOL_KEY = "3b974d04ae3ac4721a26afd38dbeb2db"
URL_FIXTURES = "https://v3.football.api-sports.io/fixtures?live=all"

HEADERS = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-apisports-key": API_FUTEBOL_KEY,
}


def enviar_alerta_telegram(mensagem):
  url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
  payload = {
      "chat_id": CHAT_ID,
      "text": mensagem,
      "parse_mode": "Markdown",
  }
  try:
    requests.post(url, json=payload)
  except Exception as e:
    print(f"[ERRO Telegram]: {e}")


def executar_ciclo_futebol():
  try:
    print("[FUTEBOL] Verificando partidas ao vivo...")
    response = requests.get(URL_FIXTURES, headers=HEADERS)
    dados = response.json()
    if "response" in dados:
      partidas = dados["response"]
      print(f"[FUTEBOL] {len(partidas)} partidas ao vivo encontradas.")
  except Exception as e:
    print(f"[ERRO Futebol]: {e}")


def main():
  enviar_alerta_telegram(
      "✅ *TESTE DO ROBÔ FUTEBOL:* Sistema rodando com sucesso!"
  )
  print("==================================================")
  print("         ROBÔ DE FUTEBOL TRADICIONAL")
  print("==================================================")
  while True:
    print("\n--- Iniciando novo ciclo de verificações ---")
    executar_ciclo_futebol()
    print("[FUTEBOL] Ciclo concluído. Aguardando próximo ciclo...")
    time.sleep(300)


if __name__ == "__main__":
  main()
