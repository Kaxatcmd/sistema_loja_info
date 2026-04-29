"""
Gerador do relatório de segurança — XSS e CSRF.

Explica por que razão estas proteções não foram implementadas
no projeto e que metodologias seriam necessárias caso a aplicação
fosse uma plataforma web.

Dependência:
    pip install reportlab

Utilização:
    python docs/gerar_relatorio_seguranca.py

O ficheiro PDF é gerado na mesma pasta deste script.
"""

from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------------
# Constantes visuais
# ---------------------------------------------------------------------------

AZUL_ESCURO   = colors.HexColor("#1e40af")
AZUL_CLARO    = colors.HexColor("#eff6ff")
CINZA_TEXTO   = colors.HexColor("#1e293b")
CINZA_SUAVE   = colors.HexColor("#64748b")
AMARELO_AVISO = colors.HexColor("#fef3c7")
AMARELO_BORDA = colors.HexColor("#f59e0b")
VERDE_CODIGO  = colors.HexColor("#86efac")
FUNDO_CODIGO  = colors.HexColor("#0f172a")
BRANCO        = colors.white

MARGEM = 2.2 * cm
PASTA_SAIDA = Path(__file__).parent


# ---------------------------------------------------------------------------
# Cabeçalho e rodapé de página
# ---------------------------------------------------------------------------

def _desenhar_pagina(canvas, doc):
    canvas.saveState()
    largura, altura = A4

    # Cabeçalho
    canvas.setFillColor(AZUL_ESCURO)
    canvas.rect(0, altura - 1.4 * cm, largura, 1.4 * cm, fill=True, stroke=False)
    canvas.setFillColor(BRANCO)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(MARGEM, altura - 0.9 * cm, "Sistema de Loja de Informática")
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(
        largura - MARGEM,
        altura - 0.9 * cm,
        "Relatório de Segurança — XSS e CSRF",
    )

    # Rodapé
    canvas.setFillColor(AZUL_ESCURO)
    canvas.rect(0, 0, largura, 1.0 * cm, fill=True, stroke=False)
    canvas.setFillColor(BRANCO)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(
        MARGEM,
        0.35 * cm,
        f"Gerado em {date.today().strftime('%d de %B de %Y')}",
    )
    canvas.drawRightString(
        largura - MARGEM,
        0.35 * cm,
        f"Página {doc.page}",
    )

    canvas.restoreState()


# ---------------------------------------------------------------------------
# Estilos
# ---------------------------------------------------------------------------

def _estilos():
    base = getSampleStyleSheet()

    titulo_doc = ParagraphStyle(
        "TituloDoc",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=BRANCO,
        alignment=TA_CENTER,
        spaceAfter=6,
    )

    subtitulo_doc = ParagraphStyle(
        "SubtituloDoc",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=11,
        textColor=colors.HexColor("#bfdbfe"),
        alignment=TA_CENTER,
        spaceAfter=4,
    )

    titulo_seccao = ParagraphStyle(
        "TituloSeccao",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=AZUL_ESCURO,
        spaceBefore=18,
        spaceAfter=6,
        borderPad=4,
    )

    corpo = ParagraphStyle(
        "Corpo",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        textColor=CINZA_TEXTO,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
    )

    nota = ParagraphStyle(
        "Nota",
        parent=base["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=10,
        textColor=colors.HexColor("#92400e"),
        leading=15,
        alignment=TA_JUSTIFY,
    )

    codigo = ParagraphStyle(
        "Codigo",
        parent=base["Normal"],
        fontName="Courier",
        fontSize=8.5,
        textColor=VERDE_CODIGO,
        leading=13,
        alignment=TA_LEFT,
        leftIndent=10,
    )

    return titulo_doc, subtitulo_doc, titulo_seccao, corpo, nota, codigo


# ---------------------------------------------------------------------------
# Blocos auxiliares
# ---------------------------------------------------------------------------

def _caixa_aviso(texto, estilo_nota):
    """Caixa destacada a amarelo para notas importantes."""
    dados = [[Paragraph(texto, estilo_nota)]]
    tabela = Table(dados, colWidths=[14.5 * cm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AMARELO_AVISO),
        ("LINEAFTER",  (0, 0), (0, -1), 4, AMARELO_BORDA),
        ("LINEBEFORE", (0, 0), (0, -1), 4, AMARELO_BORDA),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
    ]))
    return tabela


def _caixa_codigo(linhas, estilo_codigo):
    """Bloco de código com fundo escuro."""
    conteudo = "<br/>".join(linhas)
    dados = [[Paragraph(conteudo, estilo_codigo)]]
    tabela = Table(dados, colWidths=[14.5 * cm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), FUNDO_CODIGO),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
        ("ROUNDEDCORNERS", [6]),
    ]))
    return tabela


def _capa(titulo_doc, subtitulo_doc):
    """Bloco de capa do documento."""
    dados = [[
        Paragraph("Relatório de Segurança", titulo_doc),
    ], [
        Paragraph("Proteções XSS e CSRF — Contexto, Justificação e Metodologia", subtitulo_doc),
    ], [
        Paragraph(
            f"Sistema de Loja de Informática &nbsp;&nbsp;·&nbsp;&nbsp; {date.today().year}",
            subtitulo_doc,
        ),
    ]]
    tabela = Table(dados, colWidths=[14.5 * cm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), AZUL_ESCURO),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
    ]))
    return tabela


# ---------------------------------------------------------------------------
# Construção do documento
# ---------------------------------------------------------------------------

def gerar():
    caminho = PASTA_SAIDA / "seguranca_xss_csrf.pdf"
    largura, altura = A4

    doc = BaseDocTemplate(
        str(caminho),
        pagesize=A4,
        leftMargin=MARGEM,
        rightMargin=MARGEM,
        topMargin=2.0 * cm,
        bottomMargin=1.8 * cm,
    )

    frame = Frame(
        MARGEM,
        1.8 * cm,
        largura - 2 * MARGEM,
        altura - 3.4 * cm,
        id="principal",
    )
    doc.addPageTemplates([
        PageTemplate(id="padrao", frames=[frame], onPage=_desenhar_pagina)
    ])

    s_titulo, s_subtitulo, s_seccao, s_corpo, s_nota, s_codigo = _estilos()
    divisor = HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"))
    espaco = Spacer(1, 0.35 * cm)

    conteudo = []

    # ── Capa ────────────────────────────────────────────────────────────────
    conteudo.append(_capa(s_titulo, s_subtitulo))
    conteudo.append(Spacer(1, 0.7 * cm))

    # ── Secção 1 — O que são XSS e CSRF ────────────────────────────────────
    conteudo.append(Paragraph("1. O que são XSS e CSRF", s_seccao))
    conteudo.append(divisor)
    conteudo.append(espaco)

    conteudo.append(Paragraph(
        "O Cross-Site Scripting, habitualmente abreviado como XSS, é um tipo de ataque "
        "que consiste em injetar código JavaScript malicioso numa página web. Quando um "
        "utilizador visita essa página, o código executa no seu browser, podendo roubar "
        "cookies de sessão, redirecionar para sites fraudulentos ou capturar credenciais "
        "introduzidas nos formulários. O ataque tira partido da confiança que o browser "
        "deposita no conteúdo que recebe do servidor.",
        s_corpo,
    ))

    conteudo.append(Paragraph(
        "O Cross-Site Request Forgery, conhecido como CSRF, funciona de forma diferente. "
        "Aqui o atacante engana um utilizador autenticado a enviar, sem saber, um pedido "
        "HTTP para uma aplicação onde já tem sessão ativa. Por exemplo, um utilizador "
        "com sessão aberta num banco online visita um site malicioso que, em segundo plano, "
        "submete um formulário invisível para transferir dinheiro. O servidor, ao receber "
        "o pedido com os cookies legítimos do utilizador, não consegue distinguir se a "
        "ação foi intencional ou forçada.",
        s_corpo,
    ))

    # ── Secção 2 — Por que não foram implementadas ──────────────────────────
    conteudo.append(Spacer(1, 0.2 * cm))
    conteudo.append(Paragraph("2. Por que não foram implementadas neste projeto", s_seccao))
    conteudo.append(divisor)
    conteudo.append(espaco)

    conteudo.append(Paragraph(
        "A razão é simples e direta: este projeto é uma aplicação desktop desenvolvida "
        "em Python com a biblioteca Tkinter. Não existe nenhum browser envolvido, não "
        "há pedidos HTTP entre cliente e servidor web, e não existe renderização de HTML. "
        "A interface é construída diretamente pelo sistema operativo, através de widgets "
        "nativos, o que elimina por completo o contexto em que XSS e CSRF operam.",
        s_corpo,
    ))

    conteudo.append(_caixa_aviso(
        "XSS e CSRF são ameaças exclusivas de aplicações web que correm no browser. "
        "Uma aplicação desktop como esta não tem superfície de ataque para nenhuma "
        "das duas vulnerabilidades. Implementar proteções contra elas seria "
        "tecnicamente incorreto e induziria em erro quem analisasse o código.",
        s_nota,
    ))
    conteudo.append(espaco)

    conteudo.append(Paragraph(
        "A comunicação desta aplicação faz-se diretamente com a base de dados MariaDB "
        "através de um driver Python, sem qualquer intermediário HTTP. Não existem "
        "formulários HTML, não existem cookies de sessão web, e não existe um servidor "
        "a servir páginas. Por este motivo, as proteções implementadas foram as que "
        "realmente fazem sentido neste contexto, nomeadamente a validação de inputs, "
        "o uso de prepared statements contra injeção SQL, o hashing de passwords com "
        "bcrypt, e a limitação de tentativas de login.",
        s_corpo,
    ))

    # ── Secção 3 — Metodologia XSS se fosse web ────────────────────────────
    conteudo.append(Spacer(1, 0.2 * cm))
    conteudo.append(Paragraph(
        "3. Como se protegeria contra XSS se fosse uma aplicação web", s_seccao
    ))
    conteudo.append(divisor)
    conteudo.append(espaco)

    conteudo.append(Paragraph(
        "Numa aplicação web, a primeira linha de defesa contra XSS consiste em nunca "
        "colocar diretamente no HTML qualquer dado que venha do utilizador. Todos os "
        "valores devem passar por um processo de escaping antes de serem renderizados, "
        "convertendo caracteres especiais como o sinal de menor, o sinal de maior e as "
        "aspas nas suas entidades HTML equivalentes, tornando-os inofensivos para o browser.",
        s_corpo,
    ))

    conteudo.append(Paragraph(
        "Num projeto Flask, por exemplo, o motor de templates Jinja2 faz este escaping "
        "automaticamente quando se usa a sintaxe de duplas chavetas. Para situações em "
        "que seja necessário renderizar HTML de forma explícita, existe a função Markup "
        "que sinaliza o conteúdo como seguro, devendo ser usada apenas com dados "
        "previamente sanitizados.",
        s_corpo,
    ))

    conteudo.append(_caixa_codigo([
        "# Flask com Jinja2 — escaping automático",
        "# O template renderiza assim:",
        "# &lt;p&gt;{{ nome_utilizador }}&lt;/p&gt;",
        "#",
        "# Se nome_utilizador = '&lt;script&gt;alert(1)&lt;/script&gt;'",
        "# O browser recebe: &amp;lt;script&amp;gt;alert(1)&amp;lt;/script&amp;gt;",
        "# e trata-o como texto — não como código.",
    ], s_codigo))
    conteudo.append(espaco)

    conteudo.append(Paragraph(
        "Uma segunda camada de proteção é a Content Security Policy, uma diretiva "
        "enviada no cabeçalho HTTP que instrui o browser a só executar scripts "
        "provenientes de origens explicitamente autorizadas, bloqueando qualquer "
        "script injetado pelo atacante, mesmo que chegue a ser inserido na página.",
        s_corpo,
    ))

    conteudo.append(_caixa_codigo([
        "# Cabeçalho HTTP Content-Security-Policy",
        "Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'",
        "#",
        "# Em Flask:",
        "response.headers['Content-Security-Policy'] = \"default-src 'self'\"",
    ], s_codigo))
    conteudo.append(espaco)

    # ── Secção 4 — Metodologia CSRF se fosse web ───────────────────────────
    conteudo.append(Spacer(1, 0.2 * cm))
    conteudo.append(Paragraph(
        "4. Como se protegeria contra CSRF se fosse uma aplicação web", s_seccao
    ))
    conteudo.append(divisor)
    conteudo.append(espaco)

    conteudo.append(Paragraph(
        "A proteção contra CSRF assenta num mecanismo de tokens. O servidor gera um "
        "valor aleatório e imprevisível, associa-o à sessão do utilizador, e inclui-o "
        "como campo oculto em todos os formulários. Quando o formulário é submetido, "
        "o servidor valida que o token recebido corresponde ao que emitiu. Como um "
        "site malicioso não tem acesso ao token, os seus pedidos forjados são "
        "automaticamente rejeitados.",
        s_corpo,
    ))

    conteudo.append(_caixa_codigo([
        "# Flask-WTF gere os tokens CSRF automaticamente",
        "from flask_wtf import FlaskForm",
        "from wtforms import StringField",
        "",
        "class LoginForm(FlaskForm):",
        "    email    = StringField('Email')",
        "    password = StringField('Password')",
        "",
        "# No template HTML:",
        "# &lt;form method='POST'&gt;",
        "#   {{ form.hidden_tag() }}  &lt;!-- insere o token CSRF --&gt;",
        "#   ...",
        "# &lt;/form&gt;",
    ], s_codigo))
    conteudo.append(espaco)

    conteudo.append(Paragraph(
        "Uma medida complementar é configurar os cookies de sessão com o atributo "
        "SameSite definido como Strict ou Lax. Este atributo instrui o browser a não "
        "enviar o cookie em pedidos originados noutros domínios, cortando o vetor "
        "principal que o CSRF utiliza para se concretizar.",
        s_corpo,
    ))

    conteudo.append(_caixa_codigo([
        "# Configuração dos cookies de sessão em Flask",
        "app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'",
        "app.config['SESSION_COOKIE_SECURE']   = True   # apenas sobre HTTPS",
        "app.config['SESSION_COOKIE_HTTPONLY']  = True   # inacessível ao JavaScript",
    ], s_codigo))
    conteudo.append(espaco)

    # ── Secção 5 — Conclusão ────────────────────────────────────────────────
    conteudo.append(Spacer(1, 0.2 * cm))
    conteudo.append(Paragraph("5. Conclusão", s_seccao))
    conteudo.append(divisor)
    conteudo.append(espaco)

    conteudo.append(Paragraph(
        "A segurança de um sistema não se mede pelo número de proteções implementadas, "
        "mas pela adequação dessas proteções ao contexto real da aplicação. Implementar "
        "tokens CSRF ou políticas de Content Security Policy numa aplicação desktop "
        "seria o equivalente a colocar um cadeado numa porta que não existe.",
        s_corpo,
    ))

    conteudo.append(Paragraph(
        "Este projeto implementou as proteções que fazem sentido para uma aplicação "
        "desktop com acesso direto a base de dados: validação e sanitização de todos "
        "os inputs do utilizador, proteção contra injeção SQL através de prepared "
        "statements, armazenamento de passwords com hash bcrypt, controlo de tentativas "
        "de login com bloqueio temporário, gestão de sessão com expiração por "
        "inatividade, e logging de eventos de segurança para monitorização.",
        s_corpo,
    ))

    conteudo.append(Paragraph(
        "Caso este projeto evoluísse para uma plataforma web, as proteções XSS e CSRF "
        "descritas neste documento seriam obrigatórias e deveriam ser implementadas "
        "desde o primeiro dia de desenvolvimento, preferencialmente através de "
        "bibliotecas maduras como Flask-WTF, que automatizam grande parte da "
        "complexidade envolvida.",
        s_corpo,
    ))

    doc.build(conteudo)
    print(f"PDF gerado com sucesso: {caminho}")


if __name__ == "__main__":
    gerar()
