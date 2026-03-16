"""
design.py — Reusable CSS injection helpers for the CEM Generator Streamlit app.

Usage (in any page):
    from frontend.components.design import apply_global_styles, inject_footer

    apply_global_styles()   # Call once at the top of each page
    inject_footer()         # Call once at the bottom of each page
"""

import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
# 1. GLOBAL STYLES  (buttons + inputs + general polish + mobile responsive)
# ─────────────────────────────────────────────────────────────────────────────

def apply_global_styles() -> None:
    """
    Inject global CSS into the Streamlit app.

    Covers:
    * Buttons  — dark base, teal glow on hover, press-down on active
    * Text inputs  — subtle teal border on hover / focus
    * Select boxes — same treatment as text inputs
    * Mobile @media queries — stacks columns, enlarges touch targets
    """
    lang = st.session_state.get("lang", "fr")
    direction = "rtl" if lang == "ar" else "ltr"
    align = "right" if lang == "ar" else "left"
    
    dynamic_css = f"""
    <style>
    /* ── Direction Support ─────────────────────────────────────────── */
    .stApp {{
        direction: {direction};
        text-align: {align};
    }}
    /* Handle Streamlit elements RTL alignment */
    .stMarkdown, .stText, .stButton button, .stDownloadButton button, .stSelectbox label, .stTextInput label, .stSlider label {{
        text-align: {align} !important;
    }}
    </style>
    """
    st.markdown(dynamic_css, unsafe_allow_html=True)
    
    static_css = """
    <style>
    /* ── Google Font ───────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500&family=Inter:wght@300;400;500;600&display=swap');

    /* ── Root tokens ──────────────────────────────────────────────── */
    :root {
        --color-primary:      #00bfa5;
        --color-primary-glow: rgba(0, 191, 165, 0.40);
        --color-bg-btn:       #1e1e2e;
        --color-border:       #2e2e3e;
        --color-text-btn:     #e0e0e0;
        --radius:             8px;
        --transition:         0.22s ease;
    }

    /* ── Streamlit Buttons ────────────────────────────────────────── */
    div.stButton > button {
        background-color : var(--color-bg-btn)  !important;
        color            : var(--color-text-btn) !important;
        border           : 1px solid var(--color-border) !important;
        border-radius    : var(--radius)         !important;
        padding          : 0.45rem 1.1rem        !important;
        font-family      : 'Inter', sans-serif   !important;
        font-weight      : 500                   !important;
        letter-spacing   : 0.03em                !important;
        box-shadow       : 0 2px 6px rgba(0,0,0,0.35) !important;
        transition       : transform var(--transition),
                           box-shadow var(--transition),
                           border-color var(--transition) !important;
        cursor           : pointer               !important;
    }

    div.stButton > button:hover {
        transform    : translateY(-3px)             !important;
        border-color : var(--color-primary)          !important;
        box-shadow   : 0 6px 20px var(--color-primary-glow) !important;
        color        : var(--color-primary)          !important;
    }

    div.stButton > button:active {
        transform  : translateY(1px)               !important;
        box-shadow : 0 2px 8px var(--color-primary-glow) !important;
    }

    /* ── Text Inputs ──────────────────────────────────────────────── */
    div[data-baseweb="input"] input,
    div.stTextInput > div > div > input {
        background-color : #12121f                !important;
        border           : 1px solid var(--color-border) !important;
        border-radius    : var(--radius)          !important;
        color            : #e0e0e0                !important;
        transition       : border-color var(--transition),
                           box-shadow  var(--transition) !important;
        font-family      : 'Inter', sans-serif    !important;
    }

    div[data-baseweb="input"] input:hover,
    div.stTextInput > div > div > input:hover,
    div[data-baseweb="input"] input:focus,
    div.stTextInput > div > div > input:focus {
        border-color : var(--color-primary)       !important;
        box-shadow   : 0 0 0 2px rgba(0,191,165,0.20) !important;
        outline      : none                       !important;
    }

    /* ── Select Boxes ─────────────────────────────────────────────── */
    div[data-baseweb="select"] > div {
        background-color : #12121f               !important;
        border           : 1px solid var(--color-border) !important;
        border-radius    : var(--radius)         !important;
        transition       : border-color var(--transition),
                           box-shadow  var(--transition) !important;
        font-family      : 'Inter', sans-serif   !important;
    }

    div[data-baseweb="select"] > div:hover {
        border-color : var(--color-primary)      !important;
        box-shadow   : 0 0 0 2px rgba(0,191,165,0.20) !important;
    }

    /* ── Text Area ────────────────────────────────────────────────── */
    div.stTextArea textarea {
        background-color : #12121f               !important;
        border           : 1px solid var(--color-border) !important;
        border-radius    : var(--radius)         !important;
        color            : #e0e0e0               !important;
        transition       : border-color var(--transition) !important;
        font-family      : 'Inter', sans-serif   !important;
    }

    div.stTextArea textarea:hover,
    div.stTextArea textarea:focus {
        border-color : var(--color-primary)      !important;
        box-shadow   : 0 0 0 2px rgba(0,191,165,0.20) !important;
        outline      : none                      !important;
    }

    /* ════════════════════════════════════════════════════════════════
       MOBILE RESPONSIVE  ≤ 768 px
       Streamlit renders st.columns() as flex children.
       Setting width/flex on [data-testid="column"] forces vertical stacking.
    ════════════════════════════════════════════════════════════════ */
    @media (max-width: 768px) {

        /* Stack ALL Streamlit columns vertically */
        [data-testid="column"] {
            width     : 100% !important;
            min-width : 100% !important;
            flex      : 1 1 100% !important;
        }

        /* Tighter page padding */
        .block-container {
            padding-left   : 0.75rem !important;
            padding-right  : 0.75rem !important;
            padding-top    : 1rem    !important;
            padding-bottom : 4rem    !important;
        }

        /* Bigger touch targets (WCAG AA minimum: 44px) */
        div.stButton > button {
            min-height : 44px      !important;
            font-size  : 1rem      !important;
            padding    : 0.6rem 1rem !important;
        }

        /* No hover lift on touch — avoids stuck states on mobile */
        div.stButton > button:hover {
            transform : none !important;
        }

        /* Larger inputs for on-screen keyboard */
        div[data-baseweb="input"] input,
        div.stTextInput > div > div > input,
        div.stTextArea textarea {
            font-size  : 1rem !important;
            min-height : 44px !important;
        }

        /* Scale headings down gracefully */
        h1 { font-size: 1.5rem  !important; }
        h2 { font-size: 1.25rem !important; }
        h3 { font-size: 1.1rem  !important; }

        /* Larger sidebar nav buttons for thumb taps */
        [data-testid="stSidebar"] div.stButton > button {
            font-size  : 0.95rem !important;
            min-height : 48px    !important;
        }

        /* Metric cards — full row width */
        [data-testid="stMetric"] {
            width : 100% !important;
        }

        /* Dataframes — horizontal scroll inside, no page overflow */
        [data-testid="stDataFrame"] {
            overflow-x : auto !important;
        }

        /* Download buttons — full width */
        div.stDownloadButton > button {
            min-height : 44px !important;
            width      : 100% !important;
        }
    }

    /* ── Very small screens ≤ 480 px ─────────────────────────────── */
    @media (max-width: 480px) {

        /* Remove fixed footer — takes precious vertical space */
        .cem-footer { display: none !important; }

        h1 { font-size: 1.3rem !important; }

        [data-testid="stExpander"] {
            margin-bottom : 0.5rem !important;
        }
    }
    </style>
    """
    st.markdown(static_css, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 2. FOOTER
# ─────────────────────────────────────────────────────────────────────────────

def inject_footer() -> None:
    """
    Inject a fixed bottom footer with the creator credit.

    The footer is:
    * Fixed to the viewport bottom so it persists while scrolling
    * Muted / low-contrast to not distract from the main content
    * Hidden automatically on very small screens (< 480 px via CSS)
    """
    footer_html = """
    <style>
    .cem-footer {
        position         : fixed;
        bottom           : 0;
        left             : 0;
        width            : 100%;
        text-align       : center;
        padding          : 10px 0;
        font-family      : 'JetBrains Mono', 'Courier New', monospace;
        font-size        : 0.72rem;
        font-weight      : 300;
        letter-spacing   : 0.18em;
        color            : #4a4a6a;
        background       : transparent;
        pointer-events   : none;
        z-index          : 9999;
        text-transform   : uppercase;
        transition       : color 0.3s ease;
    }

    .cem-footer:hover {
        color : #7a7a9a;
    }
    </style>

    <div class="cem-footer">
        &#10022; &nbsp; CREATED BY HALIM MOUICI &nbsp; &#10022;
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 3. OPTIONAL — page-level padding tweak (tighter layout for dense pages)
# ─────────────────────────────────────────────────────────────────────────────

def set_page_container_style(max_width_px: int = 1100, padding_top_rem: float = 2.0) -> None:
    """
    Constrain the main content block width and adjust top padding.

    On mobile (< 768px) the CSS media query in apply_global_styles()
    overrides these values automatically with tighter mobile padding.

    Args:
        max_width_px:    Maximum content width in pixels (default 1100).
        padding_top_rem: Top padding in rem units (default 2.0).
    """
    st.markdown(
        f"""
        <style>
        .block-container {{
            max-width        : {max_width_px}px !important;
            padding-top      : {padding_top_rem}rem !important;
            padding-bottom   : 4rem !important;
            padding-left     : 1.5rem !important;
            padding-right    : 1.5rem !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
