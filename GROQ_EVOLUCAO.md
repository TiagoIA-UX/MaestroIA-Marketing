# Evolução do desempenho com Groq (sem treinar o modelo base)

Treinar o modelo da Groq diretamente não é possível dentro deste projeto, porque os modelos são gerenciados pela própria plataforma.

## O que é possível fazer (alto impacto)

1. **Prompting estruturado por tarefa**
   - Manter prompts separados por objetivo: pesquisa, estratégia, copy e otimização.
   - Forçar formato de saída (listas, JSON leve ou checklist).

2. **Avaliação contínua (evals)**
   - Criar um conjunto fixo de prompts reais.
   - Medir qualidade em critérios objetivos (clareza, conversão, aderência ao público).
   - Comparar versões de prompt e de modelo.

3. **RAG (memória de contexto)**
   - Injetar contexto da marca (tom de voz, ofertas, objeções, provas).
   - Reduzir respostas genéricas com base de conhecimento própria.

4. **Roteamento de modelo por etapa**
   - Modelo rápido para rascunho.
   - Modelo mais robusto para peça final (copy/estratégia).

5. **Guardrails de saída**
   - Validação automática de estrutura mínima de copy (headline, promessa, CTA, próximos passos).

## Variáveis já suportadas no projeto

- `LLM_PROVIDER=openai|groq`
- `GROQ_API_KEY`
- `GROQ_BASE_URL`
- `DEFAULT_LLM_MODEL`
- `DEFAULT_TEMPERATURE`

## Exemplo de configuração para Groq

```env
LLM_PROVIDER=groq
GROQ_API_KEY=seu_token_groq
GROQ_BASE_URL=https://api.groq.com/openai/v1
DEFAULT_LLM_MODEL=llama-3.3-70b-versatile
DEFAULT_TEMPERATURE=0.3
```

## Próximo passo recomendado

Implementar um pipeline de **evals semanais** com 20 prompts reais do seu negócio para evoluir qualidade de forma mensurável.

## Runner já disponível no projeto

Use o script:

```bash
python scripts/run_weekly_evals.py --offline
```

Modo com grafo real:

```bash
python scripts/run_weekly_evals.py --provider groq
```

Com limite de cenários:

```bash
python scripts/run_weekly_evals.py --limit 2 --offline
```

Saídas geradas em:

- `logs/evals/eval_report_YYYYMMDD_HHMMSS.json`
- `logs/evals/latest_summary.json`
