import flet as ft
import requests
import pandas as pd
import numpy as np
import time
import threading
from datetime import datetime

TOP10_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "DOTUSDT"
]

def get_futures_klines(symbol, interval="15m", limit=100):
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        resp = requests.get(url, timeout=5)
        df = pd.DataFrame(resp.json(), columns=[
            'time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'
        ])
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        return df
    except Exception:
        return None

def main(page: ft.Page):
    page.title = "量化交易雷达 Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 15
    page.scroll = ft.ScrollMode.AUTO

    usdt_text = ft.Text("$10,000.00", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_400)
    status_text = ft.Text("系统正在监控 10 个主流永续合约...", size=12, color=ft.colors.GREY_400)

    header_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("模拟合约账户权益 (3X 杠杆)", size=12, color=ft.colors.GREY_400),
                usdt_text,
                status_text,
            ]),
            padding=15
        )
    )

    list_column = ft.Column(spacing=10)

    page.add(
        header_card,
        ft.Divider(),
        ft.Text("实时行情多空监控", size=16, weight=ft.FontWeight.BOLD),
        list_column
    )

    def monitor_loop():
        while True:
            cards = []
            for symbol in TOP10_SYMBOLS:
                df = get_futures_klines(symbol)
                if df is not None and len(df) >= 25:
                    latest_price = df['close'].iloc[-1]
                    ma7 = df['close'].rolling(7).mean().iloc[-1]
                    ma25 = df['close'].rolling(25).mean().iloc[-1]

                    if latest_price > ma25 and ma7 > ma25:
                        signal = "🟢 偏多/做多观望"
                        sig_color = ft.colors.GREEN_400
                    elif latest_price < ma25 and ma7 < ma25:
                        signal = "🔴 偏空/做空观望"
                        sig_color = ft.colors.RED_400
                    else:
                        signal = "⚪ 震荡观望"
                        sig_color = ft.colors.GREY_400

                    card = ft.Card(
                        content=ft.Container(
                            content=ft.Row([
                                ft.Column([
                                    ft.Text(symbol, size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"现价: ${latest_price:,.2f}", size=12, color=ft.colors.GREY_300),
                                ]),
                                ft.Text(signal, size=14, color=sig_color, weight=ft.FontWeight.BOLD)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            padding=12
                        )
                    )
                    cards.append(card)

            list_column.controls = cards
            status_text.value = f"最后刷新时间: {datetime.now().strftime('%H:%M:%S')}"
            page.update()
            time.sleep(15)

    threading.Thread(target=monitor_loop, daemon=True).start()

ft.app(target=main)

