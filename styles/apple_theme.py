"""
SmartRoad AI — Apple Design System Styles
Implements macOS Sequoia & Apple Human Interface Guidelines aesthetic.
"""

APPLE_THEME_CSS = """
<style>
/* -------------------------------------------------------------
   SMARTROAD AI — APPLE DESIGN SYSTEM (macOS Sequoia Inspired)
   ------------------------------------------------------------- */

/* Root CSS Variables */
:root {
    --sr-bg-primary: #FFFFFF;
    --sr-bg-secondary: #F5F5F7;
    --sr-bg-sidebar: #FAFAFC;
    --sr-text-primary: #1D1D1F;
    --sr-text-secondary: #6E6E73;
    --sr-text-tertiary: #86868B;
    --sr-accent: #0071E3;
    --sr-accent-hover: #0077ED;
    --sr-accent-light: rgba(0, 113, 227, 0.08);
    --sr-success: #248A3D;
    --sr-success-bg: #EAF6ED;
    --sr-warning: #B87900;
    --sr-warning-bg: #FEF7E6;
    --sr-critical: #D70015;
    --sr-critical-bg: #FEECEB;
    --sr-border: #D2D2D7;
    --sr-border-light: #E5E5EA;
    --sr-radius-sm: 8px;
    --sr-radius-md: 12px;
    --sr-radius-lg: 16px;
    --sr-shadow-subtle: 0 1px 3px rgba(0, 0, 0, 0.04), 0 4px 12px rgba(0, 0, 0, 0.02);
    --sr-shadow-card: 0 2px 8px rgba(0, 0, 0, 0.04);
    --sr-shadow-hover: 0 4px 16px rgba(0, 0, 0, 0.08);
    --sr-font-stack: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter", "Segoe UI", sans-serif;
}

/* Global Typography & Background */
html, body, [class*="css"], .stApp {
    font-family: var(--sr-font-stack) !important;
    color: var(--sr-text-primary) !important;
    background-color: var(--sr-bg-secondary) !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Hide Streamlit default header decoration, footer, and automatic multi-page nav */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {background-color: transparent !important;}

/* Completely eliminate Streamlit's default page menu & header from the top of the sidebar */
div[data-testid="stSidebarNav"],
section[data-testid="stSidebar"] div[data-testid="stSidebarNav"],
ul[data-testid="stSidebarNavItems"],
div[data-testid="stSidebarNavSeparator"],
div[data-testid="stSidebarHeader"] {
    display: none !important;
    height: 0px !important;
    margin: 0px !important;
    padding: 0px !important;
    visibility: hidden !important;
}

/* Ensure sidebar starts at the absolute top of the screen */
section[data-testid="stSidebar"] {
    background-color: var(--sr-bg-sidebar) !important;
    border-right: 1px solid var(--sr-border-light) !important;
    box-shadow: none !important;
    width: 265px !important;
}

section[data-testid="stSidebar"] > div:first-child,
div[data-testid="stSidebarContent"],
div[data-testid="stSidebarUserContent"] {
    padding-top: 0.45rem !important;
    padding-left: 0.85rem !important;
    padding-right: 0.85rem !important;
}

/* Container adjustments */
.block-container {
    padding-top: 1.25rem !important;
    padding-bottom: 3rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1400px !important;
}

/* Apple-style Buttons with Magical Sliding and Spring Touch */
.stButton > button {
    font-family: var(--sr-font-stack) !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 0.52rem 1.15rem !important;
    border-radius: var(--sr-radius-sm) !important;
    border: 1px solid var(--sr-border) !important;
    background-color: var(--sr-bg-primary) !important;
    color: var(--sr-text-primary) !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
    position: relative;
    overflow: hidden;
}

.stButton > button:hover {
    border-color: var(--sr-accent) !important;
    color: var(--sr-accent) !important;
    background-color: #FAFAFC !important;
    box-shadow: 0 6px 18px rgba(0, 113, 227, 0.18) !important;
    transform: translateY(-2px);
}

.stButton > button:active {
    transform: translateY(0px) scale(0.97) !important;
    box-shadow: 0 1px 3px rgba(0, 113, 227, 0.25) !important;
}

/* Sidebar navigation buttons with sliding pill indicator */
section[data-testid="stSidebar"] .stButton > button {
    text-align: left !important;
    justify-content: flex-start !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    border-radius: 10px !important;
    padding: 0.5rem 0.85rem !important;
    font-size: 13.5px !important;
    color: #48484A !important;
    box-shadow: none !important;
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: rgba(0, 113, 227, 0.08) !important;
    color: var(--sr-accent) !important;
    transform: translateX(6px) !important;
    padding-left: 1.05rem !important;
    box-shadow: 0 2px 8px rgba(0, 113, 227, 0.1) !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background-color: rgba(0, 113, 227, 0.12) !important;
    color: var(--sr-accent) !important;
    font-weight: 600 !important;
    border: 1px solid rgba(0, 113, 227, 0.22) !important;
    box-shadow: 0 2px 8px rgba(0, 113, 227, 0.1) !important;
    border-left: 4px solid var(--sr-accent) !important;
}

/* Primary Action Buttons */
.stButton > button[kind="primary"], .apple-btn-primary {
    background-color: var(--sr-accent) !important;
    color: #FFFFFF !important;
    border: 1px solid var(--sr-accent) !important;
    box-shadow: 0 1px 3px rgba(0, 113, 227, 0.25) !important;
}

.stButton > button[kind="primary"]:hover, .apple-btn-primary:hover {
    background-color: var(--sr-accent-hover) !important;
    border-color: var(--sr-accent-hover) !important;
    color: #FFFFFF !important;
    box-shadow: 0 6px 22px rgba(0, 113, 227, 0.42) !important;
    transform: translateY(-2px) scale(1.015);
}
}

/* Form Inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div > div,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    font-family: var(--sr-font-stack) !important;
    border-radius: var(--sr-radius-sm) !important;
    border: 1px solid var(--sr-border) !important;
    background-color: var(--sr-bg-primary) !important;
    color: var(--sr-text-primary) !important;
    font-size: 14px !important;
    transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--sr-accent) !important;
    box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.18) !important;
}

/* Cards & Panels with Magical Apple Hover & Lift */
.apple-card {
    background-color: var(--sr-bg-primary);
    border: 1px solid var(--sr-border-light);
    border-radius: var(--sr-radius-md);
    padding: 1.25rem 1.5rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
    transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.28s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.28s ease;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}

.apple-card:hover {
    border-color: rgba(0, 113, 227, 0.4);
    box-shadow: 0 16px 36px rgba(0, 113, 227, 0.12), 0 4px 12px rgba(0, 0, 0, 0.04);
    transform: translateY(-5px) scale(1.008);
}

.apple-card img {
    transition: transform 0.38s cubic-bezier(0.16, 1, 0.3, 1);
}

.apple-card:hover img {
    transform: scale(1.04);
}

.apple-hero-logo {
    transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.apple-hero-logo:hover {
    transform: scale(1.06) rotate(1.5deg) !important;
    box-shadow: 0 16px 38px rgba(0, 113, 227, 0.45) !important;
}

.apple-card-flat {
    background-color: var(--sr-bg-primary);
    border: 1px solid var(--sr-border-light);
    border-radius: var(--sr-radius-md);
    padding: 1.25rem 1.5rem;
    box-shadow: none;
    margin-bottom: 1rem;
}

/* Metric Display Cards */
.apple-stat-card {
    background: #FFFFFF;
    border: 1px solid var(--sr-border-light);
    border-radius: var(--sr-radius-md);
    padding: 1.2rem 1.35rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 110px;
    transition: transform 0.26s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.26s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.26s ease;
}

.apple-stat-card:hover {
    transform: translateY(-4px) scale(1.012);
    border-color: rgba(0, 113, 227, 0.35);
    box-shadow: 0 10px 28px rgba(0, 113, 227, 0.12), 0 3px 8px rgba(0, 0, 0, 0.04);
}

.apple-stat-title {
    font-size: 13px;
    font-weight: 500;
    color: var(--sr-text-secondary);
    letter-spacing: -0.01em;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}

.apple-stat-value {
    font-size: 32px;
    font-weight: 600;
    letter-spacing: -0.03em;
    color: var(--sr-text-primary);
    line-height: 1.1;
    margin-bottom: 4px;
}

.apple-stat-subtitle {
    font-size: 12px;
    color: var(--sr-text-tertiary);
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Badge Pills */
.apple-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 9px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: -0.01em;
    line-height: 1.3;
}

.apple-badge-critical {
    background-color: var(--sr-critical-bg);
    color: var(--sr-critical);
    border: 1px solid rgba(215, 0, 21, 0.18);
}

.apple-badge-warning {
    background-color: var(--sr-warning-bg);
    color: var(--sr-warning);
    border: 1px solid rgba(184, 121, 0, 0.18);
}

.apple-badge-success {
    background-color: var(--sr-success-bg);
    color: var(--sr-success);
    border: 1px solid rgba(36, 138, 61, 0.18);
}

.apple-badge-accent {
    background-color: var(--sr-accent-light);
    color: var(--sr-accent);
    border: 1px solid rgba(0, 113, 227, 0.18);
}

.apple-badge-neutral {
    background-color: #F0F0F2;
    color: var(--sr-text-secondary);
    border: 1px solid var(--sr-border-light);
}

/* Custom Table Styling */
.apple-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 13.5px;
    background: #FFFFFF;
    border: 1px solid var(--sr-border-light);
    border-radius: var(--sr-radius-md);
    overflow: hidden;
}

.apple-table th {
    background: #FAFAFC;
    color: var(--sr-text-secondary);
    font-weight: 500;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    padding: 10px 16px;
    border-bottom: 1px solid var(--sr-border-light);
    text-align: left;
}

.apple-table td {
    padding: 12px 16px;
    border-bottom: 1px solid #F2F2F5;
    color: var(--sr-text-primary);
    vertical-align: middle;
}

.apple-table tr:last-child td {
    border-bottom: none;
}

.apple-table tr:hover td {
    background-color: #F8F8FA;
}

/* Page Header component */
.apple-header {
    margin-bottom: 1.5rem;
    border-bottom: 1px solid var(--sr-border-light);
    padding-bottom: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}

.apple-header-title {
    font-size: 26px;
    font-weight: 600;
    letter-spacing: -0.025em;
    color: var(--sr-text-primary);
    margin: 0;
    line-height: 1.2;
}

.apple-header-subtitle {
    font-size: 14px;
    color: var(--sr-text-secondary);
    margin-top: 4px;
    margin-bottom: 0;
}

/* Navigation items in sidebar */
.apple-nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    border-radius: var(--sr-radius-sm);
    color: var(--sr-text-secondary);
    font-size: 13.5px;
    font-weight: 500;
    text-decoration: none;
    transition: all 0.15s ease;
    margin-bottom: 2px;
    cursor: pointer;
}

.apple-nav-item:hover {
    background-color: rgba(0, 0, 0, 0.03);
    color: var(--sr-text-primary);
}

.apple-nav-item.active {
    background-color: var(--sr-accent-light);
    color: var(--sr-accent);
    font-weight: 600;
}

/* Code & pre tags */
code {
    font-family: "SF Mono", "Fira Code", Menlo, monospace !important;
    background-color: #EFEFF4 !important;
    color: #1D1D1F !important;
    padding: 2px 5px !important;
    border-radius: 4px !important;
    font-size: 12.5px !important;
}

/* Plotly chart container styling */
.js-plotly-plot .plotly .main-svg {
    background: transparent !important;
}

/* Streamlit Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #EBECEF;
    padding: 3px;
    border-radius: var(--sr-radius-sm);
    width: fit-content;
}

.stTabs [data-baseweb="tab"] {
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    color: var(--sr-text-secondary);
    background-color: transparent;
    border: none;
}

.stTabs [aria-selected="true"] {
    background-color: #FFFFFF !important;
    color: var(--sr-text-primary) !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
    font-weight: 600 !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    display: none;
}
</style>
"""

def inject_apple_theme():
    """Inject Apple design system styles into Streamlit app."""
    import streamlit as st
    st.markdown(APPLE_THEME_CSS, unsafe_allow_html=True)
