"""
print_helper.py — Direct browser print utility for Streamlit pages.

Injects a styled print button and @media print CSS that hides the
Streamlit chrome (sidebar, header, toolbar, action buttons) so only
the content card is printed cleanly.

Usage:
    from frontend.components.print_helper import inject_print_button
    inject_print_button()   # call this after rendering the content to print
"""
import streamlit as st


def inject_print_button(label: str = "🖨️ Imprimer") -> None:
    """
    Inject a print button that calls window.print() and applies
    print-specific CSS to hide non-printable UI elements.

    Args:
        label: Button label text (default: "🖨️ Imprimer").
    """
    st.markdown(f"""
    <style>
    /* ── Print: hide everything except the main content block ── */
    @media print {{
        /* Streamlit chrome */
        [data-testid="stSidebar"],
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stMainMenu"],
        footer,
        .cem-footer,
        /* All Streamlit buttons */
        div.stButton,
        div.stDownloadButton,
        /* Expanders and info boxes below the content */
        div[data-testid="stExpander"],
        div[data-testid="stAlert"],
        [data-testid="stHorizontalBlock"],
        hr {{
            display: none !important;
        }}
        /* Allow the main content block to fill the page */
        .block-container {{
            max-width : 100% !important;
            padding   : 0 !important;
        }}
        /* Force white background */
        body, .stApp {{
            background: white !important;
        }}
    }}

    /* ── Print button styling ── */
    .cem-print-btn {{
        display          : inline-flex;
        align-items      : center;
        gap              : 6px;
        background       : transparent;
        border           : 1px solid #4F8BF9;
        color            : #4F8BF9;
        border-radius    : 8px;
        padding          : 7px 16px;
        font-size        : 0.9rem;
        font-family      : 'Inter', sans-serif;
        cursor           : pointer;
        width            : 100%;
        justify-content  : center;
        transition       : background 0.2s, color 0.2s;
    }}
    .cem-print-btn:hover {{
        background : #4F8BF9;
        color      : white;
    }}
    </style>

    <button class="cem-print-btn" onclick="window.print()">
        {label}
    </button>
    """, unsafe_allow_html=True)
