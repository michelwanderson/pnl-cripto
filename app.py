from flask import Flask, render_template, request, redirect, url_for
import requests, json, os, time
from datetime import datetime

app = Flask(__name__)

DATA_DIR = "data"
ENTRIES_FILE = os.path.join(DATA_DIR, "entries.json")
PRICES_FILE = os.path.join(DATA_DIR, "prices.json")




# Configurações
SUPPORTED_COINS = ["BTC", "ETH"]
SUPPORTED_FIAT = ["BRL", "USD"]
FEE_RATE = 0.001  # 0,1% (aplicada sobre a quantidade em cripto)
PRICE_HISTORY_LIMIT = 100  # por par moeda+fiat

# Mapear símbolo -> id da CoinGecko
COIN_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
}

def last_update():
    now = datetime.now()
    hour_last_update = now.strftime("%H:%M")

    return hour_last_update


def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(ENTRIES_FILE):
        with open(ENTRIES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    if not os.path.exists(PRICES_FILE):
        with open(PRICES_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

def load_entries():
    ensure_data_files()
    with open(ENTRIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_entries(entries):
    with open(ENTRIES_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

def load_prices():
    ensure_data_files()
    with open(PRICES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_prices(prices):
    with open(PRICES_FILE, "w", encoding="utf-8") as f:
        json.dump(prices, f, ensure_ascii=False, indent=2)

def get_current_price(coin: str, fiat: str):
    coin_id = COIN_MAP.get(coin.upper())
    if coin_id is None:
        raise ValueError("Moeda não suportada")
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin_id, "vs_currencies": fiat.lower()}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    return float(data[coin_id][fiat.lower()])

def record_price_history(coin: str, fiat: str, price: float):
    prices = load_prices()
    key = f"{coin}_{fiat}"
    now = int(time.time())
    series = prices.get(key, [])
    series.append({"t": now, "p": price})
    if len(series) > PRICE_HISTORY_LIMIT:
        series = series[-PRICE_HISTORY_LIMIT:]
    prices[key] = series
    save_prices(prices)

def format_ts(ts: int):
    return datetime.fromtimestamp(ts).strftime("%H:%M")

def compute_metrics(entry, current_price):
    # Taxa aplicada sobre a quantidade (fee em cripto)
    gross_qty = entry["valor_compra"] / entry["preco_compra"]
    fee_qty = gross_qty * FEE_RATE
    qty = gross_qty - fee_qty

    # O valor atual é a quantidade líquida (qty) ao preço atual
    current_value = qty * current_price
    # PnL é a diferença entre o valor atual e o valor total da compra (investimento inicial)
    pnl = current_value - entry["valor_compra"]
    pnl_pct = (pnl / entry["valor_compra"]) * 100 if entry["valor_compra"] else 0.0

    if current_price is None:
        status = "na"
    else:
        if pnl_pct > 5:
            status = "green"
        elif pnl_pct < -2:
            status = "red"
        else:
            status = "yellow"

    return {
        "gross_qty": gross_qty,
        "fee_qty": fee_qty,
        "qty": qty,
        "invested": entry["valor_compra"],  # O valor investido é o total da compra
        "current_value": current_value,
        "pnl": pnl,
        "pnl_pct": pnl_pct,
        "status": status
    }

@app.context_processor
def utility_processor():
    # Torna a função acessível em todos os templates
    return dict(format_ts=format_ts)

@app.route("/", methods=["GET", "POST"])
def index():
    ensure_data_files()
    error = None
    api_error = None

    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            coin = request.form.get("coin", "BTC").upper()
            fiat = request.form.get("fiat", "BRL").upper()
            # Limpa a entrada para o padrão numérico (remove '.' de milhar, troca ',' decimal por '.')
            valor_compra_raw = request.form.get("valor_compra", "0")
            preco_compra_raw = request.form.get("preco_compra", "0")
            valor_compra = valor_compra_raw.replace(".", "").replace(",", ".")
            preco_compra = preco_compra_raw.replace(".", "").replace(",", ".")
            try:
                if coin not in SUPPORTED_COINS or fiat not in SUPPORTED_FIAT:
                    raise ValueError("Moeda ou fiat não suportada")
                valor_compra = float(valor_compra)
                preco_compra = float(preco_compra)
                if valor_compra <= 0 or preco_compra <= 0:
                    raise ValueError("Valores devem ser positivos")
                entries = load_entries()
                entry = {
                    "id": int(time.time() * 1000),
                    "coin": coin,
                    "fiat": fiat,
                    "valor_compra": valor_compra,
                    "preco_compra": preco_compra,
                    "ts": int(time.time())
                }
                entries.append(entry)
                save_entries(entries)
                return redirect(url_for("index"))
            except Exception as e:
                error = str(e)
        elif action == "delete":
            entry_id = request.form.get("id")
            try:
                entry_id = int(entry_id)
                entries = load_entries()
                entries = [e for e in entries if e["id"] != entry_id]
                save_entries(entries)
                return redirect(url_for("index"))
            except Exception as e:
                error = str(e)
        elif action == "refresh":
            return redirect(url_for("index"))

    # Carrega entradas
    entries = load_entries()

    # Otimização: Agrupa os pares únicos (coin, fiat) para evitar chamadas de API repetidas
    unique_pairs = {(e["coin"], e["fiat"]) for e in entries}
    current_prices = {}
    for coin, fiat in unique_pairs:
        try:
            price = get_current_price(coin, fiat)
            current_prices[(coin, fiat)] = price
            record_price_history(coin, fiat, price)
        except Exception:
            api_error = "Erro de API ao buscar preços"
            current_prices[(coin, fiat)] = None

    # Monta linhas
    rows = []
    for e in entries:
        # Reutiliza o preço já buscado
        current_price = current_prices.get((e["coin"], e["fiat"]))

        if current_price:
            metrics = compute_metrics(e, current_price)
        else:
            # Caso a busca de preço tenha falhado para este par
            metrics = {k: None for k in ["gross_qty", "fee_qty", "qty", "invested", "current_value", "pnl", "pnl_pct"]}
            metrics["status"] = "na"

        # Adiciona a linha com os dados processados
        rows.append({"entry": e, "current_price": current_price, "metrics": metrics})

    # Séries para gráficos
    prices_hist = load_prices()
    chart_series = {}
    for key, series in prices_hist.items():
        parts = key.split("_")
        if len(parts) == 2 and parts[0] in SUPPORTED_COINS and parts[1] in SUPPORTED_FIAT:
            chart_series[key] = {
                "labels": [format_ts(p["t"]) for p in series],
                "data": [p["p"] for p in series]
            }

    return render_template(
        "index.html",
        rows=rows,
        error=error,
        api_error=api_error,
        fee_rate=FEE_RATE * 100,
        chart_series=chart_series,
        supported_coins=SUPPORTED_COINS,
        supported_fiat=SUPPORTED_FIAT,
        last_update=last_update()
    )


@app.route("/refresh", methods=["POST"])
def refresh():
    # Nada além de redirecionar; o GET da index já chama a API e atualiza
    return redirect(url_for("index"))

@app.route("/health")
def health():
    return "OK", 200


    

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)