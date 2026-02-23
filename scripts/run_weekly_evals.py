"""Runner de avaliação contínua dos agentes MaestroIA.

Exemplos:
  python scripts/run_weekly_evals.py --offline
  python scripts/run_weekly_evals.py --limit 2
  python scripts/run_weekly_evals.py --scenarios maestroia/evals/scenarios.json
"""

from __future__ import annotations

import argparse
import json
import statistics
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIOS_PATH = ROOT / "maestroia" / "evals" / "scenarios.json"
EVAL_LOG_DIR = ROOT / "logs" / "evals"


@dataclass
class AgentScores:
    pesquisador: float
    estrategista: float
    criador_conteudo: float
    publicador: float
    otimizador: float
    maestro: float

    @property
    def overall(self) -> float:
        values = [
            self.pesquisador,
            self.estrategista,
            self.criador_conteudo,
            self.publicador,
            self.otimizador,
            self.maestro,
        ]
        return round(sum(values) / len(values), 2)


def _safe_text_len(value: Any) -> int:
    if value is None:
        return 0
    return len(str(value).strip())


def _count_keywords(text: str, keywords: list[str]) -> int:
    text_lower = text.lower()
    return sum(1 for keyword in keywords if keyword.lower() in text_lower)


def _score_text_block(text: str, min_len: int, keywords: list[str]) -> float:
    length = _safe_text_len(text)
    length_score = min(1.0, length / max(1, min_len))

    if not keywords:
        keyword_score = 1.0
    else:
        hits = _count_keywords(text or "", keywords)
        keyword_score = hits / len(keywords)

    score = (length_score * 0.6) + (keyword_score * 0.4)
    return round(min(1.0, max(0.0, score)) * 100, 2)


def _score_criador(conteudos: Any, canais: list[str]) -> float:
    if not isinstance(conteudos, list) or not conteudos:
        return 0.0

    joined = "\n".join(str(item) for item in conteudos)
    base = _score_text_block(
        joined,
        min_len=300,
        keywords=["cta", "oferta", "benefício", "convers"],
    )

    canais_score = min(1.0, len(conteudos) / max(1, min(len(canais), 3))) * 100
    return round((base * 0.8) + (canais_score * 0.2), 2)


def _score_publicador(publicacoes: Any, canais: list[str]) -> float:
    if not isinstance(publicacoes, dict) or not publicacoes:
        return 0.0

    coverage = 0.0
    if canais:
        covered = sum(1 for canal in canais if canal in publicacoes)
        coverage = covered / len(canais)
    else:
        coverage = 1.0

    non_empty = sum(1 for value in publicacoes.values() if _safe_text_len(value) > 15)
    non_empty_ratio = non_empty / max(1, len(publicacoes))

    return round(((coverage * 0.65) + (non_empty_ratio * 0.35)) * 100, 2)


def _score_otimizador(metricas: Any, otimizacao: Any) -> float:
    metric_score = 0.0
    if isinstance(metricas, dict):
        required = ["cliques", "conversoes", "roi"]
        found = sum(1 for key in required if key in metricas)
        metric_score = found / len(required)

    text_score = _score_text_block(str(otimizacao or ""), min_len=120, keywords=["teste", "melhoria", "ctr", "convers"]) / 100
    return round(((metric_score * 0.55) + (text_score * 0.45)) * 100, 2)


def _score_maestro(maestro_status: Any, erros: Any) -> float:
    if erros:
        return 20.0
    text = str(maestro_status or "").lower()
    if "sucesso" in text:
        return 100.0
    if "aguardando" in text:
        return 70.0
    if _safe_text_len(text) >= 20:
        return 60.0
    return 35.0


def evaluate_result(result: dict[str, Any], scenario: dict[str, Any]) -> AgentScores:
    pesquisa = str(result.get("pesquisa", ""))
    estrategia = str(result.get("estrategia", ""))
    conteudos = result.get("conteudos", [])
    publicacoes = result.get("publicacoes", {})
    metricas = result.get("metricas", {})
    otimizacao = result.get("otimizacao", "")
    maestro_status = result.get("maestro_status", "")
    erros = result.get("erros", [])

    pesquisador_score = _score_text_block(
        pesquisa,
        min_len=250,
        keywords=["tend", "oportun", "risco", "concorr"],
    )
    estrategista_score = _score_text_block(
        estrategia,
        min_len=280,
        keywords=["posicion", "mensagem", "canal", "kpi"],
    )
    criador_score = _score_criador(conteudos, scenario.get("canais", []))
    publicador_score = _score_publicador(publicacoes, scenario.get("canais", []))
    otimizador_score = _score_otimizador(metricas, otimizacao)
    maestro_score = _score_maestro(maestro_status, erros)

    return AgentScores(
        pesquisador=pesquisador_score,
        estrategista=estrategista_score,
        criador_conteudo=criador_score,
        publicador=publicador_score,
        otimizador=otimizador_score,
        maestro=maestro_score,
    )


def load_scenarios(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("Arquivo de cenários inválido: esperado array JSON")
    return data


def run_graph_once(payload: dict[str, Any]) -> dict[str, Any]:
    from maestroia.graphs.marketing_graph import build_marketing_graph

    graph = build_marketing_graph()
    return graph.invoke(payload)


def run_offline_once(payload: dict[str, Any]) -> dict[str, Any]:
    canais = payload.get("canais", [])
    publicacoes = {canal: f"Publicação simulada para {canal} pronta para revisão" for canal in canais}
    conteudos = [
        f"{canal}: Headline com promessa clara, benefícios, prova e CTA para {payload.get('objetivo', '')}."
        for canal in canais
    ]
    return {
        "pesquisa": "Tendências em alta com crescimento de demanda, oportunidades por nicho e riscos competitivos mapeados.",
        "estrategia": "Posicionamento definido, mensagem central por canal e KPIs de CAC, CTR e conversão.",
        "conteudos": conteudos,
        "publicacoes": publicacoes,
        "metricas": {"cliques": 120, "conversoes": 11, "roi": 2.1},
        "otimizacao": "Rodar testes A/B de headline e CTA, ajustar segmentação e frequência para elevar CTR e conversões.",
        "maestro_status": "Orquestração concluída com sucesso.",
        "erros": [],
    }


def persist_report(report: dict[str, Any]) -> Path:
    EVAL_LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_path = EVAL_LOG_DIR / f"eval_report_{timestamp}.json"

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    latest_path = EVAL_LOG_DIR / "latest_summary.json"
    with latest_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    return report_path


def print_summary(report: dict[str, Any]) -> None:
    print("\n=== Resultado dos Evals Semanais ===")
    print(f"Provider: {report['provider']} | Modo offline: {report['offline']}")
    print(f"Cenários avaliados: {report['scenario_count']} | Score geral: {report['overall_score']}")
    print("\nScore médio por agente:")
    for agent, score in report["agent_averages"].items():
        print(f"- {agent}: {score}")

    print("\nPor cenário:")
    for item in report["scenarios"]:
        print(f"- {item['id']}: {item['overall']} (erros={item['error_count']})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Runner de evals semanais do MaestroIA")
    parser.add_argument("--scenarios", type=str, default=str(DEFAULT_SCENARIOS_PATH))
    parser.add_argument("--limit", type=int, default=0, help="Limita o número de cenários avaliados")
    parser.add_argument("--offline", action="store_true", help="Executa simulação local sem chamar o grafo")
    parser.add_argument("--provider", type=str, default="auto", help="Rótulo do provider para o relatório")
    args = parser.parse_args()

    scenarios = load_scenarios(Path(args.scenarios))
    if args.limit and args.limit > 0:
        scenarios = scenarios[: args.limit]

    if not scenarios:
        raise SystemExit("Nenhum cenário para avaliar.")

    scenario_reports: list[dict[str, Any]] = []

    for scenario in scenarios:
        payload = {
            "objetivo": scenario.get("objetivo", "Gerar demanda"),
            "publico_alvo": scenario.get("publico_alvo", "Público geral"),
            "canais": scenario.get("canais", ["Instagram"]),
            "orcamento": scenario.get("orcamento", 0),
        }

        try:
            result = run_offline_once(payload) if args.offline else run_graph_once(payload)
        except Exception as error:
            result = {"erros": [str(error)], "maestro_status": "Execução com falha"}

        scores = evaluate_result(result, scenario)
        error_count = len(result.get("erros", []) or [])

        scenario_reports.append(
            {
                "id": scenario.get("id", "scenario_sem_id"),
                "overall": scores.overall,
                "error_count": error_count,
                "agent_scores": {
                    "pesquisador": scores.pesquisador,
                    "estrategista": scores.estrategista,
                    "criador_conteudo": scores.criador_conteudo,
                    "publicador": scores.publicador,
                    "otimizador": scores.otimizador,
                    "maestro": scores.maestro,
                },
            }
        )

    def _avg(agent_key: str) -> float:
        return round(
            statistics.mean(item["agent_scores"][agent_key] for item in scenario_reports),
            2,
        )

    report = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider": args.provider,
        "offline": args.offline,
        "scenario_count": len(scenario_reports),
        "overall_score": round(statistics.mean(item["overall"] for item in scenario_reports), 2),
        "agent_averages": {
            "pesquisador": _avg("pesquisador"),
            "estrategista": _avg("estrategista"),
            "criador_conteudo": _avg("criador_conteudo"),
            "publicador": _avg("publicador"),
            "otimizador": _avg("otimizador"),
            "maestro": _avg("maestro"),
        },
        "scenarios": scenario_reports,
    }

    output_path = persist_report(report)
    print_summary(report)
    print(f"\nRelatório salvo em: {output_path}")


if __name__ == "__main__":
    main()
