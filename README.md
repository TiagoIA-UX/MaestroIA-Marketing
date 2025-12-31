# MaestroIA

Plataforma SaaS para orquestração de agentes de IA em marketing digital.

## Visão Geral

O **MaestroIA** é uma plataforma inovadora que permite a profissionais de marketing criar e gerenciar equipes autônomas de agentes de IA. Inspirado na reportagem do Fantástico sobre a "profissão do futuro" (orquestrar agentes de IA), o sistema executa campanhas de marketing digital completas de ponta a ponta, desde pesquisa de mercado até otimização de resultados.

O usuário define o objetivo da campanha (ex.: "Lançar produto X para público feminino 25-40 anos no Instagram e Google Ads"), e os agentes trabalham em colaboração: pesquisam tendências, criam estratégias, produzem conteúdos, publicam e otimizam — tudo com comunicação interna e supervisão humana opcional.

## Funcionalidades Principais

- **Agentes Autônomos**: 6 agentes especializados (Pesquisador, Estrategista, Criador de Conteúdo, Publicador, Otimizador, Maestro).
- **Orquestração Inteligente**: Fluxo coordenado com LangGraph, garantindo consistência e eficiência.
- **Integrações**: APIs para OpenAI, simulações para Google Ads/Meta (expansível).
- **Interfaces Múltiplas**: Terminal, API REST (FastAPI) e UI Web (Streamlit).
- **Memória Vetorial**: FAISS para aprendizado contínuo de campanhas.
- **Governança**: Aprovações humanas e regras de segurança.

## Arquitetura

```
maestroia/
├─ agents/          # Agentes especializados
├─ api/             # Endpoints REST com FastAPI
├─ config/          # Configurações e settings
├─ core/            # Estado compartilhado e governança
├─ governance/      # Regras e aprovações
├─ graphs/          # Grafos de orquestração (LangGraph)
├─ memory/          # Armazenamento vetorial (FAISS)
├─ services/        # Lógica de campanhas e usuários
├─ tests/           # Testes unitários
├─ tools/           # Ferramentas auxiliares (busca, anúncios)
├─ ui/              # Interface Streamlit
├─ main.py          # Ponto de entrada principal
├─ run.py           # Script de execução
├─ api_server.py   # Servidor da API
├─ ui_app.py        # App Streamlit
├─ requirements.txt
├─ .env.example
└─ README.md
```

## Tecnologias

- **Python 3.14+**: Compatível com versões recentes.
- **LangGraph**: Orquestração de agentes.
- **OpenAI GPT-4o-mini**: Modelos de linguagem.
- **FAISS**: Busca vetorial.
- **FastAPI**: API REST.
- **Streamlit**: UI web.
- **Pydantic**: Validação de dados.

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/TiagoIA-UX/MaestroIA-Marketing.git
   cd MaestroIA-Marketing
   ```

2. Crie um ambiente virtual:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   ```bash
   cp .env.example .env
   # Edite .env com sua OPENAI_API_KEY
   ```

## Como Usar

### Terminal (Execução Rápida)
```bash
python run.py
```
Executa uma campanha de exemplo e mostra o resultado completo.

### API REST
```bash
python api_server.py
```
Acesse http://localhost:8000/docs para testar endpoints.

Exemplo de requisição:
```json
{
  "objetivo": "Lançar produto X para público feminino 25-40 anos",
  "publico_alvo": "Mulheres 25-40 anos",
  "canais": ["Instagram", "Google Ads"],
  "orcamento": 10000.0
}
```

### Interface Web
```bash
streamlit run ui_app.py
```
Interface simples para configurar e executar campanhas.

## Exemplo de Saída

Ao executar `python run.py`, o sistema gera:

- **Pesquisa**: Análise de mercado com tendências, oportunidades e riscos.
- **Estratégia**: Plano detalhado com posicionamento, mensagem e KPIs.
- **Conteúdos**: Posts para Instagram e anúncios para Google Ads.
- **Publicações**: Simulação de publicações com métricas.
- **Otimização**: Ajustes baseados em dados simulados (cliques, conversões, ROI).

## Modelo de Negócios (SaaS)

- **Planos**:
  - Básico: R$ 299/mês (3 campanhas, agentes básicos).
  - Pro: R$ 799/mês (Campanhas ilimitadas, integrações premium).
  - Enterprise: R$ 2.000+/mês (Customização, suporte dedicado).

- **Aquisição**: Parcerias com agências, webinars, anúncios no LinkedIn.

## Status e Roadmap

- ✅ MVP Funcional: Agentes, grafo, API, UI.
- 🔄 Próximos: Integrações reais (Google Ads, Meta), autenticação, banco de dados.
- 🚀 Futuro: Plugins, painel admin, IA avançada.

## Contribuição

1. Fork o repo.
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`.
3. Commit: `git commit -m 'Adiciona nova funcionalidade'`.
4. Push: `git push origin feature/nova-funcionalidade`.
5. Abra um Pull Request.

## Licença

MIT License.

## Autor

**Tiago Rocha** - Desenvolvido com foco em inovação e escalabilidade para o futuro do marketing digital.

```bash
git clone https://github.com/TiagoIA-UX/MaestroIA-Marketing.git
cd maestroia
```

2. Crie um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate     # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente (se necessário):

```bash
cp .env.example .env
```

---

## Execução

### Modo padrão

```bash
python main.py
```

### Interface gráfica (se aplicável)

```bash
streamlit run app.py
```

---

## Casos de Uso

* Orquestração de agentes de marketing digital
* Automação de processos com IA
* Plataformas educacionais e de conteúdo
* Bases para produtos SaaS com múltiplos agentes

---

## Visão de Evolução

* Sistema de plugins para agentes
* Painel administrativo
* Persistência de memória e contexto
* Integração com e-commerce e APIs externas
* Preparação para uso corporativo e investidores

---

## Status do Projeto

🚧 Em desenvolvimento ativo

---

## Licença

Definir

---

## Autor

**Tiago Rocha**

Projeto desenvolvido com foco em arquitetura limpa, escalabilidade e aplicação real de Inteligência Artificial.
