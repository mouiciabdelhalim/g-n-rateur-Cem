import streamlit as st
import logging
from backend.services.analyse_service import analyze_texte
from backend.utils.file_parser import extract_text_from_file
from frontend.components.input_form import render_curriculum_form
from frontend.translations import t

logger = logging.getLogger(__name__)

def render_page_analyse():
    st.title(t("analyse_title"))
    st.markdown(t("analyse_subtitle"))

    # ── Paramètres du curriculum ──────────────────────────────────────────────
    form_data = render_curriculum_form("analyse")

    # ── Entrée du texte ───────────────────────────────────────────────────────
    # File Uploader
    uploaded_file = st.file_uploader(
        label=t("upload_file_title"),
        type=["pdf", "docx", "txt"],
        help=t("upload_file_title")
    )
    
    extracted_text = ""
    if uploaded_file is not None:
        try:
            extracted_text = extract_text_from_file(uploaded_file)
            st.success(t("upload_file_success"))
        except Exception as e:
            st.error(t("upload_file_error", error=str(e)))
            
    # Text Area
    texte_source = st.text_area(
        label=t("upload_text_ph"),
        height=250,
        value=extracted_text,
        placeholder="Le petit gamin algérien marchait dans la casbah..."
    )

    # ── Bouton d'analyse ──────────────────────────────────────────────────────
    if st.button(t("btn_analyze"), type="primary", use_container_width=True, disabled=not form_data or not texte_source.strip()):
        with st.spinner(t("analyze_spinner")):
            try:
                result = analyze_texte(
                    texte_source=texte_source.strip(),
                    niveau=form_data["niveau"],
                    projet_num=form_data["projet_num"],
                    sequence_num=form_data["sequence_num"],
                    use_cache=True
                )
                st.session_state["current_analyse"] = result
                from backend.utils.draft_manager import add_draft
                add_draft("analyse", result)
            except Exception as exc:
                logger.error("Erreur lors de l'analyse: %s", exc)
                st.error(t("analyze_error"))
                
    # UI Brouillons
    from backend.utils.draft_manager import render_drafts_ui
    render_drafts_ui("analyse", "current_analyse")

    # ── Affichage des résultats ────────────────────────────────────────────────
    st.markdown("---")
    if "current_analyse" in st.session_state:
        res = st.session_state["current_analyse"]
        meta = res.get("_meta", {})

        # 1. Niveau CECR
        st.subheader(t("cefr_level_title"))
        col1, col2 = st.columns(2)
        col1.info(f"**{t('cefr_target')}** {meta.get('cefr_level', '')}")
        col2.success(f"**{t('cefr_estimated')}** {res.get('niveau_cefr_estime', '')}")
        st.write(f"**{t('cefr_justification')} :** {res.get('justification_niveau', '')}")

        st.markdown("<br/>", unsafe_allow_html=True)

        # 2. Vocabulaire extrait
        with st.expander("📖 " + t("vocab_title"), expanded=True):
            for v in res.get("vocabulaire_extrait", []):
                st.markdown(f"- **{v.get('mot')}**: {v.get('definition')}")

        # 3. Questions de compréhension
        with st.expander("❓ " + t("comp_questions_title"), expanded=True):
            for i, q in enumerate(res.get("questions_comprehension", []), 1):
                st.markdown(f"**{i}. {q.get('question')}**")
                st.markdown(f"*↳ {q.get('reponse_attendue')}*")

        # 4. Points grammaticaux
        with st.expander("✏️ " + t("gram_points_title"), expanded=True):
            for g in res.get("points_grammaticaux", []):
                st.markdown(f"- **{g.get('point')}** : {g.get('explication')}")

        # 5. Conseils pédagogiques
        with st.expander(t("pedag_advice_title"), expanded=True):
            st.info(res.get("conseils_pedagogiques", ""))
