import html
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

# Visual system: light zinc neutrals, one desaturated emerald accent, Geist + Geist Mono,
# white cards with hairline borders and diffusion shadows. No glows, no purple, no emoji.
_PANEL = '[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="element-container"] .mc-panel)'
_COLUMN = ':is([data-testid="column"], [data-testid="stColumn"])'

_GLOBAL_CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300..700&family=Geist+Mono:wght@400;500&display=swap');

:root {
  --ease: cubic-bezier(0.16, 1, 0.3, 1);
  --bg: #FDE6C4;
  --bg-2: #F4C886;
  --surface: #FFFFFF;
  --sunken: #FBEBD3;
  --line: rgba(228,228,231,0.8);
  --line-strong: #E4E4E7;
  --text: #18181B;
  --text-2: #3F3F46;
  --muted: #71717A;
  --faint: #A1A1AA;
  --accent: #1F8A63;
  --accent-soft: rgba(31,138,99,0.09);
  --danger: #A8505F;
  --shadow: 0 20px 40px -15px rgba(24,24,27,0.07);
}

/* ---------- Type ---------- */
.stApp, .stApp p, .stApp label, .stApp input, .stApp textarea, .stApp button,
.stApp li, .stApp span:not([class*="material"]), .stApp h1, .stApp h2, .stApp h3, .stApp h4,
[data-baseweb="popover"] li, [data-baseweb="popover"] div {
  font-family: 'Geist', system-ui, sans-serif !important;
}
.stApp { background: linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 100%); color: var(--text); }
.stApp span.mono, .stApp span.mc-mono, .stApp .mono, .stApp .mc-mono { font-family: 'Geist Mono', monospace !important; font-variant-numeric: tabular-nums; }

/* Grain on a fixed, non-interactive layer only */
.stApp::after {
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 50; opacity: 0.025;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
[data-testid="stAppViewContainer"] { background: transparent; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stDecoration"] { display: none; }

.block-container { max-width: 1240px; padding: 7rem 2.5rem 8rem; }
@media (max-width: 767px) { .block-container { padding: 5.5rem 1rem 4rem; } }

/* ---------- Floating nav ---------- */
.mc-nav {
  position: fixed; top: 16px; left: 50%; transform: translateX(-50%); z-index: 999991;
  display: flex; align-items: center; gap: 2px; padding: 6px;
  border-radius: 999px; background: rgba(255,255,255,0.72);
  border: 1px solid var(--line-strong);
  backdrop-filter: blur(18px) saturate(160%); -webkit-backdrop-filter: blur(18px) saturate(160%);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.9), 0 12px 30px -18px rgba(24,24,27,0.18);
}
.mc-nav .brand { display: flex; align-items: center; gap: 9px; padding: 6px 14px 6px 10px; color: var(--text); font-weight: 600; font-size: 14px; letter-spacing: -0.01em; }
.mc-nav .brand svg { display: block; }
.mc-nav a { color: var(--muted) !important; text-decoration: none !important; font-size: 13px; padding: 7px 13px; border-radius: 999px;
  transition: color .3s var(--ease), background-color .3s var(--ease); }
.mc-nav a:hover { color: var(--text) !important; background: var(--sunken); }
@media (max-width: 767px) { .mc-nav a { display: none; } }

/* ---------- Eyebrow + breathing status dot ---------- */
.mc-eyebrow { display: inline-flex; align-items: center; gap: 8px; padding: 5px 12px; border-radius: 999px;
  font-size: 11px !important; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted);
  background: var(--surface); border: 1px solid var(--line-strong); }
.mc-eyebrow b { font-family: 'Geist Mono', monospace !important; font-weight: 500; color: var(--text); letter-spacing: 0; }
.mc-dot { position: relative; width: 6px; height: 6px; border-radius: 99px; background: var(--accent); }
.mc-dot::after { content: ""; position: absolute; inset: 0; border-radius: 99px; background: var(--accent); animation: mc-breathe 2.4s var(--ease) infinite; }
@keyframes mc-breathe { 0% { transform: scale(1); opacity: .5; } 70%, 100% { transform: scale(2.6); opacity: 0; } }

/* ---------- Hero (split: copy left, asset right) ---------- */
.mc-hero { display: grid; grid-template-columns: 1.05fr 1fr; gap: 3.5rem; align-items: center; padding: 1.5rem 0 5.5rem; }
.mc-hero-copy { animation: mc-rise .9s var(--ease) both; }
.mc-hero h1 { font-size: clamp(2.25rem, 4.4vw, 3.75rem) !important; line-height: 1 !important; letter-spacing: -0.045em !important;
  font-weight: 600 !important; margin: 1.5rem 0 1.25rem !important; padding: 0 !important; color: var(--text); }
.mc-hero h1 span { color: var(--faint); }
.mc-hero p.lede { max-width: 52ch; font-size: 1.02rem; line-height: 1.65; color: var(--muted); margin: 0; }
.mc-hero-meta { display: grid; grid-template-columns: repeat(3, auto); justify-content: start; margin-top: 2rem; border-top: 1px solid var(--line-strong); }
.mc-hero-meta div { padding: 14px 22px 0 0; margin-right: 22px; border-right: 1px solid var(--line-strong); }
.mc-hero-meta div:last-child { border-right: none; }
.mc-hero-meta small { display: block; font-size: 11px; color: var(--faint); text-transform: uppercase; letter-spacing: .12em; }
.stApp .mc-hero-meta span { display: block; margin-top: 4px; font-family: 'Geist Mono', monospace !important; font-size: 13px; color: var(--text-2); }
.mc-hero-asset { margin: 0; padding: 1.5rem 1.5rem 1.25rem; border-radius: 2.5rem; background: var(--surface);
  border: 1px solid var(--line); box-shadow: var(--shadow); animation: mc-rise 1s var(--ease) .12s both; }
.mc-hero-asset header { display: flex; justify-content: space-between; align-items: center; padding: 0 .5rem .75rem; }
.mc-hero-asset header span { font-size: 12px; color: var(--muted); }
.mc-hero-asset header b { font-family: 'Geist Mono', monospace !important; font-size: 12px; font-weight: 500; color: var(--text-2); }
.mc-hero-asset svg { display: block; width: 100%; height: auto; }
.mc-hero-asset .draw { stroke-dasharray: 1; stroke-dashoffset: 1; animation: mc-draw 1.8s var(--ease) both; }
.mc-hero-asset .fade { animation: mc-fade 1.2s var(--ease) 1.1s both; }
.mc-hero-asset .pulse { transform-box: fill-box; transform-origin: center; animation: mc-breathe 2.4s var(--ease) 1.6s infinite; }
.mc-hero-asset figcaption { display: flex; justify-content: space-between; padding: .75rem .5rem 0; border-top: 1px solid var(--line); font-size: 12px; color: var(--faint); }
@keyframes mc-draw { to { stroke-dashoffset: 0; } }
@keyframes mc-fade { from { opacity: 0; } to { opacity: 1; } }
.mc-hero h1 a, .mc-section-head h2 a, .mc-results-head h2 a, .mc-empty h3 a { display: none !important; }
@media (max-width: 900px) {
  .mc-hero { grid-template-columns: 1fr; gap: 2.5rem; padding-bottom: 3.5rem; }
  }
@media (max-width: 520px) {
  .mc-hero-meta { grid-template-columns: 1fr; }
  .mc-hero-meta div { border-right: none; margin-right: 0; padding-right: 0; }
}

/* ---------- Panels: white card, hairline, diffusion shadow ---------- */
__PANEL__ {
  padding: 2.5rem !important; border-radius: 2.5rem !important;
  background: var(--surface) !important; border: 1px solid var(--line) !important; box-shadow: var(--shadow);
  animation: mc-rise .8s var(--ease) both;
}
__PANEL__:has(.mc-d1) { animation-delay: 70ms; }
__PANEL__:has(.mc-d2) { animation-delay: 140ms; }
__PANEL__:has(.mc-d3) { animation-delay: 210ms; }
__PANEL__:has(.mc-d4) { animation-delay: 280ms; }
@media (max-width: 767px) { __PANEL__ { padding: 1.5rem 1.25rem !important; border-radius: 1.75rem !important; } }
/* Streamlit sizes children from the column width, not the panel; make them fill the panel instead */
__PANEL__ [data-testid="stVerticalBlock"],
__PANEL__ [data-testid="element-container"],
__PANEL__ [data-testid="element-container"] > div { width: 100% !important; max-width: 100%; }
[data-testid="element-container"]:has(.mc-panel),
[data-testid="element-container"]:has(iframe[title="st.iframe"][height="0"]) { display: none; }
@keyframes mc-rise { from { opacity: 0; transform: translateY(24px); } to { opacity: 1; transform: none; } }

/* ---------- Section heads ---------- */
.mc-section-head { margin-bottom: 0.75rem; scroll-margin-top: 100px; }
.mc-section-head h2 { font-size: 1.45rem !important; font-weight: 600 !important; letter-spacing: -0.03em !important; margin: 1rem 0 0.3rem !important; padding: 0 !important; color: var(--text); }
.mc-section-head p { color: var(--muted); font-size: 0.93rem; margin: 0; max-width: 60ch; }
.mc-results-head { display: grid; grid-template-columns: 1fr auto; align-items: end; gap: 1rem 2rem; padding: 4.5rem 0 1.75rem; scroll-margin-top: 90px; }
.mc-results-head h2 { font-size: clamp(1.75rem, 3vw, 2.5rem) !important; font-weight: 600 !important; letter-spacing: -0.04em !important; line-height: 1.05 !important; margin: 1rem 0 0 !important; padding: 0 !important; }
.mc-results-head h2 span { color: var(--faint); }
.mc-results-head p { color: var(--muted); margin: 0; max-width: 38ch; font-size: .93rem; }
@media (max-width: 767px) { .mc-results-head { grid-template-columns: 1fr; } }

/* ---------- Widgets (label above, helper via tooltip, error below) ---------- */
[data-testid="stWidgetLabel"] p { color: var(--text-2) !important; font-size: 13px !important; font-weight: 500; }
[data-baseweb="select"] > div, [data-testid="stNumberInputContainer"], [data-testid="stDateInput"] [data-baseweb="input"], [data-testid="stTextInput"] [data-baseweb="input"] {
  background: var(--surface) !important; border: 1px solid var(--line-strong) !important; border-radius: 14px !important;
  transition: border-color .3s var(--ease), box-shadow .3s var(--ease);
}
[data-baseweb="select"] > div:hover, [data-testid="stNumberInputContainer"]:hover, [data-testid="stDateInput"] [data-baseweb="input"]:hover { border-color: #D4D4D8 !important; }
[data-baseweb="select"] > div:focus-within, [data-testid="stNumberInputContainer"]:focus-within, [data-testid="stDateInput"] [data-baseweb="input"]:focus-within {
  border-color: rgba(31,138,99,0.55) !important; box-shadow: 0 0 0 4px rgba(31,138,99,0.08) !important; }
[data-baseweb="input"] input, [data-testid="stNumberInputContainer"] input { background: transparent !important; font-family: 'Geist Mono', monospace !important; color: var(--text) !important; }
[data-testid="stNumberInputContainer"] [data-baseweb="input"] { border: none !important; background: transparent !important; }
[data-baseweb="base-input"] { background: transparent !important; }
[data-testid="stNumberInputContainer"] button { background: transparent !important; border-radius: 10px; color: var(--muted); }
[data-testid="stNumberInputContainer"] button:hover { background: var(--sunken) !important; color: var(--text); }
[data-baseweb="tag"] { background: var(--accent-soft) !important; border: 1px solid rgba(31,138,99,0.22); border-radius: 999px !important; max-width: none !important; }
[data-baseweb="tag"] span[title] { max-width: none !important; overflow: visible !important; text-overflow: clip !important; }
.stApp [data-baseweb="tag"] span { color: var(--accent) !important; font-family: 'Geist Mono', monospace !important; font-weight: 500; }
[data-baseweb="popover"] ul { background: var(--surface) !important; border: 1px solid var(--line-strong); border-radius: 16px; box-shadow: var(--shadow); }
[data-testid="stRadio"] label p, [data-testid="stCheckbox"] label p { font-size: 0.93rem !important; color: var(--text) !important; }
[data-testid="stDataFrame"], [data-testid="stDataEditor"] { border-radius: 14px; overflow: hidden; border: 1px solid var(--line-strong); }
[data-testid="stAlert"] > div { background: var(--sunken); border: 1px solid var(--line-strong); border-radius: 14px; color: var(--text-2); }
[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) > div { background: #FBF6F7; border-color: rgba(168,80,95,0.28); }
[data-testid="stAlertContentError"] p { color: var(--danger) !important; }

/* ---------- Primary CTA: pill with nested icon; magnetic wrapper ---------- */
[data-testid="stBaseButton-primary"] {
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  min-height: 58px; padding: 7px 7px 7px 24px !important; border-radius: 999px !important;
  background: var(--text) !important; color: #FAFAFA !important; border: none !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.12), 0 14px 28px -16px rgba(24,24,27,0.45);
  transition: transform .3s var(--ease), background-color .3s var(--ease);
}
[data-testid="stBaseButton-primary"] p { font-size: 15px !important; font-weight: 500; color: #FAFAFA !important; }
[data-testid="stBaseButton-primary"]::after {
  content: ""; flex-shrink: 0; width: 44px; height: 44px; border-radius: 999px;
  background: rgba(255,255,255,0.12) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 16 16' fill='none' stroke='%23FAFAFA' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M4.5 11.5l7-7M5.5 4.5h6v6'/%3E%3C/svg%3E") center / 16px no-repeat;
  transition: transform .3s var(--ease);
}
[data-testid="stBaseButton-primary"]:hover { background: #27272A !important; }
[data-testid="stBaseButton-primary"]:hover::after { transform: translate(2px, -1px) scale(1.05); }
[data-testid="stBaseButton-primary"]:active { transform: scale(0.98); }
[data-testid="stBaseButton-primary"]:disabled { background: #D4D4D8 !important; box-shadow: none; }
[data-testid="stBaseButton-primary"]:disabled p { color: #FAFAFA !important; }
.mc-magnet { transition: transform .5s var(--ease); will-change: transform; }

/* ---------- Dashboard (DetailHeader / DetailTag / Legend / Metric strip) ---------- */
.mc-detail-head { display: flex; flex-wrap: wrap; align-items: flex-start; justify-content: space-between; gap: 12px 20px; }
.mc-detail-head h3 { font-size: 1.05rem !important; font-weight: 500 !important; letter-spacing: -0.01em !important; line-height: 1.5 !important; margin: 0 !important; padding: 0 !important; color: var(--text); }
.mc-detail-head p { margin: 2px 0 0; font-size: 13px; color: var(--muted); max-width: 60ch; }
.mc-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.stApp span.mc-tag { display: inline-flex; align-items: center; gap: 7px; padding: 5px 11px; border-radius: 999px; font-size: 12px;
  font-family: 'Geist Mono', monospace !important; color: var(--text-2); background: var(--sunken); border: 1px solid var(--line); white-space: nowrap; }
.mc-tag.pos { color: var(--accent); background: var(--accent-soft); border-color: rgba(31,138,99,0.2); }
.mc-tag svg { display: block; }
.mc-legend { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 20px; margin-top: .35rem; }
.mc-legend span { display: inline-flex; align-items: center; gap: 8px; font-size: 12px; color: var(--muted); }
.mc-legend i { width: 10px; height: 10px; border-radius: 3px; flex-shrink: 0; }
.mc-legend i.dash { width: 14px; height: 0; border-radius: 0; border-top: 2px dashed; background: none !important; }
.mc-rule { height: 1px; background: var(--line-strong); margin: 0.75rem 0 0.25rem; }
.mc-metric h3 { font-size: 13px !important; font-weight: 500 !important; line-height: 1.4 !important; margin: 0 !important; padding: 0 !important; color: var(--muted); }
.mc-metric .v { margin-top: .6rem; font-size: 1.75rem; font-weight: 500; letter-spacing: -0.03em; line-height: 1; font-family: 'Geist Mono', monospace !important; color: var(--text); }
.mc-metric p { margin: 6px 0 0; font-size: 12px; line-height: 1.5; color: var(--muted); }
__COLUMN__:has(.mc-metric) + __COLUMN__:has(.mc-metric) { border-left: 1px solid var(--line-strong); padding-left: 1.5rem; }
@media (max-width: 900px) {
  [data-testid="stHorizontalBlock"]:has(> __COLUMN__ .mc-metric) { flex-wrap: wrap; row-gap: 1.25rem; }
  [data-testid="stHorizontalBlock"]:has(> __COLUMN__ .mc-metric) > __COLUMN__ { flex: 1 1 100% !important; width: 100% !important; min-width: 100% !important; }
  __COLUMN__:has(.mc-metric) + __COLUMN__:has(.mc-metric) { border-left: none; padding-left: 0; border-top: 1px solid var(--line-strong); padding-top: 1.25rem; }
}
__PANEL__:has(.mc-dots) [data-testid="stPlotlyChart"] {
  border-radius: 14px; background-image: radial-gradient(rgba(24,24,27,0.11) 1px, transparent 1px); background-size: 18px 18px;
}
__PANEL__:has(.mc-dots) __COLUMN__:has(.mc-metric) [data-testid="stPlotlyChart"] { background-image: none; }

/* ---------- Tips (collapsed by default; native <details>) ---------- */
.mc-tips { margin: .5rem 0; border-radius: 1.75rem; background: var(--surface); border: 1px solid var(--line); box-shadow: var(--shadow);
  animation: mc-rise .8s var(--ease) both; overflow: hidden; }
.mc-tips summary { list-style: none; cursor: pointer; display: flex; align-items: center; gap: 14px; padding: 1.1rem 1.25rem 1.1rem 1.5rem;
  transition: background-color .3s var(--ease); }
.mc-tips summary::-webkit-details-marker { display: none; }
.mc-tips summary:hover { background: #FFFBF5; }
.mc-tips summary:focus-visible { outline: 2px solid rgba(31,138,99,0.5); outline-offset: -2px; border-radius: 1.75rem; }
.mc-tips summary .t { flex: 1; font-size: .98rem; font-weight: 500; color: var(--text); letter-spacing: -0.01em; }
.mc-tips summary .t small { margin-left: 10px; font-size: 12px; font-weight: 400; color: var(--faint); }
.mc-tips summary .i { flex-shrink: 0; width: 34px; height: 34px; border-radius: 999px; background: var(--sunken); position: relative;
  transition: transform .45s var(--ease), background-color .3s var(--ease); }
.mc-tips summary .i::before, .mc-tips summary .i::after { content: ""; position: absolute; left: 50%; top: 50%; width: 12px; height: 1.5px;
  background: var(--text-2); border-radius: 2px; transform: translate(-50%, -50%); }
.mc-tips summary .i::after { transform: translate(-50%, -50%) rotate(90deg); transition: transform .45s var(--ease); }
.mc-tips[open] summary .i { transform: rotate(180deg); background: var(--accent-soft); }
.mc-tips[open] summary .i::after { transform: translate(-50%, -50%) rotate(0deg); }
.mc-tips-body { padding: .25rem 1.5rem 1.5rem; }
.mc-tips[open] .mc-tips-body { animation: mc-reveal .5s var(--ease) both; }
@keyframes mc-reveal { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: none; } }
.mc-tips-body > small { display: block; margin-top: .75rem; font-size: 12px; color: var(--faint); }
.mc-tips-list { display: grid; grid-template-columns: 1fr 1fr; column-gap: 2rem; }
.mc-tip { display: grid; grid-template-columns: auto 1fr; gap: 14px; padding: 1.1rem 0; border-top: 1px solid var(--line-strong); }
.mc-tip b { font-family: 'Geist Mono', monospace !important; font-size: 12px; font-weight: 500; color: var(--accent); padding-top: 3px; }
.mc-tip h4 { font-size: .95rem !important; font-weight: 600 !important; letter-spacing: -0.01em !important; margin: 0 0 4px !important; padding: 0 !important; color: var(--text); }
.mc-tip p { margin: 0; font-size: .87rem; line-height: 1.55; color: var(--muted); }
.mc-tip h4 a { display: none !important; }
@media (max-width: 767px) {
  .mc-tips-list { grid-template-columns: 1fr; }
  .mc-tips summary .t small { display: block; margin: 2px 0 0; }
}

/* ---------- Empty + loading states ---------- */
.mc-empty { display: grid; grid-template-columns: 1fr 1.2fr; gap: 2.5rem; align-items: center; padding: 2.5rem;
  border-radius: 2.5rem; border: 1px solid var(--line); background: var(--surface); box-shadow: var(--shadow); animation: mc-rise .8s var(--ease) both; }
.mc-empty h3 { font-size: 1.15rem !important; font-weight: 600 !important; letter-spacing: -0.02em !important; margin: 1rem 0 .5rem !important; padding: 0 !important; color: var(--text); }
.mc-empty p { color: var(--muted); font-size: .93rem; line-height: 1.6; margin: 0; max-width: 44ch; }
.mc-empty ol { margin: 1.1rem 0 0; padding: 0; list-style: none; display: grid; gap: 8px; counter-reset: s; }
.mc-empty li { counter-increment: s; display: flex; gap: 10px; font-size: .9rem; color: var(--text-2); }
.mc-empty li::before { content: counter(s, decimal-leading-zero); font-family: 'Geist Mono', monospace; font-size: 12px; color: var(--faint); padding-top: 2px; }
.mc-empty svg { width: 100%; height: auto; display: block; }
.mc-empty.compact { grid-template-columns: 1fr; padding: 1.25rem 1.5rem; border-radius: 1.25rem; margin-top: .25rem; background: var(--sunken); box-shadow: none; }
.mc-empty.compact p { max-width: none; }
@media (max-width: 767px) { .mc-empty { grid-template-columns: 1fr; padding: 1.5rem; border-radius: 1.75rem; } }

.mc-skeleton { display: grid; gap: 14px; }
.mc-skeleton .card { padding: 2.5rem; border-radius: 2.5rem; background: var(--surface); border: 1px solid var(--line); box-shadow: var(--shadow); display: grid; gap: 14px; }
.mc-skeleton .row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.mc-sk { position: relative; overflow: hidden; border-radius: 10px; background: var(--sunken); }
.mc-sk::after { content: ""; position: absolute; inset: 0; transform: translateX(-100%);
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.85), transparent); animation: mc-shimmer 1.3s var(--ease) infinite; }
@keyframes mc-shimmer { to { transform: translateX(100%); } }
@media (max-width: 767px) { .mc-skeleton .row { grid-template-columns: 1fr; } .mc-skeleton .card { padding: 1.5rem; border-radius: 1.75rem; } }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .001ms !important; animation-iteration-count: 1 !important; transition-duration: .001ms !important; }
}
</style>
""".replace('__PANEL__', _PANEL).replace('__COLUMN__', _COLUMN)

_BRAND_MARK = (
    '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M2.5 14.5c3-1 4.5-5 7.5-5.5s4 2.5 7.5-3" stroke="#1F8A63" stroke-width="1.75"/>'
    '<path d="M2.5 14.5c3 .5 5-1.5 7.5-1s4.5 1.5 7.5-.5" stroke="#A1A1AA" stroke-width="1.5"/>'
    '<path d="M2.5 17.5h15" stroke="#D4D4D8" stroke-width="1.5"/></svg>'
)

ICON_UP = ('<svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.75" '
           'stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 11.5l7-7M5.5 4.5h6v6"/></svg>')
ICON_DOWN = ('<svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.75" '
             'stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 4.5l7 7M11.5 5.5v6h-6"/></svg>')

def inject_global_styles():
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)

def render_nav():
    st.markdown(
        f"""
        <nav class="mc-nav">
          <div class="brand">{_BRAND_MARK}Quantile</div>
          <a href="#universe">Assets</a>
          <a href="#allocation">Allocation</a>
          <a href="#simulation">Simulation</a>
          <a href="#results">Results</a>
        </nav>
        """,
        unsafe_allow_html=True,
    )

def _hero_paths_svg(width=480, height=280, n_paths=28, steps=64, seed=11):
    """Real random walks (seeded) so the hero asset shows what the tool actually does."""
    rng = np.random.default_rng(seed)
    returns = rng.normal(0.0009, 0.021, size=(steps, n_paths))
    paths = np.vstack([np.ones(n_paths), np.cumprod(1 + returns, axis=0)])
    median = np.median(paths, axis=1)
    p5, p95 = np.percentile(paths, [5, 95], axis=1)
    lo, hi = paths.min() * 0.98, paths.max() * 1.02
    pad = 8

    def y_of(v):
        return height - pad - (v - lo) / (hi - lo) * (height - 2 * pad)

    def pts(series):
        xs = np.linspace(pad, width - pad, len(series))
        return ' '.join(f'{x:.1f},{y_of(v):.1f}' for x, v in zip(xs, series))

    lines = ''.join(
        f'<polyline class="draw" pathLength="1" points="{pts(paths[:, i])}" fill="none" stroke="#D4D4D8" '
        f'stroke-width="1" style="animation-delay:{i * 28}ms"/>'
        for i in range(n_paths)
    )
    end_x, end_y = width - pad, y_of(median[-1])
    svg = (
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Sample of simulated portfolio paths">'
        f'<line x1="{pad}" x2="{width - pad}" y1="{y_of(1):.1f}" y2="{y_of(1):.1f}" stroke="#E4E4E7" stroke-dasharray="3 5"/>'
        f'{lines}'
        f'<polyline class="fade" points="{pts(p95)}" fill="none" stroke="#71717A" stroke-width="1.25" stroke-dasharray="6 6"/>'
        f'<polyline class="fade" points="{pts(p5)}" fill="none" stroke="#A1A1AA" stroke-width="1.25" stroke-dasharray="2 5"/>'
        f'<polyline class="draw" pathLength="1" points="{pts(median)}" fill="none" stroke="#1F8A63" stroke-width="2.25" '
        f'stroke-linecap="round" style="animation-delay:500ms;animation-duration:2.2s"/>'
        f'<circle class="pulse" cx="{end_x}" cy="{end_y:.1f}" r="5" fill="#1F8A63" opacity=".35"/>'
        f'<circle class="fade" cx="{end_x}" cy="{end_y:.1f}" r="3.5" fill="#1F8A63"/>'
        '</svg>'
    )
    return svg, (median[-1] - 1) * 100

def render_hero():
    svg, median_change = _hero_paths_svg()
    st.markdown(
        f"""
        <section class="mc-hero">
          <div class="mc-hero-copy">
            <span class="mc-eyebrow"><span class="mc-dot"></span>Portfolio simulator</span>
            <h1>Quantify Your Portfolio Risk. <span>Replay Thousands of Market Scenarios.</span></h1>
            <p class="lede">Pick stocks from the S&amp;P&nbsp;500 and decide how to split your money. Quantile learns how those
            stocks moved together, replays thousands of possible years, and shows the median result, the chance of a loss
            and how deep the worst 5% of years go.</p>
            <div class="mc-hero-meta">
              <div><small>Model</small><span>Correlated normal</span></div>
              <div><small>Optimiser</small><span>SLSQP, long-only</span></div>
              <div><small>Risk</small><span>VaR / CVaR 95%</span></div>
            </div>
          </div>
          <figure class="mc-hero-asset">
            <header><span>28 sample paths, 64 trading days</span><b>median {median_change:+.1f}%</b></header>
            {svg}
            <figcaption><span>Illustration, seed 11</span><span>dashed: 5th / 95th percentile</span></figcaption>
          </figure>
        </section>
        """,
        unsafe_allow_html=True,
    )

def panel(dots=False, delay=0):
    """Place as the first element inside st.container(border=True) to render it as a card."""
    classes = 'mc-panel' + (' mc-dots' if dots else '') + (f' mc-d{delay}' if delay else '')
    st.markdown(f'<span class="{classes}"></span>', unsafe_allow_html=True)

def section_head(anchor, index, eyebrow, title, subtitle):
    st.markdown(
        f"""
        <div class="mc-section-head" id="{anchor}">
          <span class="mc-eyebrow"><b>{index}</b>{html.escape(eyebrow)}</span>
          <h2>{html.escape(title)}</h2>
          <p>{html.escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def results_head(num_simulations, time_horizon, note):
    st.markdown(
        f"""
        <div class="mc-results-head" id="results">
          <div>
            <span class="mc-eyebrow"><span class="mc-dot"></span><b>04</b>Results</span>
            <h2>{num_simulations:,} simulated paths, <span>{time_horizon} trading days each.</span></h2>
          </div>
          <p>{html.escape(note)}. Every figure below comes from the spread of simulated outcomes.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

_TIPS = [
    ('Mix stocks that move differently',
     'Stocks from the same industry tend to fall together. Pairing, say, a tech company with a utility or a consumer staple '
     'usually narrows the spread between the 5th and 95th percentile lines.'),
    ('Give the model a rough patch to learn from',
     'Use at least five years of history so the data includes a downturn such as 2020 or 2022. A calm window makes '
     'every simulated future look calmer than it will be.'),
    ('Watch for one stock doing all the work',
     'If a single bar dominates the Return contribution chart, the portfolio is really a bet on that company. '
     'Spreading weight more evenly lowers that single-name risk.'),
    ('Judge by the bad years, not the median',
     'Check the probability of loss and the worst-5% average loss against an amount you could live with. '
     'Optimised weights rely on past returns, so compare them with equal weights before trusting them.'),
]

def render_tips():
    items = ''.join(
        f'<div class="mc-tip"><b>{i:02d}</b><div><h4>{html.escape(title)}</h4><p>{html.escape(body)}</p></div></div>'
        for i, (title, body) in enumerate(_TIPS, start=1)
    )
    st.markdown(
        f"""
        <details class="mc-tips" id="tips">
          <summary>
            <span class="t">Tips for building a sturdier portfolio<small>4 quick checks</small></span>
            <span class="i" aria-hidden="true"></span>
          </summary>
          <div class="mc-tips-body">
            <div class="mc-tips-list">{items}</div>
            <small>General education, not financial advice.</small>
          </div>
        </details>
        """,
        unsafe_allow_html=True,
    )

_EMPTY_CHART = (
    '<svg viewBox="0 0 420 200" fill="none" aria-hidden="true">'
    '<path d="M10 150 H410" stroke="#E4E4E7" stroke-dasharray="3 5"/>'
    '<path d="M10 150 C80 140 120 110 170 104 S270 70 330 52 S390 30 410 26" stroke="#D4D4D8" stroke-width="1.5" stroke-dasharray="6 6"/>'
    '<path d="M10 150 C80 148 130 136 180 132 S280 118 340 108 S395 100 410 98" stroke="#1F8A63" stroke-opacity=".45" stroke-width="2"/>'
    '<path d="M10 150 C80 156 130 166 180 168 S280 172 340 170 S395 168 410 170" stroke="#D4D4D8" stroke-width="1.5" stroke-dasharray="2 5"/>'
    '<rect x="10" y="182" width="70" height="8" rx="4" fill="#FBEBD3"/><rect x="92" y="182" width="50" height="8" rx="4" fill="#FBEBD3"/>'
    '</svg>'
)

def render_results_empty():
    st.markdown(
        f"""
        <div class="mc-empty" id="results">
          <div>
            <span class="mc-eyebrow"><b>04</b>Results</span>
            <h3>No simulation yet</h3>
            <p>Results appear here once you run a simulation: the path of your portfolio over time, the chance of ending
            below what you put in, the size of a bad year, and each stock's yearly returns.</p>
            <ol><li>Pick at least one stock above</li><li>Set weights or let the optimiser choose</li><li>Press Run simulation</li></ol>
          </div>
          {_EMPTY_CHART}
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_tickers_empty():
    st.markdown(
        """
        <div class="mc-empty compact">
          <p>No stocks selected. Search above by company name or ticker, for example Apple, Johnson &amp; Johnson
          or <span class="mc-mono">XOM</span>. Mixing sectors usually lowers the portfolio's overall swings.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def skeleton_html():
    def bar(w, h, extra=''):
        return f'<div class="mc-sk" style="width:{w};height:{h}px;{extra}"></div>'
    return f"""
    <div class="mc-skeleton" aria-busy="true" aria-label="Running simulation">
      <div class="card">
        <div style="display:flex;justify-content:space-between;gap:16px">
          <div style="display:grid;gap:8px;flex:1">{bar('34%', 16)}{bar('58%', 12)}</div>
          {bar('150px', 28, 'border-radius:99px')}
        </div>
        {bar('100%', 320, 'border-radius:14px')}
        <div style="display:grid;grid-template-columns:5fr 4fr 3fr;gap:24px">
          <div style="display:grid;gap:8px">{bar('50%', 12)}{bar('70%', 26)}{bar('100%', 70)}</div>
          <div style="display:grid;gap:8px">{bar('50%', 12)}{bar('60%', 26)}{bar('100%', 70)}</div>
          <div style="display:grid;gap:8px">{bar('50%', 12)}{bar('55%', 26)}{bar('100%', 70)}</div>
        </div>
      </div>
      <div class="row">
        <div class="card">{bar('40%', 16)}{bar('100%', 240, 'border-radius:14px')}</div>
        <div class="card">{bar('46%', 16)}{bar('100%', 240, 'border-radius:14px')}</div>
      </div>
    </div>
    """

_MAGNET_JS = """
<script>
(() => {
  const w = window.parent, doc = w.document;
  if (w.__quantileMagnet) return;
  w.__quantileMagnet = true;
  if (w.matchMedia('(prefers-reduced-motion: reduce)').matches || w.matchMedia('(pointer: coarse)').matches) return;
  let frame = 0;
  doc.addEventListener('pointermove', (e) => {
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(() => {
      const btn = doc.querySelector('[data-testid="stBaseButton-primary"]:not(:disabled)');
      if (!btn) return;
      const wrap = btn.parentElement;
      wrap.classList.add('mc-magnet');
      const r = btn.getBoundingClientRect();
      const dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2);
      const near = Math.abs(dx) < r.width / 2 + 48 && Math.abs(dy) < r.height / 2 + 48;
      wrap.style.transform = near ? `translate(${(dx * 0.08).toFixed(1)}px, ${(dy * 0.22).toFixed(1)}px)` : '';
    });
  }, { passive: true });
})();
</script>
"""

def enable_magnetic_cta():
    """Pull the primary button slightly toward the cursor (transform only, outside Streamlit's render cycle)."""
    components.html(_MAGNET_JS, height=0)
