from typing import TypedDict, Optional, List


class MaestroState(TypedDict, total=False):
    """
    Estado global compartilhado entre os agentes do MaestroIA Marketing.
    Cada chave representa uma informação produzida ou consumida por agentes.
    """

    # =========================
    # CONTEXTO INICIAL
    # =========================
    objetivo: str
    publico_alvo: str
    canais: List[str]
    orcamento: Optional[float]

    # =========================
    # SAÍDAS DOS AGENTES
    # =========================
    pesquisa: str
    estrategia: str
    conteudos: List[str]
    publicacoes: List[str]
    metricas: dict

    # =========================
    # CONTROLE E GOVERNANÇA
    # =========================
    aprovacao_humana: bool
    erros: List[str]
