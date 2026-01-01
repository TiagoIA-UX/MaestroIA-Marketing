# Instruções para agentes Copilot — MaestroIA

Este arquivo orienta agentes de codificação (Copilot / AI pair programmers) a serem imediatamente produtivos neste repositório.

Breve objetivo: este projeto é uma plataforma de orquestração de agentes de marketing (Streamlit UI + API + grafo de agentes). As mudanças devem preservar a orquestração por grafo e as integrações LLM/API.

Principais pontos a entender rapidamente
- **Arquitetura**: orquestração via grafo em [maestroia/graphs/marketing_graph.py](maestroia/graphs/marketing_graph.py). Cada nó é um agente em [maestroia/agents/](maestroia/agents/).
- **Estado compartilhado**: `MaestroState` em [maestroia/core/state.py](maestroia/core/state.py) define o contrato de entrada/saída entre agentes. Sempre leia esse TypedDict antes de alterar nomes de chaves.
- **Entradas executáveis**: exemplos de execução local em [run.py](run.py) e [maestroia/main.py](maestroia/main.py). A API de produção usa [api_server.py](api_server.py) (uvicorn).

Ambiente e variáveis críticas
- Variáveis no [.env] esperadas em [maestroia/config/settings.py](maestroia/config/settings.py). **IMPORTANTE**: o módulo lança `RuntimeError` se `OPENAI_API_KEY` não estiver definido — para código offline use mocks ou ajuste `settings.py` durante testes.
- Dependências principais no `requirements.txt` (OpenAI/langchain/langgraph/streamlit/FAISS/etc.).

Workflows de desenvolvedor e comandos úteis
- Rodar UI local (Streamlit): `streamlit run ui_app.py` (veja [README.md](README.md)).
- Rodar API local: `python api_server.py` ou `uvicorn maestroia.api.routes:app --reload --port 8000`.
- Executar grafo de orquestração rápido: `python run.py` ou `python -m maestroia.main`.
- Testes unitários: executar `python -m unittest discover maestroia/tests`.

Padrões de implementação e convenções locais
- Agentes: cada arquivo em `maestroia/agents/` expõe uma função `agente_x(state: MaestroState) -> MaestroState` (ou dicionário parcial). Mantenha assinatura e evite efeitos colaterais globais.
- Tipos e chaves: use as chaves definidas em `MaestroState` para comunicação; novas saídas devem estar documentadas no TypedDict.
- LLM wrappers: alguns agentes usam wrappers diferentes (`langchain_openai.ChatOpenAI`, `HuggingFaceHubChat`). Ao modificar prompts, preserve contexto (ex.: `pesquisa`, `objetivo`, `publico_alvo`).
- Fail-safe e modo simulado: agentes frequentemente fazem fallback (simulações) quando APIs externas falham — preserve esses caminhos para devs sem chaves.

Integrações externas e pontos sensíveis
- OpenAI / LLMs: configurado em [maestroia/config/settings.py](maestroia/config/settings.py). Não comitar chaves; prefira mocks em CI e testes locais.
- Google Trends / SEMrush / Mercado Pago: comportamentos simulados presentes em `maestroia/agents/*`. Se integrar de fato, crie abstração em `maestroia/services/` e documente credenciais no `.env.example`.

Exemplos práticos (quando editar/introduzir código)
- Quer adicionar um nó ao grafo? 1) criar `maestroia/agents/novo_agente.py` com `agente_novo(state)`; 2) adicionar `graph.add_node("novo_agente", agente_novo)` e arestar `graph.add_edge(...)` em [maestroia/graphs/marketing_graph.py](maestroia/graphs/marketing_graph.py); 3) atualizar `MaestroState` se sair novas chaves; 4) adicionar teste unitário em `maestroia/tests/`.
- Corrigir bug em agente: modifique apenas a função do agente; mantenha as chaves do estado e garanta que retornos sejam serializáveis (dict/TypedDict).

O que evitar
- Não alterar arbitrariamente as chaves de `MaestroState` sem atualizar todos consumidores no grafo e testes.
- Não inserir chamadas síncronas bloqueantes de I/O pesadas diretamente nos agentes sem explicitar comportamento assíncrono ou timeouts.

Arquivos de referência imediata
- [README.md](README.md) — visão geral e comandos de setup
- [maestroia/graphs/marketing_graph.py](maestroia/graphs/marketing_graph.py) — orquestração
- [maestroia/core/state.py](maestroia/core/state.py) — contrato de estado
- [maestroia/config/settings.py](maestroia/config/settings.py) — variáveis de ambiente críticas
- [run.py](run.py), [api_server.py](api_server.py), [ui_app.py](ui_app.py) — formas de executar

Seções não cobertas (peça ao mantenedor)
- Políticas de deploy/CI (não encontrei workflows GitHub Actions nesse repositório)
- Endpoints reais de redes sociais em produção (atualmente simulados)

Feedback
Se algo neste rascunho estiver incompleto ou você quer que eu inclua exemplos de prompts/trechos de código, diga quais áreas priorizar (ex.: LLM prompt patterns, testes isolados, ou integração Mercado Pago). 
