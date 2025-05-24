from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import pandas_ta as ta
import requests

app = FastAPI()

# CORS liberado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnaliseRequest(BaseModel):
    symbol: str
    interval: str


@app.get("/")
def read_root():
    return {"message": "API Criptoeasy rodando com dados reais da Binance."}


@app.post("/analisar")
def analisar_dados(request: AnaliseRequest):
    try:
        # Endpoint da Binance para pegar dados de candles
        url = f"https://api.binance.com/api/v3/klines?symbol={request.symbol}&interval={request.interval}&limit=100"

        # Adicionando headers para evitar bloqueio
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        if response.status_code != 200:
            return {"error": f"Erro ao buscar dados da Binance. Status code: {response.status_code}"}

        data = response.json()

        # Preparando o dataframe
        df = pd.DataFrame(data, columns=[
            "Open time", "Open", "High", "Low", "Close", "Volume",
            "Close time", "Quote asset volume", "Number of trades",
            "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"
        ])

        df["Close"] = df["Close"].astype(float)

        # Calculando indicadores
        df["RSI"] = ta.rsi(df["Close"])
        df["EMA20"] = ta.ema(df["Close"], length=20)
        df["EMA50"] = ta.ema(df["Close"], length=50)

        rsi = round(df["RSI"].iloc[-1], 2) if not pd.isna(df["RSI"].iloc[-1]) else "Indisponível"
        ema20 = round(df["EMA20"].iloc[-1], 2) if not pd.isna(df["EMA20"].iloc[-1]) else "Indisponível"
        ema50 = round(df["EMA50"].iloc[-1], 2) if not pd.isna(df["EMA50"].iloc[-1]) else "Indisponível"
        preco_atual = df["Close"].iloc[-1]

        # Definindo a tendência
        if ema20 > ema50:
            tendencia = "Tendência de Alta"
        elif ema20 < ema50:
            tendencia = "Tendência de Baixa"
        else:
            tendencia = "Indefinida"

        return {
            "Tendência": tendencia,
            "Preço Atual": preco_atual,
            "RSI": rsi,
            "EMA20": ema20,
            "EMA50": ema50
        }
    except Exception as e:
        return {"error": str(e)}
