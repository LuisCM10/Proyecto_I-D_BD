"""Capa de presentación de Job to go.

Componentes visuales de solo lectura: el estado, los formularios y las acciones
siguen controlados por Streamlit y los módulos de operaciones sobre Neo4j.
"""
from __future__ import annotations

from html import escape
from typing import Mapping, Any

import streamlit as st


def safe(value: Any) -> str:
    return escape('' if value is None else str(value), quote=True)


def initials(value: Any) -> str:
    parts = [p for p in str(value or '?').strip().split() if p]
    return ''.join(part[0].upper() for part in parts[:2]) or '?'


def format_cop(value: Any) -> str:
    try:
        amount = float(value or 0)
    except (TypeError, ValueError):
        return 'Salario por definir'
    return f'${amount:,.0f} COP' if amount > 0 else 'Salario por definir'


def chips(items, *, limit: int = 6) -> str:
    values = list(items or [])
    result = ''.join(f'<span class="jt-chip">{safe(x)}</span>' for x in values[:limit] if x)
    if len(values) > limit:
        result += f'<span class="jt-chip jt-chip-muted">+{len(values)-limit}</span>'
    return result


def hero(eyebrow: str, title: str, description: str, *, badge: str = '') -> None:
    badge_markup = f'<span class="jt-hero-badge">{safe(badge)}</span>' if badge else ''
    st.markdown(
        '<section class="jt-page-hero"><div class="jt-hero-copy">'
        f'<div class="jt-eyebrow">{safe(eyebrow)}</div>'
        f'<h1>{safe(title)}</h1><p>{safe(description)}</p></div>'
        f'{badge_markup}</section>',
        unsafe_allow_html=True,
    )


def section(title: str, subtitle: str = '') -> None:
    st.markdown(
        '<div class="jt-section-head">'
        f'<div><h3>{safe(title)}</h3>{f"<p>{safe(subtitle)}</p>" if subtitle else ""}</div>'
        '</div>', unsafe_allow_html=True,
    )


def portrait_card(name: str, *, category: str = 'Profesional', location: str = '',
                  description: str = '', skills=(), detail: str = '') -> None:
    details = ' · '.join(str(x) for x in [location, detail] if x)
    st.markdown(
        '<div class="jt-person-card">'
        f'<div class="jt-avatar">{safe(initials(name))}</div>'
        '<div class="jt-person-info">'
        f'<span class="jt-overline">{safe(category)}</span><h4>{safe(name)}</h4>'
        f'<p class="jt-person-meta">{safe(details)}</p>'
        f'{f"<p class=\"jt-person-desc\">{safe(description)}</p>" if description else ""}'
        f'{f"<div class=\"jt-chip-list\">{chips(skills)}</div>" if skills else ""}'
        '</div></div>', unsafe_allow_html=True,
    )


def job_card(job: Mapping[str, Any], *, recommended: bool = False,
             compact: bool = False, embedded: bool = False) -> None:
    title = job.get('titulo') or job.get('titulo_oferta') or 'Vacante sin título'
    company = job.get('empresa') or 'Empresa no especificada'
    location = job.get('ubicacion') or 'Ubicación por confirmar'
    contract = job.get('tipo_contrato') or job.get('contrato') or ''
    salary = format_cop(job.get('salario'))
    status = job.get('estado_visible') or job.get('estado') or ''
    state_class = 'jt-status-muted' if status in ('Cerrada', 'Vencida') else 'jt-status-success'
    label = (f'<span class="jt-status {state_class}">{safe(status)}</span>' if status else
             ('<span class="jt-status jt-status-info">Recomendada</span>' if recommended else ''))
    matches = job.get('coincidencias')
    if matches is None:
        matches = job.get('habilidades_coincidentes')
    try:
        match_badge = f'<span class="jt-match">{int(matches)} coincidencia(s)</span>' if matches is not None else ''
    except (TypeError, ValueError):
        match_badge = ''
    skills = job.get('habilidades') or job.get('habilidades_match') or []
    if isinstance(skills, str):
        skills = [skills]
    description = str(job.get('descripcion') or '')
    if compact: description = description[:160] + ('…' if len(description) > 160 else '')
    meta = ' · '.join(x for x in [location, contract] if x)
    st.markdown(
        '<article class="jt-job'+(' jt-job-embedded' if embedded else '')+'">'
        '<div class="jt-job-top"><div class="jt-company-mark">JT</div>'
        f'<div class="jt-job-identity"><span class="jt-overline">{safe(company)}</span>'
        f'<h4>{safe(title)}</h4><div class="jt-job-meta">{safe(meta)}</div></div>{label}</div>'
        '<div class="jt-job-bottom">'
        f'<span class="jt-salary">{safe(salary)}</span>{match_badge}</div>'
        + (f'<p class="jt-job-desc">{safe(description)}</p>' if description else '')
        + (f'<div class="jt-chip-list">{chips(skills)}</div>' if skills else '')
        + '</article>', unsafe_allow_html=True,
    )


def notice(title: str, detail: str = '') -> None:
    st.markdown(f'<div class="jt-notice"><strong>{safe(title)}</strong><span>{safe(detail)}</span></div>', unsafe_allow_html=True)


def inject_theme() -> None:
    st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
:root {
  --jt-paper:#f7f9fc; --jt-card:#ffffff; --jt-ink:#142b48;
  --jt-muted:#677a95; --jt-primary:#2260d8; --jt-soft:#ebf2ff;
  --jt-line:#e4eaf3; --jt-shadow:0 8px 30px rgba(19,47,94,.035);
}
html,body,[class*="css"],.stApp {font-family:'DM Sans',sans-serif !important;}
.stApp {background:var(--jt-paper) !important;color:var(--jt-ink) !important;}
.block-container {max-width:1390px !important;padding:2rem 2.5rem 4rem !important;}
[data-testid="stHeader"] {background:rgba(247,249,252,.86) !important;backdrop-filter:blur(10px);}
[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
 background:#fff !important;
}
[data-testid="stSidebar"] {border-right:1px solid var(--jt-line) !important;}
[data-testid="stSidebarUserContent"] {padding:22px 16px 22px !important;}
h1,h2,h3,h4 {font-family:'Plus Jakarta Sans','DM Sans',sans-serif !important;letter-spacing:-.035em !important;color:var(--jt-ink) !important;}
h1 {font-size:clamp(30px,2.8vw,40px) !important;line-height:1.2 !important;}
h2 {font-size:25px !important;}h3{font-size:19px !important;}
[data-testid="stSidebar"] .jtg-brand {font-size:25px !important;letter-spacing:-1.1px !important;padding:6px 0 8px !important;color:var(--jt-primary) !important;}
.jt-logo-line {display:flex;align-items:center;gap:11px;margin-bottom:5px;}
.jt-logo-mark {background:#2363e4;color:#fff;border-radius:13px;font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;font-size:22px;width:43px;height:43px;display:flex;align-items:center;justify-content:center;box-shadow:0 9px 18px rgba(38,96,216,.18);}
.jt-logo-wordmark {font-family:'Plus Jakarta Sans',sans-serif;font-size:22px;font-weight:800;color:#163a6e;letter-spacing:-1px;}
.jt-logo-subtitle {font-size:11px;color:#8c9bb0;margin-bottom:23px;padding-left:2px;}
.jt-side-account {display:flex;align-items:center;gap:10px;padding:12px 10px;margin:10px 0 20px;background:#f5f8fd;border:1px solid #e7edf5;border-radius:15px;}
.jt-account-avatar {background:#dce9ff;color:#1f5aca;display:flex;align-items:center;justify-content:center;border-radius:10px;width:37px;height:37px;flex:none;font-weight:800;font-size:13px;}
.jt-account-title {font-size:12px;font-weight:800;color:#163a61;max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.jt-account-role {font-size:11px;color:#7b8ca6;}
.jt-topbar {display:flex;align-items:center;justify-content:space-between;gap:12px;padding:0 0 22px;}
.jt-topbar-left {display:flex;align-items:center;gap:10px;letter-spacing:.01em;font-size:12px;color:#7889a2;}
.jt-topbar-left strong {color:#2b496c;font-weight:800;}
.jt-topbar-right {display:inline-flex;gap:7px;align-items:center;font-size:11px;color:#6980a0;background:white;border:1px solid var(--jt-line);border-radius:999px;padding:7px 12px;}
.jt-online {height:7px;width:7px;border-radius:50%;background:#16a085;display:inline-block;}
[data-testid="stSidebar"] .jtg-sidebar-caption {font-size:10px !important;color:#98a7ba !important;margin:18px 10px 7px !important;letter-spacing:1.4px !important;}
[data-testid="stSidebar"] [data-testid="stButton"] button {border-radius:12px !important;min-height:44px !important;padding:10px 13px !important;font-size:12.5px !important;}
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {background:#eaf2ff !important;border-color:#dbe9ff !important;box-shadow:inset 3px 0 0 var(--jt-primary) !important;color:#1857c4 !important;}
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"]:hover {background:#f2f6ff !important;}
.jt-page-hero {display:flex;align-items:center;justify-content:space-between;gap:18px;border:1px solid #e1e9f5;background:linear-gradient(110deg,#fff 55%,#f0f6ff 100%);border-radius:22px;padding:30px 34px;margin:0 0 22px;box-shadow:var(--jt-shadow);position:relative;overflow:hidden;}
.jt-page-hero::after{content:'';position:absolute;width:210px;height:210px;right:-110px;top:-100px;background:radial-gradient(circle,#d9e9ff 0%,transparent 70%);pointer-events:none;}
.jt-page-hero h1{font-size:clamp(27px,2.7vw,38px) !important;line-height:1.2;margin:9px 0 9px !important;max-width:830px;}
.jt-page-hero p{font-size:13.5px;color:#677e9a;line-height:1.7;margin:0;max-width:770px;}
.jt-eyebrow{font-size:10px;letter-spacing:1.8px;font-weight:800;text-transform:uppercase;color:#2766d8;}
.jt-hero-badge {border:1px solid #d3e5ff;background:#eef5ff;padding:10px 13px;border-radius:999px;color:#255cac;font-weight:750;font-size:11px;z-index:1;white-space:nowrap;}
.hero {border-radius:22px !important;box-shadow:var(--jt-shadow) !important;margin:0 0 22px !important;}
.jt-section-head {margin:26px 0 14px;display:flex;align-items:center;justify-content:space-between;gap:14px;}
.jt-section-head h3 {font-size:19px !important;margin:0 0 4px !important;}
.jt-section-head p {margin:0;color:var(--jt-muted);font-size:12px;}
.jt-profile-details{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:10px 0 18px;}
.jt-profile-detail {background:white;border:1px solid var(--jt-line);border-radius:13px;padding:15px 18px;min-width:0;}
.jt-profile-detail span{display:block;color:#8798ad;font-size:10px;letter-spacing:.3px;margin-bottom:7px;}
.jt-profile-detail strong{font-size:12px;color:#294b72;overflow-wrap:anywhere;}
.jt-person-card {display:flex;gap:14px;align-items:flex-start;background:#fff;border:1px solid var(--jt-line);border-radius:16px;padding:18px 19px;margin:5px 0 11px;box-shadow:var(--jt-shadow);min-width:0;}
.jt-avatar {width:48px;height:48px;flex:none;display:flex;align-items:center;justify-content:center;border-radius:13px;background:#e6efff;color:#2462d4;font-size:16px;font-weight:800;font-family:'Plus Jakarta Sans',sans-serif;}
.jt-person-info {min-width:0;flex:1;}
.jt-overline {display:block;font-size:10px;color:#4877b6;text-transform:uppercase;letter-spacing:1.1px;font-weight:800;}
.jt-person-info h4{font-size:15px !important;line-height:1.3;margin:5px 0 5px !important;overflow-wrap:anywhere;}
.jt-person-meta {color:#70849e;font-size:12px;line-height:1.5;margin:0 0 5px;}
.jt-person-desc {color:#627995;font-size:12px;line-height:1.65;margin:8px 0 !important;}
.jt-chip-list {display:flex;gap:6px;flex-wrap:wrap;margin-top:11px;}
.jt-chip {border:1px solid #dce7fa;background:#f1f6ff;color:#2c5eac;padding:5px 9px;border-radius:999px;font-size:10px;line-height:1.3;font-weight:650;}
.jt-chip-muted{background:#f5f7fb;color:#637998;}
.jt-job-embedded {padding:0 !important;border:0 !important;box-shadow:none !important;margin:0 0 12px !important;}
.jt-job {background:#fff;border:1px solid var(--jt-line);border-radius:17px;padding:19px 21px;margin:4px 0 10px;box-shadow:var(--jt-shadow);min-width:0;}
.jt-job-top{display:flex;gap:13px;align-items:flex-start;}
.jt-company-mark {display:flex;align-items:center;justify-content:center;width:46px;height:46px;background:linear-gradient(140deg,#d8e8ff,#ecf4ff);color:#225fc8;border-radius:13px;font-size:12px;font-weight:800;letter-spacing:-.3px;flex:none;}
.jt-job-identity{flex:1;min-width:0;}
.jt-job h4{font-size:16px !important;margin:4px 0 6px !important;overflow-wrap:anywhere;line-height:1.35;}
.jt-job-meta{font-size:11.5px;color:#7587a2;}
.jt-job-bottom {display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:16px 0 0 59px;}
.jt-salary{font-size:12px;font-weight:800;color:#1b486d;}
.jt-match {font-size:10.5px;color:#2260d8;border-radius:999px;background:#e9f2ff;padding:5px 9px;font-weight:750;}
.jt-job-desc {font-size:12px;color:#607694;line-height:1.6;margin:12px 0 0 59px !important;}
.jt-job .jt-chip-list {margin-left:59px;margin-top:12px;}
.jt-status{border-radius:99px;padding:6px 10px;font-size:10px;font-weight:750;flex:none;white-space:nowrap;}
.jt-status-success {background:#ecfaf2;color:#15803d;}
.jt-status-muted {background:#f1f3f7;color:#64748b;}
.jt-status-info {background:#eff5ff;color:#2563eb;}
.jt-list-counter{font-weight:700;font-size:12px;color:#68819f;margin:11px 0 16px;}
.jt-notice {display:flex;flex-direction:column;gap:3px;border-radius:13px;background:#eef5ff;border:1px solid #dceaff;padding:14px 17px;color:#2a5c9c;margin:11px 0;}
.jt-notice strong {font-size:12px;font-weight:800;}.jt-notice span {font-size:11px;line-height:1.6;color:#6983a2;}
.rp-kpis {grid-template-columns:repeat(5,minmax(0,1fr));gap:12px !important;margin-top:13px !important;}
.rp-kpi {border-radius:18px !important;border:1px solid var(--jt-line) !important;padding:19px 20px !important;box-shadow:var(--jt-shadow) !important;}
.rp-kpi:before {height:2px !important;}
.rp-kpi-icon {border-radius:10px !important;background:#edf4ff !important;}
.rp-kpi-number {font-size:31px !important;}
.rp-bar-row{grid-template-columns:minmax(0,1.1fr) minmax(0,1.2fr) 30px;}
.rp-bar-name {white-space:normal !important;overflow-wrap:anywhere;line-height:1.35;}
.rp-bars {min-height:280px !important;border-color:var(--jt-line) !important;border-radius:18px !important;box-shadow:var(--jt-shadow);}
.rp-result {border-color:var(--jt-line) !important;box-shadow:var(--jt-shadow) !important;}
[data-testid="stVerticalBlockBorderWrapper"]:has(>div>[data-testid="stVerticalBlock"]) {border-color:var(--jt-line) !important;}
[data-testid="stForm"] {border:1px solid var(--jt-line) !important;border-radius:18px !important;padding:22px !important;box-shadow:var(--jt-shadow) !important;}
[data-testid="stMetric"] {border:1px solid var(--jt-line) !important;border-radius:16px !important;padding:19px !important;box-shadow:var(--jt-shadow) !important;}
[data-testid="stMetricLabel"] p {font-size:12px;font-weight:650;color:#7186a0;}
[data-testid="stMetricValue"] {font-family:'Plus Jakarta Sans',sans-serif;font-size:27px;color:#153761;}
[data-testid="stDataFrame"], [data-testid="stExpander"], [data-testid="stTabs"] {border-radius:15px !important;}
[data-testid="stExpander"] {background:white;border-color:var(--jt-line) !important;}
[data-testid="stDataFrame"] {border:1px solid var(--jt-line) !important;overflow:hidden;}
[data-baseweb="tab-list"] {gap:3px !important;border-bottom:1px solid #e5ebf4;padding:1px 2px 0;}
[data-baseweb="tab"] {border-radius:10px 10px 0 0 !important;padding:12px 16px !important;font-size:12px !important;font-weight:750 !important;}
[data-baseweb="tab"][aria-selected="true"]{background:#eef4ff !important;border-bottom:2px solid #2563eb !important;color:#1c5ac9 !important;}
[data-testid="stFormSubmitButton"] button[kind="primary"],.stButton>button[kind="primary"]{background:#2563eb !important;border-color:#2563eb !important;box-shadow:none !important;border-radius:11px !important;}
.stButton>button,.stFormSubmitButton>button {min-height:41px;font-weight:700 !important;border-radius:11px !important;}
.stButton>button[kind="secondary"] {border:1px solid #dbe5f3;color:#355779;background:#fff;}
.stButton>button:hover,.stFormSubmitButton>button:hover {transform:none !important;}
[data-testid="stSelectbox"],[data-testid="stTextInput"],[data-testid="stMultiSelect"],[data-testid="stTextArea"],[data-testid="stNumberInput"] {margin-bottom:6px;}
label[data-testid="stWidgetLabel"] p {font-size:12px;color:#334e6d;font-weight:650;}
[data-testid="stAlert"] {border-radius:13px !important;}
[data-testid="stSidebarCollapsedControl"] {display:flex !important;visibility:visible !important;}
[data-testid="stSidebarCollapsedControl"] button {background:white !important;border:1px solid #dbe7f7 !important;}
.jt-auth-promo {padding:30px 29px;background:linear-gradient(150deg,#1d59cb,#3478ee);color:white;border-radius:23px;min-height:300px;box-shadow:0 12px 40px rgba(27,81,178,.15);}
.jt-auth-promo .jt-auth-kicker {text-transform:uppercase;letter-spacing:2px;font-size:10px;color:#c8ddff;font-weight:750;}
.jt-auth-promo h2 {color:white !important;line-height:1.25 !important;font-size:29px !important;margin:20px 0 10px !important;}
.jt-auth-promo p{color:#dbe8ff;font-size:13px;line-height:1.8;}
.jt-auth-divider {height:1px;background:rgba(255,255,255,.2);margin:23px 0;}
.jt-auth-point{display:flex;gap:10px;align-items:center;padding:9px 0;font-size:12px;font-weight:650;color:#fff;}
.jt-auth-point span{width:20px;height:20px;display:flex;justify-content:center;align-items:center;color:#195ac7;background:#fff;border-radius:50%;font-size:11px;font-weight:800;}
.jt-login-hint{color:#7991ae;font-size:11px;text-align:center;}
@media(max-width:1100px){.block-container {padding:1.4rem 1.35rem 3rem !important;}.rp-kpis{grid-template-columns:repeat(3,minmax(0,1fr));}}
@media(max-width:820px){.jt-page-hero{padding:24px 22px;}.jt-page-hero h1{font-size:29px !important;}.jt-hero-badge{display:none;}}
@media(max-width:700px){.block-container {padding:1.2rem .85rem 2rem !important;}.jt-job-bottom,.jt-job-desc,.jt-job .jt-chip-list{margin-left:0;}.jt-job-top{flex-wrap:wrap;}.jt-page-hero{padding:21px 19px;}.jt-page-hero h1{font-size:26px !important;}.rp-kpis{grid-template-columns:repeat(2,minmax(0,1fr)) !important;}.jt-person-card{padding:15px;}.jt-profile-details{grid-template-columns:1fr;}.jt-auth-promo{min-height:0;padding:22px;}}
</style>
    ''', unsafe_allow_html=True)
