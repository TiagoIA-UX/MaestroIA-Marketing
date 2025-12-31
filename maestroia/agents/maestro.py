from maestroia.core.state import MaestroState
from maestroia.governance.approvals import verificar_aprovacao

def agente_maestro(state: MaestroState) -> MaestroState:
    """
    Agente orquestrador central: valida estado, chama governança e decide fluxos.
    """
    erros = state.get("erros", [])
    if erros:
        return {"maestro_status": f"Erros detectados: {erros}"}

    # Verificar aprovação humana se necessário
    if state.get("aprovacao_humana", False):
        aprovacao = verificar_aprovacao(state)
        if not aprovacao:
            return {"maestro_status": "Aguardando aprovação humana."}

    return {"maestro_status": "Orquestração concluída com sucesso."}
