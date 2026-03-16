import streamlit as st
from frontend.translations import t

def render_page_guide():
    st.title(t("guide_title"))
    st.markdown(t("guide_welcome"))
    st.markdown("---")

    st.subheader(t("guide_what_title"))
    st.info(t("guide_what_desc"))
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        st.markdown(f"### {t('guide_what_1_title')}\n{t('guide_what_1_desc')}")
    with col2:
        st.markdown(f"### {t('guide_what_2_title')}\n{t('guide_what_2_desc')}")
    with col3:
        st.markdown(f"### {t('guide_what_3_title')}\n{t('guide_what_3_desc')}")
    with col4:
        st.markdown(f"### {t('guide_what_4_title')}\n{t('guide_what_4_desc')}")

    st.markdown("---")
    st.subheader(t("guide_how_title"))

    with st.expander(t("guide_step1_title"), expanded=True):
        st.markdown("""
1. Cliquez sur **📝 Texte de Support** / **نص داعم** dans le menu.
2. Sélectionnez le **Niveau**, le **Projet** et la **Séquence**.
3. *(Optionnel)* Entrez un thème ou cliquez sur **🤖 Suggérer un thème** / **اقتراح موضوع**.
4. Cliquez sur **✨ Générer** / **توليد**.
5. Consultez le texte, le vocabulaire clé et les questions de compréhension.
6. Exportez en **PDF** ou **.txt**, ou **💾 Sauvegardez**.
        """)

    with st.expander(t("guide_step2_title")):
        st.markdown("""
1. Cliquez sur **🎯 Situation d'Intégration** / **وضعية إدماجية** dans le menu.
2. Sélectionnez Niveau / Projet / Séquence.
3. Cliquez sur **✨ Générer la situation** / **توليد الوضعية**.
4. Consultez le contexte, la consigne et les critères.
5. Exportez en PDF ou sauvegardez.
        """)

    with st.expander(t("guide_step3_title")):
        st.markdown("""
1. Cliquez sur **📊 Grille d'Évaluation** / **شبكة تقييم** dans le menu.
2. Choisissez le niveau, le type et la compétence.
3. Cliquez sur **✨ Générer la grille** / **توليد الشبكة**.
4. Modifiez les critères si besoin.
5. Téléchargez (PDF ou Excel) ou sauvegardez.
        """)

    with st.expander(t("guide_step4_title")):
        st.markdown("""
1. Cliquez sur **💬 DISCUSSION LIBRE** / **مناقشة حرة** dans le menu.
2. Posez des questions sur l'enseignement à l'Assistant IA (Professeur NADIA).
3. Obtenez des conseils et des idées d'activités.
        """)

    with st.expander(t("guide_step5_title")):
        st.markdown("""
1. Allez dans **📁 Mes Archives** / **أرشيفي**.
2. Filtrez, cherchez, regardez en détail vos historiques de génération.
3. Exportez toutes vos archives en un clic.
        """)

    st.markdown("---")
    st.subheader(t("guide_settings_title"))
    st.markdown(f"🔧 Gérer la langue et la clé API GEMINI dans ce menu.")

    st.markdown("---")
    st.subheader(t("guide_faq_title"))

    with st.expander(t("guide_faq1_q")):
        st.markdown("Oui, 5 à 15 secs selon les serveurs.")

    with st.expander(t("guide_faq2_q")):
        st.markdown("Affiché en lecture seule (copiable). Grilles d'évaluation : éditor intégré.")

    with st.expander(t("guide_faq3_q")):
        st.markdown("Non, cliquez sur Sauvegarder.")

    with st.expander(t("guide_faq4_q")):
        st.markdown("5 générations par minute en moyenne par module.")

    st.markdown("---")
    st.caption(t("footer_text"))
