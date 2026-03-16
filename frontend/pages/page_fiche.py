import streamlit as st
import json
from frontend.translations import t
from frontend.components.input_form import render_curriculum_form
from backend.services.fiche_service import generate_fiche
from backend.database.db_manager import save_to_archive
from backend.exporters.pdf_exporter import export_fiche_pdf
from backend.utils.rate_limit import check_rate_limit, remaining_wait

DOMAINES = [
    "Compréhension de l'écrit",
    "Production écrite", 
    "Compréhension de l'oral",
    "Production orale",
    "Points de langue"
]

def render_page_fiche():
    st.title(t("fiche_title"))
    st.caption(t("fiche_subtitle"))
    
    form_data = render_curriculum_form(form_key="fiche_prep_form")
    
    # Sélection du domaine
    domaine = st.selectbox(t("fiche_domaine_label"), DOMAINES)
    
    col_gen, col_regen = st.columns(2)
    
    with col_gen:
        gen_clicked = st.button(t("btn_generate"), use_container_width=True, type="primary")
    with col_regen:
        regen_clicked = st.button(t("fiche_btn_regen"), use_container_width=True, 
                                   disabled=("fiche_result" not in st.session_state))
    
    # Génération
    if gen_clicked and form_data:
        if not check_rate_limit("fiche_gen"):
            wait = remaining_wait("fiche_gen")
            st.warning(t("limit_reached", wait=wait))
        else:
            with st.spinner(t("gen_spinner")):
                try:
                    p = form_data
                    result = generate_fiche(p["niveau"], p["projet_num"], p["sequence_num"], domaine)
                    st.session_state["fiche_result"] = result
                    from backend.utils.draft_manager import add_draft
                    add_draft("fiche", result)
                except Exception as e:
                    st.error(t("gen_error"))
    
    # Régénération (sans cache)
    if regen_clicked and form_data:
        if not check_rate_limit("fiche_gen"):
            wait = remaining_wait("fiche_gen")
            st.warning(t("limit_reached", wait=wait))
        else:
            with st.spinner(t("regen_spinner")):
                try:
                    p = form_data
                    result = generate_fiche(p["niveau"], p["projet_num"], p["sequence_num"], domaine, use_cache=False)
                    st.session_state["fiche_result"] = result
                except Exception:
                    st.error(t("regen_error"))
                    
    # UI Brouillons
    from backend.utils.draft_manager import render_drafts_ui
    render_drafts_ui("fiche", "fiche_result")
    
    # Affichage du résultat
    if "fiche_result" in st.session_state:
        fiche = st.session_state["fiche_result"]
        _render_fiche(fiche)
    else:
        st.info(t("fiche_no_params"))


def _render_fiche(fiche: dict):
    """Affiche la fiche de préparation de manière structurée et professionnelle."""
    
    # ── En-tête ──────────────────────────────────────────────
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(79,139,249,0.15), rgba(0,191,165,0.1)); 
                border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; 
                border: 1px solid rgba(79,139,249,0.2);">
        <h2 style="color: #4F8BF9; margin: 0 0 0.5rem 0;">📋 {fiche.get('titre', 'Fiche de Préparation')}</h2>
        <div style="display: flex; gap: 20px; flex-wrap: wrap; color: #aaa; font-size: 0.9rem;">
            <span>📚 <b>{fiche.get('niveau', '')}</b></span>
            <span>📂 {fiche.get('projet', '')}</span>
            <span>📝 {fiche.get('sequence', '')}</span>
            <span>⏱️ {fiche.get('duree_totale', '')}</span>
            <span>🎯 {fiche.get('domaine', '')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ── Compétences ──────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{t('fiche_comp_terminale')}**")
        st.info(fiche.get("competence_terminale", ""))
    with col2:
        st.markdown(f"**{t('fiche_comp_transversale')}**")
        st.info(fiche.get("competence_transversale", ""))
    
    # ── Objectifs ────────────────────────────────────────────
    with st.expander(t("fiche_objectifs_title"), expanded=True):
        objectifs = fiche.get("objectifs_apprentissage", [])
        for obj in objectifs:
            st.markdown(f"- ✅ {obj}")
    
    # ── Prérequis ────────────────────────────────────────────
    with st.expander(t("fiche_prerequis_title")):
        prerequis = fiche.get("prerequis", [])
        for pr in prerequis:
            st.markdown(f"- 📌 {pr}")
    
    # ── Matériel ─────────────────────────────────────────────
    with st.expander(t("fiche_materiel_title")):
        materiel = fiche.get("materiel_didactique", [])
        for m in materiel:
            st.markdown(f"- 🧰 {m}")
        st.markdown(f"\n**{t('fiche_support_label')}:** {fiche.get('support_pedagogique', '')}")
    
    # ── Déroulement de la séance (étapes) ────────────────────
    st.markdown(f"### {t('fiche_deroulement_title')}")
    
    etapes = fiche.get("etapes", [])
    for i, etape in enumerate(etapes):
        with st.expander(f"**{i+1}. {etape.get('nom_etape', '')}** — ⏱️ {etape.get('duree', '')}", expanded=(i == 0)):
            st.markdown(f"**🎯 {t('fiche_objectif_etape')}:** {etape.get('objectif_etape', '')}")
            
            col_ens, col_eleve = st.columns(2)
            with col_ens:
                st.markdown(f"""
                <div style="background: rgba(79,139,249,0.08); border-radius: 10px; padding: 1rem; 
                            border-left: 3px solid #4F8BF9;">
                    <p style="color: #4F8BF9; font-weight: 600; margin: 0 0 0.5rem 0;">👨‍🏫 {t('fiche_activite_enseignant')}</p>
                    <p style="color: #ccc; margin: 0;">{etape.get('activite_enseignant', '')}</p>
                </div>
                """, unsafe_allow_html=True)
            with col_eleve:
                st.markdown(f"""
                <div style="background: rgba(0,191,165,0.08); border-radius: 10px; padding: 1rem; 
                            border-left: 3px solid #00bfa5;">
                    <p style="color: #00bfa5; font-weight: 600; margin: 0 0 0.5rem 0;">👨‍🎓 {t('fiche_activite_eleve')}</p>
                    <p style="color: #ccc; margin: 0;">{etape.get('activite_eleve', '')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"📎 **{t('fiche_supports')}:** {etape.get('supports', '')}  |  👥 **{t('fiche_modalite')}:** {etape.get('modalite', '')}")
    
    # ── Évaluation, Remédiation, Prolongement ────────────────
    st.markdown("---")
    col_eval, col_rem, col_pro = st.columns(3)
    with col_eval:
        st.markdown(f"#### 📊 {t('fiche_evaluation')}")
        st.write(fiche.get("evaluation", ""))
    with col_rem:
        st.markdown(f"#### 🔧 {t('fiche_remediation')}")
        st.write(fiche.get("remediation", ""))
    with col_pro:
        st.markdown(f"#### 📝 {t('fiche_prolongement')}")
        st.write(fiche.get("prolongement", ""))
    
    # ── Notes Professeur NADIA ───────────────────────────────
    notes = fiche.get("notes_professeur_nadia", "")
    if notes:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(255,193,7,0.08), rgba(255,152,0,0.05)); 
                    border-radius: 12px; padding: 1rem; margin-top: 1rem;
                    border: 1px solid rgba(255,193,7,0.2);">
            <p style="color: #ffc107; font-weight: 600; margin: 0 0 0.5rem 0;">💡 {t('fiche_notes_nadia')}</p>
            <p style="color: #ccc; margin: 0;">{notes}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # ── Actions ──────────────────────────────────────────────
    st.markdown("---")
    action_cols = st.columns(3)
    
    with action_cols[0]:
        if st.button(t("btn_save"), key="save_fiche", use_container_width=True):
            try:
                meta = fiche.get("_meta", {})
                save_to_archive(
                    content_type="Fiche",
                    niveau=meta.get("niveau", fiche.get("niveau", "")),
                    projet_num=meta.get("projet_num", 0),
                    sequence_num=meta.get("sequence_num", 0),
                    theme=fiche.get("domaine", ""),
                    title=fiche.get("titre", "Fiche de Préparation"),
                    content_json=json.dumps(fiche, ensure_ascii=False)
                )
                st.success(t("save_success"))
            except Exception:
                st.error(t("save_error"))
    
    with action_cols[1]:
        if st.button(t("btn_pdf"), key="pdf_fiche", use_container_width=True):
            try:
                filepath = export_fiche_pdf(fiche, f"fiche_{fiche.get('niveau', '')}_{fiche.get('domaine', '')}.pdf")
                with open(filepath, "rb") as f:
                    st.download_button(
                        "📥 Télécharger PDF", data=f.read(),
                        file_name=f"fiche_{fiche.get('niveau','')}.pdf",
                        mime="application/pdf", use_container_width=True
                    )
            except Exception:
                st.error(t("pdf_error"))
    
    with action_cols[2]:
        from frontend.components.print_helper import inject_print_button
        inject_print_button()
