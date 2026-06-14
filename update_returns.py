#!/usr/bin/env python3
"""
update_returns.py
Calcula el rendimiento anualizado (CAGR) a 1, 3, 5 y 10 años de cada fondo
usando precios AJUSTADOS (reinvierte dividendos y capital gains) y captura el
nombre oficial del fondo. Escribe fund_returns.json para la calculadora.

CORRER EN UN MAC (no en Render: yfinance da 429 desde IPs de Render).
Luego subir solo fund_returns.json:

    python3 update_returns.py
    git add fund_returns.json && git commit -m "update returns" && git push origin main
"""

import json
import time
from datetime import datetime, timezone

import yfinance as yf
from dateutil.relativedelta import relativedelta

# ── Edita esta lista con tus fondos ───────────────────────────────────────────
FUNDS = ["FELAX", "FKDNX", "VADAX", "FOCPX", "FNIAX"]

PERIODS = [1, 3, 5, 10]
OUTPUT = "fund_returns.json"
MAX_RETRIES = 4
RETRY_BACKOFF = 3
# ──────────────────────────────────────────────────────────────────────────────


def fetch_history(ticker):
    """Descarga ~11 años de precios ajustados con reintentos."""
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            df = yf.download(ticker, period="11y", auto_adjust=True,
                             progress=False, threads=False)
            if df is not None and not df.empty:
                if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
                    df.columns = df.columns.get_level_values(0)
                return df
            last_err = "respuesta vacía"
        except Exception as e:
            last_err = str(e)
        wait = RETRY_BACKOFF * attempt
        print(f"  reintento {attempt}/{MAX_RETRIES} ({last_err}) — espero {wait}s")
        time.sleep(wait)
    raise RuntimeError(f"no se pudo descargar {ticker}: {last_err}")


def fetch_name(ticker):
    """Nombre oficial del fondo desde yfinance (longName preferido)."""
    try:
        info = yf.Ticker(ticker).info
        return info.get("longName") or info.get("shortName") or ticker
    except Exception:
        return ticker


def cagr(df, years):
    """CAGR geométrico sobre precio ajustado para la ventana de N años."""
    end_date = df.index[-1]
    target = end_date - relativedelta(years=years)
    window = df.loc[:target]
    if window.empty:
        return None
    start_date = window.index[-1]
    start_p = float(df.loc[start_date, "Close"])
    end_p = float(df.iloc[-1]["Close"])
    real_years = (end_date - start_date).days / 365.25
    if start_p <= 0 or real_years <= 0:
        return None
    return round(((end_p / start_p) ** (1 / real_years) - 1) * 100, 2)


def main():
    results = {}
    for ticker in FUNDS:
        print(f"{ticker} …")
        try:
            df = fetch_history(ticker)
            name = fetch_name(ticker)
            returns = {f"{y}y": cagr(df, y) for y in PERIODS}
            results[ticker] = {
                "name": name,
                "returns": returns,
                "price": round(float(df.iloc[-1]["Close"]), 2),
                "last_data": df.index[-1].strftime("%Y-%m-%d"),
            }
            shown = "  ".join(f"{k}={v}%" if v is not None else f"{k}=n/a"
                              for k, v in returns.items())
            print(f"  ✓ {name}")
            print(f"    {shown}")
        except Exception as e:
            print(f"  ✗ {e}")
            results[ticker] = {"error": str(e)}

    payload = {
        "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "source": "yfinance (adjusted close, CAGR)",
        "funds": results,
    }
    with open(OUTPUT, "w") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    ok = len([f for f in results.values() if "error" not in f])
    print(f"\nEscrito {OUTPUT} ({ok}/{len(FUNDS)} ok)")


if __name__ == "__main__":
    main()
