# MaestroIA

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/TiagoIA-UX/MaestroIA/releases/tag/v1.0.0)
[![Python](https://img.shields.io/badge/python-3.14+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

Plataforma SaaS para orquestração de agentes de IA em marketing digital.

## 🎯 Sobre o Projeto

O **MaestroIA** é uma plataforma inovadora que permite a profissionais de marketing criar e gerenciar equipes autônomas de agentes de IA. Inspirado na reportagem do Fantástico sobre a "profissão do futuro" (orquestrar agentes de IA), o sistema executa campanhas de marketing digital completas de ponta a ponta, desde pesquisa de mercado até otimização de resultados.

O usuário define o objetivo da campanha (ex.: "Lançar produto X para público feminino 25-40 anos no Instagram e Google Ads"), e os agentes trabalham em colaboração: pesquisam tendências, criam estratégias, produzem conteúdos, publicam e otimizam — tudo com comunicação interna e supervisão humana opcional.

## ✨ Funcionalidades (v1.0.0)

### 🤖 Agentes Autônomos
- **Pesquisador**: Análise de mercado e tendências (Google Trends)
- **Estrategista**: Desenvolvimento de estratégias de marketing
- **Criador de Conteúdo**: Produção de conteúdos otimizados por rede social
- **Publicador**: Publicação automatizada em múltiplas plataformas
- **Otimizador**: Análise e otimização de performance
- **Maestro**: Coordenação e supervisão geral

### 🔗 Integrações
- **OpenAI**: GPT-4o-mini para texto, DALL-E para imagens
- **Google Trends**: Pesquisa de tendências reais
- **Twitter/X**: Publicação automatizada
- **Meta (Instagram/Facebook)**: Estrutura preparada
- **Google Ads, LinkedIn, TikTok**: Estruturas implementadas
- **YouTube, Pinterest, Snapchat**: Suporte planejado

### 🔐 Segurança
- **Autenticação obrigatória** com cadastro seguro
- **Validação de emails** e senhas fortes
- **Criptografia SHA-256** para senhas
- **Sistema de permissões** e controle de acesso

### 🎨 Interface
- **Design elegante** com gradientes e cards modernos
- **Interface intuitiva** para usuários não-técnicos
- **Progress bars** e feedback visual em tempo real
- **Relatórios em PDF** para download
- **Configurações de APIs** organizadas por plataforma

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.14 ou superior
- Git
- Conta OpenAI (para funcionalidades de IA)

### Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/TiagoIA-UX/MaestroIA.git
cd MaestroIA

# Crie ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/Mac

# Instale dependências
pip install -r requirements.txt
```

### Configuração

1. **Chaves de API**: Configure suas chaves no arquivo `.env`:
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite com suas chaves
OPENAI_API_KEY=sk-your-openai-key
TWITTER_API_KEY=your-twitter-key
# ... outras chaves conforme necessário
```

2. **Execute a aplicação**:
```bash
# Interface Web (recomendado)
python -m streamlit run ui_app.py

# Ou API REST
python api_server.py
```

3. **Acesse**: `http://localhost:8503`

### Primeiro Uso
1. **Cadastre-se** na aba "📝 Cadastrar-se"
2. **Configure APIs** na aba "⚙️ Configurações" (opcional)
3. **Crie campanhas** na aba "📝 Criar Campanha"
4. **Acompanhe resultados** na aba "📊 Resultados"

## 📊 Arquitetura

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
├─ users.json       # Armazenamento de usuários
├─ requirements.txt
├─ .env.example
└─ README.md
```

## 🛠️ Tecnologias

- **Python 3.14+**: Compatível com versões recentes
- **LangGraph**: Orquestração de agentes
- **Streamlit**: Interface web moderna
- **FastAPI**: API REST (estrutura preparada)
- **OpenAI API**: GPT-4o-mini + DALL-E
- **FAISS**: Memória vetorial
- **ReportLab**: Geração de PDFs
- **SQLAlchemy**: ORM para banco de dados (planejado)
- **OpenAI GPT-4o-mini**: Modelos de linguagem.
- **APIs de Redes Sociais**: Twitter (tweepy), Google Ads, Meta, etc.

## Configuração de APIs

Para usar integrações reais com redes sociais, configure as chaves de API no arquivo `.env`:

```bash
# Copie .env.example para .env
cp .env.example .env

# Edite .env com suas chaves:
OPENAI_API_KEY=your_key
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
# ... outras chaves
```

**APIs suportadas:**
- **Twitter/X**: Gratuito para posts (até 1.500 tweets/mês)
- **Meta (Instagram/Facebook)**: Requer app no Facebook Developers
- **Google Ads**: Requer conta Google Ads certificada
- **LinkedIn**: Requer app no LinkedIn Developers
- **TikTok**: Requer conta Business
- **YouTube**: API gratuita para uploads
- **Pinterest/Snapchat**: Requerem contas business

Se as chaves não forem configuradas, o sistema usa simulações.
- **FAISS**: Busca vetorial.
- **FastAPI**: API REST.
- **Streamlit**: UI web.
- **Pydantic**: Validação de dados.

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/TiagoIA-UX/MaestroIA.git
   cd MaestroIA
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

### Cadastro e Login
- **API**: Use `/register` para criar conta e `/token` para login (retorna JWT).
- **UI**: Interface Streamlit inclui formulário de login básico.

### Terminal (Execução Rápida)
```bash
python run.py
```
Executa uma campanha de exemplo e mostra o resultado completo.

### API REST
```bash
python api_server.py
```
Acesse http://localhost:8000/docs para testar endpoints (requer token JWT).

Exemplo de requisição autenticada:
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
Interface com login e execução de campanhas, exibindo resultados e imagens geradas.

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

## Atribuições

Para informações sobre citações de código e licenças de terceiros, veja [ATTRIBUTIONS.md](ATTRIBUTIONS.md).

---

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## Autor

**Tiago Rocha**

Projeto desenvolvido com foco em arquitetura limpa, escalabilidade e aplicação real de Inteligência Artificial.
