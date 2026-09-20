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
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 2rem;}
    </style>
"""
st.markdown(ocultar_menus_css, unsafe_allow_html=True)

# Detecta automaticamente a pasta onde o script está salvo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo_ths.jpg")
if not os.path.exists(LOGO_PATH):
    LOGO_PATH = os.path.join(BASE_DIR, "logo_ths.png")

# Arquivos locais para salvar os estados do sistema permanentemente
ARQUIVO_BANCO_CLIENTES = os.path.join(BASE_DIR, "banco_clientes.json")
ARQUIVO_CONTROLE_SENHA = os.path.join(BASE_DIR, "controle_senha.json")

# 🔑 FUNÇÕES DE CONTROLE DE ACESSOS E SENHA (PERMITE 8 USOS)
def carregar_controle_seguranca():
    if os.path.exists(ARQUIVO_CONTROLE_SENHA):
        try:
            with open(ARQUIVO_CONTROLE_SENHA, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"senha": "ths123", "usos": 0}

def salvar_controle_seguranca(senha, usos):
    dados = {"senha": str(senha), "usos": int(usos)}
    with open(ARQUIVO_CONTROLE_SENHA, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# Inicialização de estados do sistema na sessão atual
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "bloqueado" not in st.session_state:
    st.session_state.bloqueado = False

# Carrega o estado atual de segurança guardado no disco do servidor
CONTROLE_ATUAL = carregar_controle_seguranca()
SENHA_VALIDA_AGORA = CONTROLE_ATUAL.get("senha", "ths123")
USOS_REALIZADOS = CONTROLE_ATUAL.get("usos", 0)
USUARIO_CORRETO = "ths"

# Tela de Bloqueio Definitivo pós-uso ou encerramento por limite
if st.session_state.bloqueado:
    st.markdown("<h2 style='text-align: center; color: #C00000;'>🔒 Sessão Encerrada</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>Esta aplicação expirou o limite de uso de segurança.</h4>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px; font-weight: bold; color: #C00000;'>Entre em contato com o administrador Bruno Held.</p>", unsafe_allow_html=True)
    st.stop()

def tela_login():
    st.markdown("<h2 style='text-align: center; color: #C00000;'>🛗 THS ELEVADORES</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Painel Restrito - Sistema de Orçamentos Comercial</p>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns((1, 2, 1))
    with col_l2:
        with st.form("formulario_login"):
            usuario_input = st.text_input("Usuário", placeholder="Digite o usuário da empresa")
            senha_input = st.text_input("Senha", type="password", placeholder="Digite a senha de segurança")
            botao_entrar = st.form_submit_button("Entrar no Sistema", use_container_width=True)
            
            if botao_entrar:
                # Se a senha padrão já atingiu os 8 usos e mudou para 8148 no servidor
                if usuario_input == USUARIO_CORRETO and senha_input == "ths123" and SENHA_VALIDA_AGORA == "8148":
                    st.error("❌ Esta senha padrão atingiu o limite máximo de 8 usos e está expirada. Para obter acesso ilimitado, entre em contato com o administrador Bruno Held.")
                
                # Validação dos acessos permitidos com a senha padrão ths123 (Até 8 vezes)
                elif usuario_input == USUARIO_CORRETO and senha_input == "ths123" and SENHA_VALIDA_AGORA == "ths123":
                    novo_contador = USOS_REALIZADOS + 1
                    if novo_contador >= 8:
                        salvar_controle_seguranca("8148", novo_contador) # Bloqueia mudando a senha mestre para 8148
                    else:
                        salvar_controle_seguranca("ths123", novo_contador) # Incrementa o uso
                    
                    st.session_state.autenticado = True
                    # Alerta o usuário na tela sobre o limite restante
                    st.warning(f"Atenção: Você está utilizando uma senha temporária. Uso registrado ({novo_contador}/8). Para obter acesso ilimitado, entre em contato com o administrador Bruno Held.")
                    st.rerun()
                
                # Validação do acesso permanente com a sua senha master 8148
                elif usuario_input == USUARIO_CORRETO and senha_input == "8148":
                    st.session_state.autenticado = True
                    st.success("Acesso master autorizado com sucesso!")
                    st.rerun()
                
                else:
                    st.error("Usuário ou senha incorretos. Tente novamente.")

# Aplica a trava rígida de login
if not st.session_state.autenticado:
    tela_login()
    st.stop()
def carregar_todos_clientes():
    if os.path.exists(ARQUIVO_BANCO_CLIENTES):
        try:
            with open(ARQUIVO_BANCO_CLIENTES, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "Condomínio Edifício Horizon": {
            "cnpj": "12.345.678/0001-99",
            "endereco": "Av. Paulista, 1000 - São Paulo - SP"
        }
    }

def salvar_cliente_no_banco(nome, cnpj, endereco):
    banco = carregar_todos_clientes()
    banco[nome] = {"cnpj": cnpj, "endereco": endereco}
    with open(ARQUIVO_BANCO_CLIENTES, "w", encoding="utf-8") as f:
        json.dump(banco, f, ensure_ascii=False, indent=4)

def remover_cliente_do_banco(nome):
    banco = carregar_todos_clientes()
    if nome in banco:
        del banco[nome]
        with open(ARQUIVO_BANCO_CLIENTES, "w", encoding="utf-8") as f:
            json.dump(banco, f, ensure_ascii=False, indent=4)

if 'lista_clientes_completa' not in st.session_state:
    st.session_state.lista_clientes_completa = carregar_todos_clientes()

col_logo_web, col_titulo_web, col_logout = st.columns((1, 2, 0.6))
with col_logo_web:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=150)
    else:
        st.warning("⚠️ Logo não encontrado.")
with col_titulo_web:
    st.title("Gerador de Orçamento - THS Elevadores")
    st.write("Painel Comercial Restrito - Gerenciamento de Propostas.")
with col_logout:
    st.write("") 
    if st.button("🚪 Fechar Aplicação", type="secondary", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.bloqueado = True
        st.rerun()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Gestão Permanente de Clientes")
    opcoes_select = list(st.session_state.lista_clientes_completa.keys()) + ["+ Cadastrar Novo Cliente"]
    cliente_selecionado = st.selectbox("Selecione o Cliente Destinatário:", opcoes_select)
    
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

    cliente = st.text_input("Nome do Cliente / Empresa", value=val_nome, disabled=desativar_nome)
    cnpj = st.text_input("CNPJ", value=val_cnpj)
    endereco = st.text_input("Endereço Completo", value=val_endereco)
    
    if cliente_selecionado == "+ Cadastrar Novo Cliente":
        if st.button("➕ Gravar Novo Cliente no Banco de Dados", use_container_width=True):
            if cliente and cnpj and endereco:
                salvar_cliente_no_banco(cliente, cnpj, endereco)
                st.session_state.lista_clientes_completa = carregar_todos_clientes()
                st.success(f"Cliente '{cliente}' cadastrado!")
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
                st.warning(f"Cliente '{cliente_selecionado}' foi removido!")
                st.rerun()

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
            st.success(f"Item '{f_nome}' adicionado!")

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
        'CompanyHeader', parent=styles['Normal'], fontName='Helvetica-Bold',
        fontSize=22, leading=26, textColor=colors.HexColor('#C00000')
    )
    style_subtitle_company = ParagraphStyle(
        'CompanySubtitle', parent=styles['Normal'], fontName='Helvetica',
        fontSize=10, leading=12, textColor=colors.HexColor('#555555')
    )
    style_title = ParagraphStyle(
        'DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold',
        fontSize=16, leading=20, alignment=1, textColor=colors.HexColor('#C00000'), spaceAfter=20
    )
    style_body = ParagraphStyle(
        'BodyTextCustom', parent=styles['Normal'], fontName='Helvetica',
        fontSize=10, leading=14, textColor=colors.HexColor('#222222')
    )
    style_th = ParagraphStyle(
        'TableHead', parent=styles['Normal'], fontName='Helvetica-Bold',
        fontSize=10, leading=12, textColor=colors.white
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
    
    client_info = f"<b>Cliente:</b> {cliente}<br/><b>CNPJ:</b> {cnpj}<br/><b>Endereço:</b> {endereco}"
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
        Paragraph("<b>VALOR TOTAL DA PROPOSTA</b>", style_body), "", "",
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
    return buffer.getvalue()

if st.session_state.pecas:
    st.subheader("🖨️ Emitir Documento")
    pdf_bytes = gerar_pdf_orcamento(cliente if cliente else "Cliente", cnpj, endereco, st.session_state.pecas)
    
    if st.download_button(
        label="📥 Baixar Orçamento em PDF Oficial para Cliente",
        data=pdf_bytes,
        file_name=f"Orcamento_THS_{(cliente if cliente else 'Cliente').replace(' ', '_')}.pdf",
        mime="application/pdf",
        with_key="btn_download_pdf",
        use_container_width=True
    ):
        st.session_state.autenticado = False
        st.session_state.bloqueado = True
        st.rerun()
else:
    st.warning("Adicione pelo menos um item para liberar a emissão do orçamento em PDF.")
