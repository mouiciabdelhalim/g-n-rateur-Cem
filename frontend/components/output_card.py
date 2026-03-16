import streamlit as st
import html  # ← SECURITY

def render_output_card(title: str, content_html: str = None):
    """Render a styled output card for generated content.

    Args:
        title:        Card heading — automatically HTML-escaped.
        content_html: Pre-formatted HTML body. CALLER is responsible for
                      sanitizing any user/LLM-sourced data BEFORE passing it here.
    """
    # SECURITY FIX: escape the title; it may contain LLM-generated text
    safe_title = html.escape(str(title))

    st.markdown(f"""
    <div style="
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        color: #333;
    ">
        <h3 style="color: #4F8BF9; margin-top: 0;">{safe_title}</h3>
        {content_html if content_html else ''}
    </div>
    """, unsafe_allow_html=True)
