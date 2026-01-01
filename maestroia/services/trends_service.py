from typing import List

def get_trends_summary(keywords: List[str], timeframe: str = "today 12-m", geo: str = "") -> str:
    """Tenta buscar dados do Google Trends via pytrends; em falha retorna summary simulado.

    Retorna um texto resumido pronto para inserção em prompts.
    """
    try:
        from pytrends.request import TrendReq

        pytrends = TrendReq()
        pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo, gprop='')
        trends_data = pytrends.interest_over_time()
        if trends_data is None or trends_data.empty:
            raise RuntimeError("Dados do Google Trends vazios")

        latest = trends_data.iloc[-1] if len(trends_data) > 0 else trends_data.iloc[0]
        previous = trends_data.iloc[-2] if len(trends_data) > 1 else latest

        parts = []
        for kw in keywords:
            try:
                cur = latest.get(kw, None)
                prev = previous.get(kw, cur)
                if cur is None:
                    parts.append(f"'{kw}': sem dados recentes")
                    continue
                change = ((cur - prev) / prev * 100) if prev and prev != 0 else 0
                parts.append(f"'{kw}': interesse {cur}/100, variação {change:.1f}%")
            except Exception:
                parts.append(f"'{kw}': erro ao processar dados")

        return "Dados do Google Trends: " + "; ".join(parts)
    except Exception as e:
        return f"Dados simulados do Google Trends: interesse crescente em {', '.join(keywords)} (fallback). Erro: {e}"
