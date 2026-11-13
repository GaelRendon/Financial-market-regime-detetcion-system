"""
Internationalization (i18n) translation dictionary and helpers for the
Financial Market Regime Detection System.
Provides 0-latency, 0-cost, deterministic translations for English and Spanish.
"""

from typing import Dict, Any

SUPPORTED_LANGUAGES = {
    "en": "EN (English)",
    "es": "ES (Español)"
}

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # ==========================================
    # SIDEBAR
    # ==========================================
    "sidebar_language": {
        "en": "🌐 Language",
        "es": "🌐 Idioma"
    },
    "sidebar_title": {
        "en": "⚙️ Asset & Horizon",
        "es": "⚙️ Activo y Horizonte"
    },
    "sidebar_subtitle": {
        "en": "Configure target financial asset and denomination fiat:",
        "es": "Configura el activo financiero y la divisa fiat de denominación:"
    },
    "asset_class_label": {
        "en": "Asset Class",
        "es": "Clase de Activo"
    },
    "asset_class_crypto": {
        "en": "🪙 Cryptocurrencies",
        "es": "🪙 Criptomonedas"
    },
    "asset_class_stocks": {
        "en": "🏢 Global Stocks / Equities",
        "es": "🏢 Acciones Globales"
    },
    "asset_class_commodities": {
        "en": "🥇 Commodities & Metals",
        "es": "🥇 Materias Primas y Metales"
    },
    "asset_class_indices": {
        "en": "📊 Market Indices & ETFs",
        "es": "📊 Índices de Mercado y ETFs"
    },
    "asset_class_custom": {
        "en": "🔍 Custom Symbol (Any Ticker)",
        "es": "🔍 Símbolo Personalizado (Cualquier Ticker)"
    },
    "select_crypto": {
        "en": "Cryptocurrency",
        "es": "Criptomoneda"
    },
    "select_stock": {
        "en": "Stock / Company",
        "es": "Acción / Empresa"
    },
    "select_commodity": {
        "en": "Commodity",
        "es": "Materia Prima"
    },
    "select_index": {
        "en": "Market Index",
        "es": "Índice de Mercado"
    },
    "custom_ticker_label": {
        "en": "Enter Any Yahoo Finance Symbol (e.g. NVDA, GC=F, TSM, BABA)",
        "es": "Ingresa cualquier símbolo de Yahoo Finance (ej. NVDA, GC=F, TSM, BABA)"
    },
    "fiat_currency_label": {
        "en": "Fiat Currency",
        "es": "Divisa Fiat"
    },
    "lookback_window_label": {
        "en": "Historical Lookback Window",
        "es": "Ventana Histórica de Análisis"
    },
    "horizon_1y": {
        "en": "1 Year",
        "es": "1 Año"
    },
    "horizon_2y": {
        "en": "2 Years",
        "es": "2 Años"
    },
    "horizon_3y": {
        "en": "3 Years",
        "es": "3 Años"
    },
    "horizon_5y": {
        "en": "5 Years",
        "es": "5 Años"
    },
    "horizon_max": {
        "en": "Maximum Available",
        "es": "Máximo Disponible"
    },
    "about_model_title": {
        "en": "ℹ️ About the Model",
        "es": "ℹ️ Acerca del Modelo"
    },
    "about_model_caption": {
        "en": "This system applies **Rolling Z-Score Normalization (252-day window)** to contextualize Returns, 30d Volatility, and 14d Momentum relative to recent market conditions — not all-time history. **PCA (95% variance)** then reduces these into orthogonal components, **K-Means (K=4)** partitions market states, **Markov Chains** model regime persistence, and **Random Forest** forecasts the next regime.",
        "es": "Este sistema aplica **Normalización Z-Score Móvil (ventana de 252 días)** para contextualizar Retornos, Volatilidad a 30d y Momento a 14d respecto a condiciones recientes del mercado — no de toda la historia. Luego, **PCA (95% de varianza)** reduce estas variables a componentes ortogonales, **K-Means (K=4)** particiona los estados del mercado, las **Cadenas de Markov** modelan la persistencia y un **Random Forest** pronostica el siguiente régimen."
    },
    "run_button": {
        "en": "🚀 Run Live Analysis",
        "es": "🚀 Ejecutar Análisis en Vivo"
    },
    "spinner_fetching": {
        "en": "Fetching market data for {ticker} and executing quantitative pipeline...",
        "es": "Descargando datos de mercado para {ticker} y ejecutando pipeline cuantitativo..."
    },

    # ==========================================
    # APP HEADER
    # ==========================================
    "main_header": {
        "en": "📈 Financial Market Regime Detection System",
        "es": "📈 Sistema de Detección de Regímenes de Mercado Financiero"
    },
    "sub_header": {
        "en": "Live quantitative regime identification, probabilistic forecasting, and automated risk allocation for <b>{ticker}</b>",
        "es": "Identificación cuantitativa de regímenes en vivo, pronóstico probabilístico y asignación automatizada de riesgo para <b>{ticker}</b>"
    },

    # ==========================================
    # MAIN TABS
    # ==========================================
    "tab_analysis": {
        "en": "📊 Live Market Regime Analysis",
        "es": "📊 Análisis de Régimen en Vivo"
    },
    "tab_simulator": {
        "en": "🔮 7-Day Money Growth Simulator (Optional)",
        "es": "🔮 Simulador de Crecimiento de Capital a 7 Días (Opcional)"
    },

    # ==========================================
    # TOP METRICS
    # ==========================================
    "metric_current_price": {
        "en": "Current Price ({fiat})",
        "es": "Precio Actual ({fiat})"
    },
    "metric_current_price_help": {
        "en": "Last updated closing price denominated in {fiat}.",
        "es": "Último precio de cierre actualizado denominado en {fiat}."
    },
    "metric_current_regime": {
        "en": "Current Regime",
        "es": "Régimen Actual"
    },
    "metric_current_regime_help": {
        "en": "Active Market Regime: {regime}.",
        "es": "Régimen de Mercado Activo: {regime}."
    },
    "metric_persistence": {
        "en": "Regime Persistence",
        "es": "Persistencia de Régimen"
    },
    "metric_persistence_help": {
        "en": "Consecutive days the market has stayed within this regime.",
        "es": "Días consecutivos que el mercado ha permanecido dentro de este régimen."
    },
    "days_suffix": {
        "en": "days",
        "es": "días"
    },
    "metric_volatility": {
        "en": "30-Day Volatility",
        "es": "Volatilidad a 30 Días"
    },
    "metric_momentum": {
        "en": "14-Day Momentum",
        "es": "Momento a 14 Días"
    },

    # ==========================================
    # FORECAST & RECOMMENDATION BANNER
    # ==========================================
    "forecast_heading": {
        "en": "Tomorrow's Forecasted Regime:",
        "es": "Régimen Pronosticado para Mañana:"
    },
    "suggestion_heading": {
        "en": "🎯 SUGGESTION:",
        "es": "🎯 SUGERENCIA:"
    },
    "exposure_suffix": {
        "en": "{pct}% Exposure",
        "es": "{pct}% de Exposición"
    },
    "risk_level_label": {
        "en": "Risk Level:",
        "es": "Nivel de Riesgo:"
    },
    "chart_forecast_confidence_title": {
        "en": "Forecast Confidence Distribution ({ticker})",
        "es": "Distribución de Confianza del Pronóstico ({ticker})"
    },
    "chart_probability_axis": {
        "en": "Probability (%)",
        "es": "Probabilidad (%)"
    },

    # ==========================================
    # HISTORICAL TIMELINE
    # ==========================================
    "timeline_section_title": {
        "en": "### 📊 Historical Market Regime Timeline",
        "es": "### 📊 Línea de Tiempo Histórica de Regímenes"
    },
    "timeline_chart_title": {
        "en": "{ticker} Daily Price History with Detected Regimes",
        "es": "Historial de Precios Diarios de {ticker} con Regímenes Detectados"
    },
    "timeline_chart_date": {
        "en": "Date",
        "es": "Fecha"
    },
    "timeline_chart_price": {
        "en": "Price ({fiat})",
        "es": "Precio ({fiat})"
    },
    "timeline_close_price": {
        "en": "Close Price",
        "es": "Precio de Cierre"
    },

    # ==========================================
    # FEATURE DECOMPOSITION
    # ==========================================
    "features_section_title": {
        "en": "### 🔍 Engineered Feature Dynamics",
        "es": "### 🔍 Dinámica de Variables de Características"
    },
    "features_tab_returns": {
        "en": "Daily Returns",
        "es": "Retornos Diarios"
    },
    "features_tab_volatility": {
        "en": "30-Day Volatility",
        "es": "Volatilidad a 30d"
    },
    "features_tab_momentum": {
        "en": "14-Day Momentum",
        "es": "Momento a 14d"
    },
    "features_chart_return_axis": {
        "en": "Daily Return (%)",
        "es": "Retorno Diario (%)"
    },
    "features_chart_vol_axis": {
        "en": "Volatility (%)",
        "es": "Volatilidad (%)"
    },
    "features_chart_mom_axis": {
        "en": "Momentum (%)",
        "es": "Momento (%)"
    },

    # ==========================================
    # MARKOV TRANSITIONS
    # ==========================================
    "markov_section_title": {
        "en": "### 🔄 Markov Regime Transition Dynamics",
        "es": "### 🔄 Dinámica de Transición de Regímenes de Markov"
    },
    "markov_heatmap_title": {
        "en": "Historical 1-Day Transition Probabilities (%)",
        "es": "Probabilidades Históricas de Transición a 1 Día (%)"
    },
    "markov_next_day_axis": {
        "en": "Next Day Regime (t+1)",
        "es": "Régimen del Siguiente Día (t+1)"
    },
    "markov_current_day_axis": {
        "en": "Current Regime (t)",
        "es": "Régimen Actual (t)"
    },
    "markov_persistence_title": {
        "en": "#### Regime Persistence",
        "es": "#### Persistencia del Régimen"
    },
    "markov_expected_holding": {
        "en": "<b>Expected Holding Duration:</b>",
        "es": "<b>Duración Esperada de Mantenimiento:</b>"
    },
    "markov_caption": {
        "en": "Expected duration indicates how many consecutive days the market typically remains inside that state before shifting.",
        "es": "La duración esperada indica cuántos días consecutivos suele permanecer el mercado dentro de ese estado antes de cambiar."
    },
    "table_col_regime": {
        "en": "Regime",
        "es": "Régimen"
    },
    "table_col_self_prob": {
        "en": "Self-Transition Prob",
        "es": "Prob. de Auto-Transición"
    },
    "table_col_exp_duration": {
        "en": "Expected Duration",
        "es": "Duración Esperada"
    },

    # ==========================================
    # POWER BI / EXCEL EXPORT
    # ==========================================
    "export_section_title": {
        "en": "### 📥 Export Dataset for Power BI / Excel",
        "es": "### 📥 Exportar Dataset para Power BI / Excel"
    },
    "export_description": {
        "en": "You can export this analyzed dataset directly into a standardized CSV file ready to connect into **Power BI**, **Excel**, or SQL databases:",
        "es": "Puedes exportar este conjunto de datos analizado directamente a un archivo CSV estandarizado listo para conectar en **Power BI**, **Excel** o bases de datos SQL:"
    },
    "export_button": {
        "en": "💾 Download {ticker} Regime Dataset (CSV for Power BI)",
        "es": "💾 Descargar Dataset de Regímenes de {ticker} (CSV para Power BI)"
    },

    # ==========================================
    # TAB 2: 7-DAY MONEY GROWTH SIMULATOR
    # ==========================================
    "sim_title": {
        "en": "### 🔮 7-Day Forward Capital Growth Simulator",
        "es": "### 🔮 Simulador de Proyección de Capital a 7 Días"
    },
    "sim_description": {
        "en": "This optional simulator projects how an investment in **{coin}** (denominated in **{fiat}**) could behave over the next 7 days based on our machine learning regime forecast, empirical Markov chain transitions, and 1,000 Monte Carlo statistical simulation paths.",
        "es": "Este simulador opcional proyecta cómo una inversión en **{coin}** (denominada en **{fiat}**) podría comportarse durante los próximos 7 días con base en el pronóstico de regímenes de machine learning, transiciones empíricas de cadenas de Markov y 1,000 trayectorias estadísticas de Monte Carlo."
    },
    "sim_disclaimer_title": {
        "en": "⚠️ IMPORTANT DISCLAIMER: It's a prediction, not a statement — take your own risk.",
        "es": "⚠️ DESCARGO DE RESPONSABILIDAD: Es una predicción, no una afirmación — asume tu propio riesgo."
    },
    "sim_disclaimer_body": {
        "en": "Cryptocurrency and financial markets are inherently volatile, speculative, and subject to unexpected external macroeconomic events. This simulation represents a <b>probabilistic statistical model</b> conditioned on historical regime dynamics. <b>It does NOT represent a factual statement, guaranteed performance, or professional financial advice.</b> Any capital you invest carries risk of partial or total loss. Always exercise independent diligence and strictly manage your downside risk.",
        "es": "Los mercados cripto y financieros son inherentemente volátiles, especulativos y están sujetos a eventos macroeconómicos inesperados. Esta simulación representa un <b>modelo estadístico probabilístico</b> condicionado a la dinámica histórica de regímenes. <b>NO representa una afirmación fáctica, rendimiento garantizado ni asesoramiento financiero profesional.</b> Cualquier capital invertido conlleva riesgo de pérdida parcial o total. Realiza siempre tu debida diligencia de forma independiente y gestiona estrictamente tu riesgo a la baja."
    },
    "sim_input_capital": {
        "en": "Enter hypothetical investment amount in {fiat} ({symbol}):",
        "es": "Ingresa el monto hipotético de inversión en {fiat} ({symbol}):"
    },
    "sim_button": {
        "en": "🚀 Calculate 7-Day Money Projection",
        "es": "🚀 Calcular Proyección a 7 Días"
    },
    "sim_starting_capital": {
        "en": "Starting Capital",
        "es": "Capital Inicial"
    },
    "sim_expected_capital": {
        "en": "Expected Capital (Day 7)",
        "es": "Capital Esperado (Día 7)"
    },
    "sim_projected_pnl": {
        "en": "Projected Net P&L",
        "es": "Ganancia / Pérdida Neta Proyectada"
    },
    "sim_confidence_corridor": {
        "en": "90% Confidence Corridor",
        "es": "Corredor de Confianza al 90%"
    },
    "sim_confidence_corridor_help": {
        "en": "Range spanning the 10th percentile (defensive adverse scenario) to 90th percentile (optimistic bullish scenario).",
        "es": "Rango que abarca desde el percentil 10 (escenario adverso defensivo) hasta el percentil 90 (escenario alcista optimista)."
    },
    "sim_chart_title": {
        "en": "7-Day Forward Money Growth Simulation for {symbol}{capital:,.2f} in {ticker}",
        "es": "Simulación de Crecimiento de Capital a 7 Días para {symbol}{capital:,.2f} en {ticker}"
    },
    "sim_chart_date_axis": {
        "en": "Forecast Horizon Date",
        "es": "Fecha del Horizonte"
    },
    "sim_chart_balance_axis": {
        "en": "Projected Balance ({fiat})",
        "es": "Saldo Proyectado ({fiat})"
    },
    "sim_legend_80ci": {
        "en": "80% Confidence Interval (10th–90th Pct)",
        "es": "Intervalo de Confianza del 80% (Perc. 10–90)"
    },
    "sim_legend_50ci": {
        "en": "50% Core Interquartile Range (25th–75th Pct)",
        "es": "Rango Intercuartílico Central del 50% (Perc. 25–75)"
    },
    "sim_legend_mean": {
        "en": "Expected Balance (Mean)",
        "es": "Saldo Esperado (Promedio)"
    },
    "sim_legend_median": {
        "en": "Median Balance (50th Pct)",
        "es": "Saldo Mediano (Percentil 50)"
    },
    "sim_initial_baseline": {
        "en": "Initial Capital ({symbol}{capital:,.2f})",
        "es": "Capital Inicial ({symbol}{capital:,.2f})"
    },
    "sim_table_title": {
        "en": "#### 📅 Day-by-Day Forecast Summary Table",
        "es": "#### 📅 Tabla Resumen del Pronóstico Día por Día"
    },
    "sim_download_button": {
        "en": "💾 Download 7-Day Projection Report ({fiat})",
        "es": "💾 Descargar Reporte de Proyección a 7 Días ({fiat})"
    },

    # Simulator Table Column Headers
    "col_day": {"en": "Day", "es": "Día"},
    "col_date": {"en": "Date", "es": "Fecha"},
    "col_pred_regime": {"en": "Predicted_Regime", "es": "Régimen_Pronosticado"},
    "col_confidence": {"en": "Confidence (%)", "es": "Confianza (%)"},
    "col_daily_ret": {"en": "Exp. Daily Return (%)", "es": "Retorno Diario Esp. (%)"},
    "col_proj_cap": {"en": "Projected Capital", "es": "Capital Proyectado"},
    "col_lower_10": {"en": "Lower Bound (10th)", "es": "Límite Inferior (10%)"},
    "col_upper_90": {"en": "Upper Bound (90th)", "es": "Límite Superior (90%)"},
    "col_cum_pnl": {"en": "Cumulative P&L", "es": "Ganancia Acumulada"},
    "col_cum_ret": {"en": "Cumulative Return (%)", "es": "Retorno Acumulado (%)"}
}

# ==========================================
# REGIME & ACTION POLICIES TRANSLATIONS
# ==========================================
REGIME_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "Moderate-Volatility Bullish": {
        "en": "Moderate-Volatility Bullish",
        "es": "Alcista de Moderada Volatilidad"
    },
    "Low-Volatility Neutral": {
        "en": "Low-Volatility Neutral",
        "es": "Neutral de Baja Volatilidad"
    },
    "High-Volatility Transition": {
        "en": "High-Volatility Transition",
        "es": "Transición de Alta Volatilidad"
    },
    "High-Volatility Bearish": {
        "en": "High-Volatility Bearish",
        "es": "Bajista de Alta Volatilidad"
    }
}

ACTION_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "BUY / OVERWEIGHT": {
        "en": "BUY / OVERWEIGHT",
        "es": "COMPRAR / SOBREPONDERAR"
    },
    "HOLD / ACCUMULATE": {
        "en": "HOLD / ACCUMULATE",
        "es": "MANTENER / ACUMULAR"
    },
    "REDUCE EXPOSURE / DEFENSIVE": {
        "en": "REDUCE EXPOSURE / DEFENSIVE",
        "es": "REDUCIR EXPOSICIÓN / DEFENSIVO"
    },
    "SELL / CASH (FLAT)": {
        "en": "SELL / CASH (FLAT)",
        "es": "VENDER / LIQUIDEZ (EFECTIVO)"
    }
}

RISK_LEVEL_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "Moderate Risk / High Upside": {
        "en": "Moderate Risk / High Upside",
        "es": "Riesgo Moderado / Alto Potencial"
    },
    "Low Risk / Stable": {
        "en": "Low Risk / Stable",
        "es": "Bajo Riesgo / Estable"
    },
    "Elevated Risk / Regime Shift": {
        "en": "Elevated Risk / Regime Shift",
        "es": "Riesgo Elevado / Cambio de Régimen"
    },
    "Severe Capital Destruction Risk": {
        "en": "Severe Capital Destruction Risk",
        "es": "Riesgo Severo de Destrucción de Capital"
    }
}

RATIONALE_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "Moderate-Volatility Bullish": {
        "en": "Market displays strong positive momentum with controlled volatility. Historical data supports full market exposure to capture appreciation.",
        "es": "El mercado muestra un fuerte momento positivo con volatilidad controlada. Los datos históricos respaldan una exposición total al mercado para capturar la apreciación."
    },
    "Low-Volatility Neutral": {
        "en": "Market is in an orderly consolidation or low-volatility phase. Downside variance is subdued; maintaining full market position is recommended.",
        "es": "El mercado se encuentra en una consolidación ordenada o fase de baja volatilidad. La varianza a la baja está contenida; se recomienda mantener la posición completa en el mercado."
    },
    "High-Volatility Transition": {
        "en": "Volatility is surging with unstable momentum. Downside tail-risk is elevated. De-risking to 50% exposure and 50% cash preserves capital.",
        "es": "La volatilidad está repuntando con momento inestable. El riesgo de cola a la baja es elevado. Reducir el riesgo al 50% de exposición y 50% en efectivo preserva el capital."
    },
    "High-Volatility Bearish": {
        "en": "Severe downward momentum coupled with extreme volatility. The model strongly advises moving 100% to cash to protect capital against severe drawdowns.",
        "es": "Momento bajista severo junto con volatilidad extrema. El modelo aconseja enfáticamente pasar el 100% a efectivo para proteger el capital contra caídas pronunciadas."
    }
}


def t(key: str, lang: str = "en", **kwargs) -> str:
    """Retrieve translated string with optional formatting."""
    lang_code = lang if lang in SUPPORTED_LANGUAGES else "en"
    text = TRANSLATIONS.get(key, {}).get(lang_code, TRANSLATIONS.get(key, {}).get("en", key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


def translate_regime(regime_name: str, lang: str = "en") -> str:
    """Translate market regime label to target language."""
    lang_code = lang if lang in SUPPORTED_LANGUAGES else "en"
    return REGIME_TRANSLATIONS.get(regime_name, {}).get(lang_code, regime_name)


def translate_action(action_name: str, lang: str = "en") -> str:
    """Translate recommendation action label to target language."""
    lang_code = lang if lang in SUPPORTED_LANGUAGES else "en"
    return ACTION_TRANSLATIONS.get(action_name, {}).get(lang_code, action_name)


def translate_risk_level(risk_level: str, lang: str = "en") -> str:
    """Translate risk level description."""
    lang_code = lang if lang in SUPPORTED_LANGUAGES else "en"
    return RISK_LEVEL_TRANSLATIONS.get(risk_level, {}).get(lang_code, risk_level)


def translate_rationale(regime_name: str, lang: str = "en", default_text: str = "") -> str:
    """Translate strategy rationale for a given regime."""
    lang_code = lang if lang in SUPPORTED_LANGUAGES else "en"
    return RATIONALE_TRANSLATIONS.get(regime_name, {}).get(lang_code, default_text)
