"""
Curated Multi-Asset Catalog and Discovery Directory for the
Financial Market Regime Detection System.
Provides structured metadata, typeahead search formatting, and cheat-sheet dataframes
across Cryptocurrencies, Global Equities, Commodities, and Major Market Indices.
"""

from typing import List, Dict, Any, Optional
import pandas as pd

ASSET_CATALOG: List[Dict[str, str]] = [
    # ==========================================
    # 1. CRYPTOCURRENCIES
    # ==========================================
    {"symbol": "BTC", "name_en": "Bitcoin", "name_es": "Bitcoin", "category_en": "Cryptocurrency", "category_es": "Criptomoneda", "badge": "🪙"},
    {"symbol": "ETH", "name_en": "Ethereum", "name_es": "Ethereum", "category_en": "Cryptocurrency", "category_es": "Criptomoneda", "badge": "🪙"},
    {"symbol": "SOL", "name_en": "Solana", "name_es": "Solana", "category_en": "Cryptocurrency", "category_es": "Criptomoneda", "badge": "🪙"},
    {"symbol": "BNB", "name_en": "Binance Coin", "name_es": "Binance Coin", "category_en": "Cryptocurrency", "category_es": "Criptomoneda", "badge": "🪙"},
    {"symbol": "XRP", "name_en": "Ripple", "name_es": "Ripple", "category_en": "Cryptocurrency", "category_es": "Criptomoneda", "badge": "🪙"},
    {"symbol": "ADA", "name_en": "Cardano", "name_es": "Cardano", "category_en": "Cryptocurrency", "category_es": "Criptomoneda", "badge": "🪙"},
    {"symbol": "DOGE", "name_en": "Dogecoin", "name_es": "Dogecoin", "category_en": "Cryptocurrency", "category_es": "Criptomoneda", "badge": "🪙"},
    {"symbol": "AVAX", "name_en": "Avalanche", "name_es": "Avalanche", "category_en": "Cryptocurrency", "category_es": "Criptomoneda", "badge": "🪙"},
    {"symbol": "LINK", "name_en": "Chainlink", "name_es": "Chainlink", "category_en": "Cryptocurrency", "category_es": "Criptomoneda", "badge": "🪙"},
    {"symbol": "DOT", "name_en": "Polkadot", "name_es": "Polkadot", "category_en": "Cryptocurrency", "category_es": "Criptomoneda", "badge": "🪙"},
    {"symbol": "MATIC", "name_en": "Polygon", "name_es": "Polygon", "category_en": "Cryptocurrency", "category_es": "Criptomoneda", "badge": "🪙"},
    {"symbol": "SUI", "name_en": "Sui Network", "name_es": "Red Sui", "category_en": "Cryptocurrency", "category_es": "Criptomoneda", "badge": "🪙"},
    {"symbol": "NEAR", "name_en": "Near Protocol", "name_es": "Protocolo Near", "category_en": "Cryptocurrency", "category_es": "Criptomoneda", "badge": "🪙"},
    {"symbol": "LTC", "name_en": "Litecoin", "name_es": "Litecoin", "category_en": "Cryptocurrency", "category_es": "Criptomoneda", "badge": "🪙"},

    # ==========================================
    # 2. GLOBAL EQUITIES / TECH GIANTS
    # ==========================================
    {"symbol": "NVDA", "name_en": "NVIDIA Corporation", "name_es": "Corporación NVIDIA", "category_en": "Global Equities", "category_es": "Acciones Globales", "badge": "🏢"},
    {"symbol": "AAPL", "name_en": "Apple Inc.", "name_es": "Apple Inc.", "category_en": "Global Equities", "category_es": "Acciones Globales", "badge": "🏢"},
    {"symbol": "MSFT", "name_en": "Microsoft Corporation", "name_es": "Corporación Microsoft", "category_en": "Global Equities", "category_es": "Acciones Globales", "badge": "🏢"},
    {"symbol": "GOOGL", "name_en": "Alphabet Inc. (Google)", "name_es": "Alphabet Inc. (Google)", "category_en": "Global Equities", "category_es": "Acciones Globales", "badge": "🏢"},
    {"symbol": "AMZN", "name_en": "Amazon.com Inc.", "name_es": "Amazon.com Inc.", "category_en": "Global Equities", "category_es": "Acciones Globales", "badge": "🏢"},
    {"symbol": "TSLA", "name_en": "Tesla Inc.", "name_es": "Tesla Inc.", "category_en": "Global Equities", "category_es": "Acciones Globales", "badge": "🏢"},
    {"symbol": "META", "name_en": "Meta Platforms Inc.", "name_es": "Meta Platforms Inc.", "category_en": "Global Equities", "category_es": "Acciones Globales", "badge": "🏢"},
    {"symbol": "TSM", "name_en": "Taiwan Semiconductor (TSMC)", "name_es": "Taiwan Semiconductor (TSMC)", "category_en": "Global Equities", "category_es": "Acciones Globales", "badge": "🏢"},
    {"symbol": "BRK-B", "name_en": "Berkshire Hathaway Inc.", "name_es": "Berkshire Hathaway Inc.", "category_en": "Global Equities", "category_es": "Acciones Globales", "badge": "🏢"},
    {"symbol": "AVGO", "name_en": "Broadcom Inc.", "name_es": "Broadcom Inc.", "category_en": "Global Equities", "category_es": "Acciones Globales", "badge": "🏢"},
    {"symbol": "AMD", "name_en": "Advanced Micro Devices", "name_es": "Advanced Micro Devices", "category_en": "Global Equities", "category_es": "Acciones Globales", "badge": "🏢"},
    {"symbol": "ASML", "name_en": "ASML Holding N.V.", "name_es": "ASML Holding N.V.", "category_en": "Global Equities", "category_es": "Acciones Globales", "badge": "🏢"},
    {"symbol": "NFLX", "name_en": "Netflix Inc.", "name_es": "Netflix Inc.", "category_en": "Global Equities", "category_es": "Acciones Globales", "badge": "🏢"},
    {"symbol": "JPM", "name_en": "JPMorgan Chase & Co.", "name_es": "JPMorgan Chase & Co.", "category_en": "Global Equities", "category_es": "Acciones Globales", "badge": "🏢"},
    {"symbol": "V", "name_en": "Visa Inc.", "name_es": "Visa Inc.", "category_en": "Global Equities", "category_es": "Acciones Globales", "badge": "🏢"},

    # ==========================================
    # 3. COMMODITIES & METALS
    # ==========================================
    {"symbol": "GC=F", "name_en": "Gold Futures", "name_es": "Futuros de Oro", "category_en": "Commodities", "category_es": "Materias Primas", "badge": "🥇"},
    {"symbol": "GLD", "name_en": "SPDR Gold Shares ETF", "name_es": "ETF SPDR Gold Shares", "category_en": "Commodities", "category_es": "Materias Primas", "badge": "🥇"},
    {"symbol": "SI=F", "name_en": "Silver Futures", "name_es": "Futuros de Plata", "category_en": "Commodities", "category_es": "Materias Primas", "badge": "🥈"},
    {"symbol": "SLV", "name_en": "iShares Silver Trust ETF", "name_es": "ETF iShares Silver Trust", "category_en": "Commodities", "category_es": "Materias Primas", "badge": "🥈"},
    {"symbol": "CL=F", "name_en": "Crude Oil (WTI) Futures", "name_es": "Futuros de Petróleo Crudo (WTI)", "category_en": "Commodities", "category_es": "Materias Primas", "badge": "🛢️"},
    {"symbol": "BZ=F", "name_en": "Brent Crude Oil Futures", "name_es": "Futuros de Petróleo Brent", "category_en": "Commodities", "category_es": "Materias Primas", "badge": "🛢️"},
    {"symbol": "NG=F", "name_en": "Natural Gas Futures", "name_es": "Futuros de Gas Natural", "category_en": "Commodities", "category_es": "Materias Primas", "badge": "🔥"},
    {"symbol": "HG=F", "name_en": "Copper Futures", "name_es": "Futuros de Cobre", "category_en": "Commodities", "category_es": "Materias Primas", "badge": "🧱"},
    {"symbol": "PL=F", "name_en": "Platinum Futures", "name_es": "Futuros de Platino", "category_en": "Commodities", "category_es": "Materias Primas", "badge": "🪙"},
    {"symbol": "C=F", "name_en": "Corn Futures", "name_es": "Futuros de Maíz", "category_en": "Commodities", "category_es": "Materias Primas", "badge": "🌽"},

    # ==========================================
    # 4. MARKET INDICES & BENCHMARK ETFS
    # ==========================================
    {"symbol": "^GSPC", "name_en": "S&P 500 Index", "name_es": "Índice S&P 500", "category_en": "Indices & ETFs", "category_es": "Índices y ETFs", "badge": "📊"},
    {"symbol": "^NDX", "name_en": "Nasdaq 100 Index", "name_es": "Índice Nasdaq 100", "category_en": "Indices & ETFs", "category_es": "Índices y ETFs", "badge": "📊"},
    {"symbol": "^DJI", "name_en": "Dow Jones Industrial Average", "name_es": "Promedio Industrial Dow Jones", "category_en": "Indices & ETFs", "category_es": "Índices y ETFs", "badge": "📊"},
    {"symbol": "^RUT", "name_en": "Russell 2000 Index", "name_es": "Índice Russell 2000", "category_en": "Indices & ETFs", "category_es": "Índices y ETFs", "badge": "📊"},
    {"symbol": "^VIX", "name_en": "CBOE Volatility Index", "name_es": "Índice de Volatilidad CBOE (VIX)", "category_en": "Indices & ETFs", "category_es": "Índices y ETFs", "badge": "⚡"},
    {"symbol": "SPY", "name_en": "SPDR S&P 500 ETF Trust", "name_es": "ETF SPDR S&P 500", "category_en": "Indices & ETFs", "category_es": "Índices y ETFs", "badge": "📊"},
    {"symbol": "QQQ", "name_en": "Invesco QQQ (Nasdaq 100 ETF)", "name_es": "ETF Invesco QQQ (Nasdaq 100)", "category_en": "Indices & ETFs", "category_es": "Índices y ETFs", "badge": "📊"},
    {"symbol": "IBIT", "name_en": "iShares Bitcoin Trust ETF", "name_es": "ETF iShares Bitcoin Trust", "category_en": "Indices & ETFs", "category_es": "Índices y ETFs", "badge": "🪙"},
    {"symbol": "SMH", "name_en": "VanEck Semiconductor ETF", "name_es": "ETF VanEck Semiconductores", "category_en": "Indices & ETFs", "category_es": "Índices y ETFs", "badge": "💻"},
    {"symbol": "TLT", "name_en": "iShares 20+ Year Treasury Bond ETF", "name_es": "ETF Bonos del Tesoro 20+ Años", "category_en": "Indices & ETFs", "category_es": "Índices y ETFs", "badge": "🏛️"}
]

CUSTOM_OPTION_EN = "🔍 Custom Ticker (Enter any Yahoo Finance symbol)..."
CUSTOM_OPTION_ES = "🔍 Ticker Personalizado (Ingresa cualquier símbolo)..."


def get_search_options(lang: str = "en") -> List[str]:
    """
    Return formatted search strings for typeahead selectbox.
    Example: '🪙 BTC - Bitcoin (Cryptocurrency)'
    """
    options = []
    is_es = (lang == "es")
    for item in ASSET_CATALOG:
        name = item["name_es"] if is_es else item["name_en"]
        cat = item["category_es"] if is_es else item["category_en"]
        badge = item.get("badge", "📌")
        options.append(f"{badge} {item['symbol']} — {name} ({cat})")
    
    # Add custom symbol entry at the end
    options.append(CUSTOM_OPTION_ES if is_es else CUSTOM_OPTION_EN)
    return options


def extract_symbol_from_choice(choice: str) -> Optional[str]:
    """
    Extract pure symbol from the selectbox option string.
    Returns None if the user selected custom entry.
    """
    if choice in (CUSTOM_OPTION_EN, CUSTOM_OPTION_ES):
        return None
    try:
        # Format is '{badge} {symbol} — {name} ({cat})'
        symbol_part = choice.split("—")[0].strip()
        # Remove any leading emoji
        symbol = symbol_part.split()[-1].strip()
        return symbol
    except Exception:
        return choice.strip()


def get_directory_dataframe(lang: str = "en") -> pd.DataFrame:
    """Return a clean pandas DataFrame for the cheat sheet directory."""
    is_es = (lang == "es")
    records = []
    for item in ASSET_CATALOG:
        records.append({
            "Icon": item.get("badge", "📌"),
            "Symbol": item["symbol"],
            "Asset Name": item["name_es"] if is_es else item["name_en"],
            "Category": item["category_es"] if is_es else item["category_en"]
        })
    df = pd.DataFrame(records)
    if is_es:
        df = df.rename(columns={
            "Icon": "Ícono",
            "Symbol": "Símbolo (Ticker)",
            "Asset Name": "Nombre del Activo",
            "Category": "Categoría"
        })
    return df
