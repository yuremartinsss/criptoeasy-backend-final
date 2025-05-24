from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import pandas_ta as ta
from numpy import nan as npNaN

app = FastAPI()

class AnaliseRequest(BaseModel):
    symbol: str
    interval: str

@app.get("/")
def read_root():
    return {"message": "API Criptoeasy rodando perfeitamente."}

@app.post("/analisar")
def analisar_dados(request: AnaliseRequest):
    df = pd.DataFrame({
        "close": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
    })

    df["rsi"] = ta.rsi(df["close"])
    rsi = df["rsi"].iloc[-1]

    tendencia = "Alta" if rsi > 50 else "Baixa"

    return {
        "Tendência": tendencia,
        "RSI": round(rsi, 2) if not pd.isna(rsi) else "Indisponível",
        "Preço Simulado": df["close"].iloc[-1]
    }