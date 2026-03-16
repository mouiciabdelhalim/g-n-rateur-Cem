import os
import re  # ← SECURITY: for filename sanitization
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from backend.config import EXPORT_DIR

def _ensure_export_dir():
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)


def _safe_filename(filename: str) -> str:
    """
    SECURITY: sanitize caller-supplied filenames to prevent Path Traversal.
    Strips directory components and replaces any character that is not
    alphanumeric, a dot, hyphen, or underscore.
    """
    # 1. Remove any directory components (e.g. '../../etc/passwd' → 'etc/passwd' → 'passwd')
    basename = os.path.basename(filename)
    # 2. Whitelist safe characters only
    safe = re.sub(r'[^\w.\-]', '_', basename)
    if not safe or safe.startswith('.'):
        safe = 'export_output'
    return safe

def _header_footer(canvas, doc):
    canvas.saveState()
    
    # Default font
    canvas.setFont('Helvetica', 10)
    
    # Header
    canvas.drawCentredString(A4[0]/2.0, A4[1]-2*cm, "République Algérienne Démocratique et Populaire")
    canvas.drawCentredString(A4[0]/2.0, A4[1]-2.5*cm, "Ministère de l'Éducation Nationale")
    canvas.line(A4[0]/2.0 - 5*cm, A4[1]-2.7*cm, A4[0]/2.0 + 5*cm, A4[1]-2.7*cm)
    
    # School Info
    canvas.drawString(2*cm, A4[1]-3.5*cm, "Établissement: " + "_"*30)
    canvas.drawCentredString(A4[0]/2.0, A4[1]-3.5*cm, "Année scolaire: " + "_"*20)
    canvas.drawRightString(A4[0]-2*cm, A4[1]-3.5*cm, "Enseignant(e): " + "_"*30)
    
    # Footer
    canvas.setFont('Helvetica', 9)
    canvas.drawCentredString(A4[0]/2.0, 1.5*cm, f"Page {doc.page}")
    
    canvas.restoreState()

def export_texte_pdf(texte_data: dict, output_filename: str) -> str:
    _ensure_export_dir()
    filepath = os.path.join(EXPORT_DIR, _safe_filename(output_filename))  # SECURITY FIX: path traversal
    
    doc = SimpleDocTemplate(
        filepath, 
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=4.5*cm, bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], alignment=1, spaceAfter=20)
    normal_style = styles['Normal']
    normal_style.fontSize = 11
    normal_style.leading = 14
    
    story = []
    
    # Titre
    story.append(Paragraph(texte_data.get('titre', 'Texte de Support'), title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Texte (gérer les retours à la ligne)
    texte = texte_data.get('texte', '').replace('\n', '<br/>')
    story.append(Paragraph(texte, normal_style))
    story.append(Spacer(1, 1*cm))
    
    # Vocabulaire
    vocab = texte_data.get('vocabulaire_cle', [])
    if vocab:
        story.append(Paragraph("<b>Vocabulaire clé:</b>", normal_style))
        story.append(Spacer(1, 0.2*cm))
        for v in vocab:
            story.append(Paragraph(f"• <b>{v.get('mot', '')}</b> : {v.get('definition', '')}", normal_style))
        story.append(Spacer(1, 0.5*cm))
        
    # Questions
    questions = texte_data.get('questions_comprehension', [])
    if questions:
        story.append(Paragraph("<b>Questions de compréhension:</b>", normal_style))
        story.append(Spacer(1, 0.2*cm))
        for i, q in enumerate(questions, 1):
            story.append(Paragraph(f"{i}. {q.get('question', '')}", normal_style))
            story.append(Spacer(1, 1.5*cm)) # Espace pour répondre
    
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return filepath

def export_situation_pdf(situation_data: dict, output_filename: str) -> str:
    _ensure_export_dir()
    filepath = os.path.join(EXPORT_DIR, _safe_filename(output_filename))  # SECURITY FIX: path traversal
    
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=4.5*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=1)
    heading_style = styles['Heading3']
    normal_style = styles['Normal']
    normal_style.fontSize = 11
    normal_style.leading = 14
    
    story = []
    story.append(Paragraph(f"Situation d'Intégration: {situation_data.get('titre', '')}", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph(f"<b>Niveau:</b> {situation_data.get('niveau', '')} &nbsp;&nbsp;&nbsp; <b>Durée:</b> {situation_data.get('duree_estimee', '')}", normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("<b>Contexte:</b>", heading_style))
    story.append(Paragraph(situation_data.get('contexte', '').replace('\n', '<br/>'), normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("<b>Support fourni:</b>", heading_style))
    story.append(Paragraph(situation_data.get('support_fourni', '').replace('\n', '<br/>'), normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("<b>Consigne:</b>", heading_style))
    story.append(Paragraph(situation_data.get('consigne', '').replace('\n', '<br/>'), normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    criteres = situation_data.get('criteres_reussite', [])
    if criteres:
        story.append(Paragraph("<b>Critères de réussite:</b>", heading_style))
        for c in criteres:
            story.append(Paragraph(f"• <b>{c.get('critere', '')}</b>: {c.get('indicateurs', '')}", normal_style))
    
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return filepath

def _build_grille_table(grille_data: dict, header_color, row_colors: list, styles) -> "Table":
    """Construit la table de la grille avec des couleurs personnalisées."""
    table_data = [['Critères', 'Très Satisfaisant', 'Satisfaisant', 'Peu Satisfaisant', 'Insuffisant']]
    criteres = grille_data.get('criteres', [])
    
    for c in criteres:
        nom = Paragraph(f"<b>{c.get('nom', '')}</b><br/><font size=8>{c.get('description', '')}</font>", styles['Normal'])
        niveaux = c.get('niveaux', {})
        exc     = Paragraph(f"{niveaux.get('excellent', {}).get('description', '')}<br/><b>{niveaux.get('excellent', {}).get('points', '')} pts</b>", styles['Normal'])
        bien    = Paragraph(f"{niveaux.get('bien', {}).get('description', '')}<br/><b>{niveaux.get('bien', {}).get('points', '')} pts</b>", styles['Normal'])
        passable= Paragraph(f"{niveaux.get('passable', {}).get('description', '')}<br/><b>{niveaux.get('passable', {}).get('points', '')} pts</b>", styles['Normal'])
        insuff  = Paragraph(f"{niveaux.get('insuffisant', {}).get('description', '')}<br/><b>{niveaux.get('insuffisant', {}).get('points', '')} pts</b>", styles['Normal'])
        table_data.append([nom, exc, bien, passable, insuff])
    
    col_widths = [A4[0]*0.2, A4[0]*0.185, A4[0]*0.185, A4[0]*0.185, A4[0]*0.185]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    base_style = [
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.HexColor('#888888')),
        ('WORDWRAP', (0, 0), (-1, -1), True),
    ]
    
    # Alternating row colors
    for i, row_color in enumerate(row_colors):
        row_idx = i + 1  # skip header
        if row_idx < len(table_data):
            base_style.append(('BACKGROUND', (0, row_idx), (-1, row_idx), row_color))
    
    t.setStyle(TableStyle(base_style))
    return t


# SECURITY: allowed template values — reject anything else to prevent injection
_ALLOWED_TEMPLATES = frozenset({"officiel", "simplifie", "colore"})


def export_grille_pdf(grille_data: dict, output_filename: str, template: str = "officiel") -> str:
    """
    Exporte une grille d'évaluation en PDF.

    template: "officiel" | "simplifie" | "colore"
    """
    # SECURITY FIX: whitelist template parameter
    if template not in _ALLOWED_TEMPLATES:
        template = "officiel"
    _ensure_export_dir()
    filepath = os.path.join(EXPORT_DIR, _safe_filename(output_filename))  # SECURITY FIX: path traversal
    styles = getSampleStyleSheet()

    # ── Configuration par template ────────────────────────────────────────────
    if template == "simplifie":
        header_color   = colors.HexColor('#555555')
        row_colors     = [colors.white, colors.HexColor('#F2F2F2')]
        top_margin     = 2 * cm
        title_color    = '#333333'
        use_inst_header = False
    elif template == "colore":
        header_color   = colors.HexColor('#1B5E20')  # dark green
        row_colors     = [colors.HexColor('#E8F5E9'), colors.HexColor('#FFF9C4')]  # green / yellow alt
        top_margin     = 4.5 * cm
        title_color    = '#1B5E20'
        use_inst_header = True
    else:  # officiel (default)
        header_color   = colors.HexColor('#4F8BF9')
        row_colors     = [colors.white, colors.HexColor('#EEF4FF')]
        top_margin     = 4.5 * cm
        title_color    = '#2C3E50'
        use_inst_header = True

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=top_margin, bottomMargin=2*cm
    )

    title_style = ParagraphStyle(
        'GrilleTitle', parent=styles['Heading1'], alignment=1,
        textColor=colors.HexColor(title_color), spaceAfter=12
    )
    info_style = styles['Normal']

    story = []
    story.append(Paragraph(grille_data.get('titre', "Grille d'évaluation"), title_style))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        f"<b>Niveau:</b> {grille_data.get('niveau', '')} &nbsp;|&nbsp; <b>Type:</b> {grille_data.get('type_production', '')}",
        info_style
    ))
    story.append(Paragraph(f"<b>Compétence:</b> {grille_data.get('competence', '')}", info_style))
    story.append(Spacer(1, 0.5 * cm))

    table = _build_grille_table(grille_data, header_color, row_colors, styles)
    story.append(table)

    # Observations
    observations = grille_data.get('observations', '')
    if observations:
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph(f"<b>Observations:</b> {observations}", info_style))

    on_page = _header_footer if use_inst_header else None
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    return filepath


def export_fiche_pdf(fiche_data: dict, output_filename: str) -> str:
    """Exporte une fiche de préparation en PDF avec le format officiel CEM."""
    _ensure_export_dir()
    filepath = os.path.join(EXPORT_DIR, _safe_filename(output_filename))
    
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                           rightMargin=1.5*cm, leftMargin=1.5*cm,
                           topMargin=4.5*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('FicheTitle', parent=styles['Heading1'], alignment=1,
                                  textColor=colors.HexColor('#2C3E50'), spaceAfter=12)
    heading_style = ParagraphStyle('FicheHeading', parent=styles['Heading3'],
                                    textColor=colors.HexColor('#1B5E20'), spaceBefore=10)
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    normal_style.leading = 13
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=9, leading=11)
    
    story = []
    
    # Titre
    story.append(Paragraph(f"Fiche de Préparation: {fiche_data.get('titre', '')}", title_style))
    story.append(Spacer(1, 0.3*cm))
    
    # Info box
    info_lines = [
        f"<b>Niveau:</b> {fiche_data.get('niveau', '')} &nbsp;|&nbsp; <b>Durée:</b> {fiche_data.get('duree_totale', '')} &nbsp;|&nbsp; <b>Domaine:</b> {fiche_data.get('domaine', '')}",
        f"<b>Projet:</b> {fiche_data.get('projet', '')}",
        f"<b>Séquence:</b> {fiche_data.get('sequence', '')}",
    ]
    for line in info_lines:
        story.append(Paragraph(line, normal_style))
    story.append(Spacer(1, 0.4*cm))
    
    # Compétences
    story.append(Paragraph("<b>Compétence terminale:</b>", heading_style))
    story.append(Paragraph(fiche_data.get('competence_terminale', ''), normal_style))
    story.append(Paragraph(f"<b>Compétence transversale:</b> {fiche_data.get('competence_transversale', '')}", normal_style))
    story.append(Spacer(1, 0.3*cm))
    
    # Objectifs
    story.append(Paragraph("<b>Objectifs d'apprentissage:</b>", heading_style))
    for obj in fiche_data.get('objectifs_apprentissage', []):
        story.append(Paragraph(f"• {obj}", normal_style))
    story.append(Spacer(1, 0.3*cm))
    
    # Prérequis
    prerequis = fiche_data.get('prerequis', [])
    if prerequis:
        story.append(Paragraph("<b>Prérequis:</b>", heading_style))
        for pr in prerequis:
            story.append(Paragraph(f"• {pr}", normal_style))
        story.append(Spacer(1, 0.3*cm))
    
    # Matériel
    story.append(Paragraph("<b>Matériel didactique:</b>", heading_style))
    for m in fiche_data.get('materiel_didactique', []):
        story.append(Paragraph(f"• {m}", normal_style))
    story.append(Paragraph(f"<b>Support:</b> {fiche_data.get('support_pedagogique', '')}", normal_style))
    story.append(Spacer(1, 0.4*cm))
    
    # Déroulement — Table
    story.append(Paragraph("<b>Déroulement de la séance:</b>", heading_style))
    story.append(Spacer(1, 0.2*cm))
    
    table_data = [['Étape', 'Durée', 'Activité enseignant', 'Activité élève', 'Modalité']]
    for etape in fiche_data.get('etapes', []):
        table_data.append([
            Paragraph(f"<b>{etape.get('nom_etape', '')}</b>", small_style),
            Paragraph(etape.get('duree', ''), small_style),
            Paragraph(etape.get('activite_enseignant', ''), small_style),
            Paragraph(etape.get('activite_eleve', ''), small_style),
            Paragraph(etape.get('modalite', ''), small_style),
        ])
    
    col_widths = [A4[0]*0.14, A4[0]*0.08, A4[0]*0.30, A4[0]*0.30, A4[0]*0.12]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B5E20')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#888888')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#E8F5E9')),
        ('BACKGROUND', (0, 2), (-1, 2), colors.white),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#E8F5E9')),
        ('BACKGROUND', (0, 4), (-1, 4), colors.white),
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#E8F5E9')),
        ('BACKGROUND', (0, 6), (-1, 6), colors.white),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4*cm))
    
    # Évaluation, Remédiation, Prolongement
    eval_text = fiche_data.get('evaluation', '')
    rem_text = fiche_data.get('remediation', '')
    pro_text = fiche_data.get('prolongement', '')
    
    if eval_text:
        story.append(Paragraph(f"<b>Évaluation:</b> {eval_text}", normal_style))
    if rem_text:
        story.append(Paragraph(f"<b>Remédiation:</b> {rem_text}", normal_style))
    if pro_text:
        story.append(Paragraph(f"<b>Prolongement:</b> {pro_text}", normal_style))
    
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return filepath

def export_exercices_pdf(exercices_data: dict, output_filename: str) -> str:
    """Exporte une fiche d'exercices en PDF."""
    _ensure_export_dir()
    filepath = os.path.join(EXPORT_DIR, _safe_filename(output_filename))
    
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                           rightMargin=1.5*cm, leftMargin=1.5*cm,
                           topMargin=4.5*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('ExoTitle', parent=styles['Heading1'], alignment=1,
                                  textColor=colors.HexColor('#2C3E50'), spaceAfter=15)
    heading_style = ParagraphStyle('ExoHeading', parent=styles['Heading3'],
                                    textColor=colors.HexColor('#1B5E20'), spaceBefore=10, spaceAfter=5)
    normal_style = styles['Normal']
    normal_style.fontSize = 11
    normal_style.leading = 14
    
    story = []
    
    # Titre
    story.append(Paragraph(f"{exercices_data.get('titre', 'Exercices')}", title_style))
    story.append(Spacer(1, 0.3*cm))
    
    # Info
    niveau = exercices_data.get('niveau', '')
    theme = exercices_data.get('theme', '')
    info_text = f"<b>Niveau:</b> {niveau}"
    if theme:
         info_text += f" &nbsp;|&nbsp; <b>Thème:</b> {theme}"
    story.append(Paragraph(info_text, normal_style))
    story.append(Spacer(1, 1*cm))
    
    # Exercices
    exercices_list = exercices_data.get('exercices', [])
    for i, exo in enumerate(exercices_list, 1):
        # Type & Consigne
        story.append(Paragraph(f"<b>Exercice {i} :</b> {exo.get('consigne', '')}", heading_style))
        story.append(Spacer(1, 0.2*cm))
        
        # Contenu
        contenu = exo.get('contenu', '').replace('\\n', '<br/>')
        story.append(Paragraph(contenu, normal_style))
        story.append(Spacer(1, 1*cm)) # Espace pour que l'élève réponde
        
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return filepath

