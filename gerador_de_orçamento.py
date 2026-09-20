import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect
import io
import os
import json

# Configuração da página do Streamlit
st.set_page_config(page_title="Gerador de Orçamentos - THS Elevadores", page_icon="🛗", layout="wide")

# 🔒 BLOCO CSS PARA OCULTAR O ÍCONE DO GITHUB, MENUS E ENGRENAGENS
ocultar_menus_css = """
    <style>
    /* Esconde o menu superior direito (engrenagem/opções) */
    #MainMenu {visibility: hidden;}
    
    /* Esconde a barra de cabeçalho completa (inclui o ícone do GitHub) */
    header {visibility: hidden;}
    
    /* Esconde o rodapé padrão do Streamlit */
    footer {visibility: hidden;}
    
    /* Ajusta o espaçamento do topo que ficou vazio após sumir com o cabeçalho */
    .block-container {padding-top: 2rem;}
    </style>
"""
st.markdown(ocultar_menus_css, unsafe_allow_html=True)

# Detecta automaticamente a pasta onde o script está salvo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo_ths.jpg")
if not os.path.exists(LOGO_PATH):
    LOGO_PATH = os.path.join(BASE_DIR, "logo_ths.png")

# Arquivo local para salvar o histórico de clientes permanentemente
ARQUIVO_BANCO_CLIENTES = os.path.join(BASE_DIR, "banco_clientes.json")

# Função para carregar todos os clientes do banco de dados
def carregar_todos_clientes():
    if os.path.exists(ARQUIVO_BANCO_CLIENTES):
        try:
            with open(ARQUIVO_BANCO_CLIENTES, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    # Clientes padrão caso o banco esteja vazio
    return {
        "Condomínio Edifício Horizon": {
            "cnpj": "12.345.678/0001-99",
            "endereco": "Av. Paulista, 1000 - São Paulo - SP"
        },
        "Condomínio Residencial Vertikal": {
            "cnpj": "98.765.432/0001-00",
            "endereco": "Av. Atlântica, 500 - Rio de Janeiro - RJ"
        }
    }

# Função para salvar/adicionar um cliente no banco de dados
def salvar_cliente_no_banco(nome, cnpj, endereco):
    banco = carregar_todos_clientes()
    banco[nome] = {"cnpj": cnpj, "endereco": endereco}
    with open(ARQUIVO_BANCO_CLIENTES, "w", encoding="utf-8") as f:
        json.dump(banco, f, ensure_ascii=False, indent=4)

# Função para remover um cliente do banco de dados
def remover_cliente_do_banco(nome):
    banco = carregar_todos_clientes()
    if nome in banco:
        del banco[nome]
        with open(ARQUIVO_BANCO_CLIENTES, "w", encoding="utf-8") as f:
            json.dump(banco, f, ensure_ascii=False, indent=4)

# Inicializa o banco de dados na sessão do Streamlit
if 'lista_clientes_completa' not in st.session_state:
    st.session_state.lista_clientes_completa = carregar_todos_clientes()

# Cabeçalho da Aplicação Web com o Logo real da THS
col_logo_web, col_titulo_web = st.columns(2)
with col_logo_web:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=150)
    else:
        st.warning("⚠️ 'logo_ths.jpg' ou 'logo_ths.png' não encontrado na mesma pasta do script.")
with col_titulo_web:
    st.title("Gerador de Orçamento - THS Elevadores")
    st.write("Selecione, cadastre ou remova clientes para gerenciar suas propostas comerciais.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Gestão Permanente de Clientes")
    
    # Opções para a caixa de seleção (Clientes cadastrados + Opção de novo)
    opcoes_select = list(st.session_state.lista_clientes_completa.keys()) + ["+ Cadastrar Novo Cliente"]
    
    cliente_selecionado = st.selectbox("Selecione o Cliente Destinatário:", opcoes_select)
    
    # Lógica para preencher os campos com base na seleção
    if cliente_selecionado == "+ Cadastrar Novo Cliente":
        val_nome = ""
        val_cnpj = ""
        val_endereco = ""
        desativar_nome = False
    else:
        val_nome = cliente_selecionado
        val_cnpj = st.session_state.lista_clientes_completa[cliente_selecionado]["cnpj"]
        val_endereco = st.session_state.lista_clientes_completa[cliente_selecionado]["endereco"]
        desativar_nome = True

    # Campos de entrada de dados
    cliente = st.text_input("Nome do Cliente / Empresa", value=val_nome, disabled=desativar_nome)
    cnpj = st.text_input("CNPJ", value=val_cnpj)
    endereco = st.text_input("Endereço Completo", value=val_endereco)
    
    # Botões de ação baseados na seleção do cliente
    if cliente_selecionado == "+ Cadastrar Novo Cliente":
        if st.button("➕ Gravar Novo Cliente no Banco de Dados", use_container_width=True):
            if cliente and cnpj and endereco:
                salvar_cliente_no_banco(cliente, cnpj, endereco)
                st.session_state.lista_clientes_completa = carregar_todos_clientes()
                st.success(f"Cliente '{cliente}' cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("Preencha todos os campos antes de cadastrar.")
    else:
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("💾 Atualizar Dados", use_container_width=True):
                salvar_cliente_no_banco(cliente, cnpj, endereco)
                st.session_state.lista_clientes_completa = carregar_todos_clientes()
                st.success("Dados atualizados permanentemente!")
                st.rerun()
        with col_btn2:
            if st.button("❌ Remover da Lista", use_container_width=True, type="primary"):
                remover_cliente_do_banco(cliente_selecionado)
                st.session_state.lista_clientes_completa = carregar_todos_clientes()
                st.warning(f"Cliente '{cliente_selecionado}' foi removido com sucesso!")
                st.rerun()

# Inicializa o estado da lista de peças se não existir
if 'pecas' not in st.session_state:
    st.session_state.pecas = [
        {"nome": "Cabo de Tração 1/2", "quantidade": 4, "custo": 150.0},
        {"nome": "Polia de Desvio", "quantidade": 1, "custo": 450.0},
        {"nome": "Placa Eletrônica Principal", "quantidade": 1, "custo": 1200.0}
    ]

with col2:
    st.subheader("⚙️ Itens do Orçamento (Painel Interno)")
    
    with st.form("nova_peca_form", clear_on_submit=True):
        f_nome = st.text_input("Nome da Peça")
        f_qnt = st.number_input("Quantidade", min_value=1, value=1, step=1)
        f_custo = st.number_input("Seu Custo Unitário Real (R$)", min_value=0.0, value=0.0, step=10.0)
        submit = st.form_submit_button("Adicionar Item")
        
        if submit and f_nome:
            st.session_state.pecas.append({"nome": f_nome, "quantidade": f_qnt, "custo": f_custo})
            st.success(f"Item '{f_nome}' adicionado com sucesso!")

    if st.session_state.pecas:
        df_pecas = pd.DataFrame(st.session_state.pecas)
        df_pecas['Preço Venda Unit.'] = df_pecas['custo'] * 2.5
        df_pecas['Total Item'] = df_pecas['Preço Venda Unit.'] * df_pecas['quantidade']
        
        df_display = df_pecas.copy()
        df_display['custo'] = df_display['custo'].map('R$ {:,.2f}'.format)
        df_display['Preço Venda Unit.'] = df_display['Preço Venda Unit.'].map('R$ {:,.2f}'.format)
        df_display['Total Item'] = df_display['Total Item'].map('R$ {:,.2f}'.format)
        
        df_display.columns = ['Nome da Peça', 'Qtd', 'Seu Custo Original', 'Preço Venda Final', 'Total do Item']
        
        st.write("### Itens Atuais no Sistema")
        st.dataframe(df_display, use_container_width=True)
        
        if st.button("Limpar Todos os Itens"):
            st.session_state.pecas = []
            st.rerun()
    else:
        st.info("Nenhum item adicionado ainda.")
# Função que desenha o seu LOGO como Marca d'Água no fundo do PDF
def draw_watermark(canvas, doc):
    if os.path.exists(LOGO_PATH):
        canvas.saveState()
        canvas.setFillAlpha(0.06)
        canvas.setStrokeAlpha(0.06)
        
        largura_logo = 380
        altura_logo = 310
        pos_x = (612 - largura_logo) / 2
        pos_y = (792 - altura_logo) / 2
        
        canvas.drawImage(LOGO_PATH, pos_x, pos_y, width=largura_logo, height=altura_logo, mask='auto')
        canvas.restoreState()

# Geração dinâmica do PDF em memória (Sem rastros de margem ou custos)
def gerar_pdf_orcamento(cliente, cnpj, endereco, pecas):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40,
        title="Orçamento - THS Elevadores"
    )
    
    styles = getSampleStyleSheet()
    
    style_header_company = ParagraphStyle(
        'CompanyHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#C00000')
    )
    
    style_subtitle_company = ParagraphStyle(
        'CompanySubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#555555')
    )

    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        alignment=1,
        textColor=colors.HexColor('#C00000'),
        spaceAfter=20
    )
    
    style_body = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#222222')
    )
    
    style_th = ParagraphStyle(
        'TableHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.white
    )

    story = []
    
    header_data = [
        [Paragraph("THS ELEVADORES", style_header_company), Paragraph("<b>ORÇAMENTO COMERCIAL</b>", style_subtitle_company)],
        [Paragraph("Manutenção e Modernização de Elevadores", style_subtitle_company), Paragraph("Data de Emissão: 20/09/2026", style_subtitle_company)]
    ]
    largura_colunas_cabecalho = (300, 232)
    header_table = Table(header_data, colWidths=largura_colunas_cabecalho)
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))
    
    line_drawing = Drawing(532, 2)
    line_drawing.add(Rect(0, 0, 532, 2, fillColor=colors.HexColor('#C00000'), strokeColor=None))
    story.append(line_drawing)
    story.append(Spacer(1, 15))
    
    client_info = f"""
    <b>Cliente:</b> {cliente}<br/>
    <b>CNPJ:</b> {cnpj}<br/>
    <b>Endereço:</b> {endereco}
    """
    story.append(Paragraph(client_info, style_body))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("PROPOSTA DE FORNECIMENTO DE PEÇAS", style_title))
    
    table_data = [[
        Paragraph("Item / Descrição da Peça", style_th),
        Paragraph("Qtd", style_th),
        Paragraph("Preço Unitário", style_th),
        Paragraph("Preço Total", style_th)
    ]]
    
    total_geral_venda = 0.0
    for p in pecas:
        venda_unit = p['custo'] * 2.5
        total_item_venda = venda_unit * p['quantidade']
        total_geral_venda += total_item_venda
        
        table_data.append([
            Paragraph(p['nome'], style_body),
            Paragraph(str(p['quantidade']), style_body),
            Paragraph(f"R$ {venda_unit:,.2f}", style_body),
            Paragraph(f"R$ {total_item_venda:,.2f}", style_body)
        ])
        
    table_data.append([
        Paragraph("<b>VALOR TOTAL DA PROPOSTA</b>", style_body),
        "", "",
        Paragraph(f"<b>R$ {total_geral_venda:,.2f}</b>", style_body)
    ])
    
    largura_colunas_itens = (252, 50, 115, 115)
    item_table = Table(table_data, colWidths=largura_colunas_itens)
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C00000')),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#DDDDDD')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('SPAN', (0, -1), (2, -1)),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#EEEEEE')),
    ]))
    
    story.append(item_table)
    story.append(Spacer(1, 30))
    
    termos = """
    <b>Termos e Condições:</b><br/>
    1. Validade desta proposta: 15 dias a contar da data de emissão.<br/>
    2. Prazo de entrega: Conforme disponibilidade de estoque.<br/>
    3. Garantia: 90 dias contra defeitos de fabricação.<br/>
    <br/><br/>
    Atenciosamente,<br/>
    <b>THS ELEVADORES LTDA</b>
    """
    story.append(Paragraph(termos, style_body))
    
    doc.build(story, onFirstPage=draw_watermark, onLaterPages=draw_watermark)
    
    buffer.seek(0)
    return buffer.getvalue()

if st.session_state.pecas:
    st.subheader("🖨️ Emitir Documento")
    pdf_bytes = gerar_pdf_orcamento(cliente if cliente else "Cliente", cnpj, endereco, st.session_state.pecas)
    
    st.download_button(
        label="📥 Baixar Orçamento em PDF Oficial para Cliente",
        data=pdf_bytes,
        file_name=f"Orcamento_THS_{(cliente if cliente else 'Cliente').replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
else:
    st.warning("Adicione pelo menos um item para liberar a emissão do orçamento em PDF.")
