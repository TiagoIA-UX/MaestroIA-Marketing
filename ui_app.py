import streamlit as st
import requests
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.units import inch
from maestroia.graphs.marketing_graph import build_marketing_graph

def gerar_pdf_campanha(result, objetivo, publico, canais, orcamento):
    """Gera um PDF com os resultados da campanha"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
    )
    normal_style = styles['Normal']
    
    story = []
    
    # Título
    story.append(Paragraph("Relatório da Campanha MaestroIA", title_style))
    story.append(Spacer(1, 12))
    
    # Informações da campanha
    story.append(Paragraph("Informações da Campanha", heading_style))
    story.append(Paragraph(f"<b>Objetivo:</b> {objetivo}", normal_style))
    story.append(Paragraph(f"<b>Público-Alvo:</b> {publico}", normal_style))
    story.append(Paragraph(f"<b>Canais:</b> {', '.join(canais)}", normal_style))
    story.append(Paragraph(f"<b>Orçamento:</b> R$ {orcamento:.2f}", normal_style))
    story.append(Spacer(1, 20))
    
    # Resultados
    if "pesquisa" in result:
        story.append(Paragraph("Análise de Mercado", heading_style))
        story.append(Paragraph(result["pesquisa"], normal_style))
        story.append(Spacer(1, 12))
    
    if "conteudos" in result:
        story.append(Paragraph("Conteúdos Gerados", heading_style))
        for i, conteudo in enumerate(result["conteudos"], 1):
            story.append(Paragraph(f"Conteúdo {i}:", styles['Heading3']))
            # Limpar markdown e HTML
            conteudo_limpo = conteudo.replace('*', '').replace('#', '').replace('**', '')
            story.append(Paragraph(conteudo_limpo, normal_style))
            story.append(Spacer(1, 8))
        story.append(Spacer(1, 12))
    
    if "publicacoes" in result:
        story.append(Paragraph("Publicações", heading_style))
        for canal, status in result["publicacoes"].items():
            story.append(Paragraph(f"<b>{canal}:</b> {status}", normal_style))
        story.append(Spacer(1, 12))
    
    # Imagens (se houver URLs válidas)
    if "imagens" in result:
        story.append(Paragraph("Imagens Geradas", heading_style))
        for img_url in result["imagens"]:
            if img_url.startswith("http"):
                try:
                    # Tentar baixar e adicionar imagem
                    response = requests.get(img_url)
                    if response.status_code == 200:
                        img_buffer = BytesIO(response.content)
                        img = RLImage(img_buffer, width=4*inch, height=3*inch)
                        story.append(img)
                        story.append(Spacer(1, 12))
                except:
                    story.append(Paragraph(f"Imagem: {img_url}", normal_style))
            else:
                story.append(Paragraph(f"Descrição da imagem: {img_url}", normal_style))
    
    # Rodapé
    story.append(Spacer(1, 30))
    story.append(Paragraph("Relatório gerado pelo MaestroIA", styles['Italic']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

st.title("MaestroIA - Orquestração de Agentes de Marketing")

# Simulação de login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if email and password:
            st.session_state.logged_in = True
            st.session_state.email = email
            st.rerun()
        else:
            st.error("Credenciais inválidas")
else:
    st.success(f"Logado como {st.session_state.email}")

    graph = build_marketing_graph()

    # Abas para organizar
    tab1, tab2, tab3 = st.tabs(["Campanha", "Configurações", "Resultados"])

    with tab1:
        st.header("Criar Campanha")
        objetivo = st.text_input("Objetivo da Campanha", placeholder="Ex: Aumentar vendas em 30%")
        publico = st.text_input("Público-Alvo", placeholder="Ex: Mulheres 25-40 anos interessadas em bem-estar")
        canais = st.multiselect("Canais", ["Instagram", "Facebook", "Google Ads", "Twitter/X", "LinkedIn", "TikTok", "YouTube", "Pinterest", "Snapchat"])
        orcamento = st.number_input("Orçamento (R$)", min_value=0.0, value=1000.0)

        if st.button("Executar Campanha", type="primary"):
            if not objetivo or not publico or not canais:
                st.error("Preencha todos os campos obrigatórios!")
            else:
                # Barra de progresso
                progress_bar = st.progress(0)
                status_text = st.empty()

                state = {
                    "objetivo": objetivo,
                    "publico_alvo": publico,
                    "canais": canais,
                    "orcamento": orcamento
                }

                # Simular progresso por agente
                agentes = ["pesquisador", "estrategista", "criador_conteudo", "publicador", "otimizador", "maestro"]
                for i, agente in enumerate(agentes):
                    status_text.text(f"Executando {agente}...")
                    progress_bar.progress((i + 1) / len(agentes))
                    # Pequeno delay para visualização
                    import time
                    time.sleep(0.5)

                # Executar campanha
                result = graph.invoke(state)
                st.session_state.last_result = result
                st.session_state.campaign_executed = True

                status_text.text("Campanha concluída!")
                progress_bar.progress(1.0)

                st.success("Campanha executada com sucesso!")

    with tab2:
        st.header("Configurações de Redes Sociais")
        st.info("Configure suas chaves de API para integrações reais. Deixe vazio para usar simulações.")

        with st.expander("Meta (Instagram/Facebook)"):
            st.text_input("Access Token", type="password", key="meta_token")
            st.text_input("App ID", key="meta_app_id")

        with st.expander("Twitter/X"):
            st.text_input("API Key", type="password", key="twitter_api_key")
            st.text_input("API Secret", type="password", key="twitter_api_secret")
            st.text_input("Access Token", type="password", key="twitter_access_token")
            st.text_input("Access Token Secret", type="password", key="twitter_access_secret")

        with st.expander("LinkedIn"):
            st.text_input("Access Token", type="password", key="linkedin_token")

        with st.expander("TikTok"):
            st.text_input("Access Token", type="password", key="tiktok_token")

        with st.expander("YouTube"):
            st.text_input("API Key", type="password", key="youtube_key")

        with st.expander("Pinterest"):
            st.text_input("Access Token", type="password", key="pinterest_token")

        with st.expander("Snapchat"):
            st.text_input("Access Token", type="password", key="snapchat_token")

        if st.button("Salvar Configurações"):
            st.success("Configurações salvas! (Nota: Ainda não persistidas - implementar futuramente)")

    with tab3:
        if "campaign_executed" in st.session_state and st.session_state.campaign_executed:
            result = st.session_state.last_result

            st.header("Resultados da Campanha")

            # Mostrar resumo
            if "pesquisa" in result:
                st.subheader("📊 Pesquisa de Mercado")
                st.write(result["pesquisa"])

            if "conteudos" in result:
                st.subheader("📝 Conteúdos Gerados")
                for i, conteudo in enumerate(result["conteudos"], 1):
                    st.write(f"**Conteúdo {i}:** {conteudo[:200]}...")

            if "publicacoes" in result:
                st.subheader("🚀 Publicações")
                st.json(result["publicacoes"])

            if "imagens" in result:
                st.subheader("🖼️ Imagens Geradas")
                for img_url in result["imagens"]:
                    if img_url.startswith("http"):
                        st.image(img_url, caption="Imagem gerada")
                    else:
                        st.write(img_url)

            # Botões de ação
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("✅ Aprovar e Publicar", type="primary"):
                    st.success("Publicação aprovada! (Integração real pendente)")

            with col2:
                if st.button("🔄 Ajustar Campanha"):
                    st.info("Recarregue a página e ajuste os parâmetros.")

            with col3:
                # Download JSON
                result_json = json.dumps(result, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📄 Baixar JSON",
                    data=result_json,
                    file_name="campanha_maestroia.json",
                    mime="application/json"
                )

            with col4:
                # Download PDF
                pdf_buffer = gerar_pdf_campanha(result, objetivo, publico, canais, orcamento)
                st.download_button(
                    label="📕 Baixar PDF",
                    data=pdf_buffer,
                    file_name="relatorio_campanha_maestroia.pdf",
                    mime="application/pdf"
                )
        else:
            st.info("Execute uma campanha primeiro para ver os resultados.")