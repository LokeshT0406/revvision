"""
RevVision Pro – Theme System
Three themes: Dark (default), Light, System (follows OS preference).
"""

_FONT_IMPORT = "@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;600&display=swap');"

DARK_CSS = f"""
<style>
{_FONT_IMPORT}

html, body, [class*='css'], .stApp {{
    font-family: 'DM Sans', system-ui, sans-serif !important;
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
}}
.main .block-container {{ background: #0d1117 !important; padding-top: 1.5rem !important; }}
section[data-testid="stSidebar"] {{ background: #161b22 !important; border-right: 1px solid #30363d !important; }}
section[data-testid="stSidebar"] * {{ color: #c9d1d9 !important; }}
h1, h2, h3, h4 {{ font-family: 'DM Sans', sans-serif !important; font-weight: 700 !important; }}
h1 {{ color: #f0f6fc !important; font-size: 2rem !important; letter-spacing: -0.5px; }}
h2 {{ color: #e6edf3 !important; }}
h3 {{ color: #c9d1d9 !important; }}

[data-testid="stMetric"] {{
    background: linear-gradient(135deg, #161b22 0%, #1c2128 100%) !important;
    border: 1px solid #30363d !important;
    border-radius: 12px !important;
    padding: 16px !important;
}}
[data-testid="stMetric"]:hover {{ border-color: #58a6ff !important; box-shadow: 0 0 16px rgba(88,166,255,0.12) !important; }}
[data-testid="stMetricLabel"] {{ color: #8b949e !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.08em; }}
[data-testid="stMetricValue"] {{ color: #58a6ff !important; font-family: 'JetBrains Mono', monospace !important; font-size: 1.8rem !important; }}

.stTabs [data-baseweb="tab-list"] {{
    background: #161b22 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border: 1px solid #30363d !important;
    gap: 2px !important;
}}
.stTabs [data-baseweb="tab"] {{
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    color: #8b949e !important;
    border-radius: 7px !important;
    padding: 6px 14px !important;
    border: none !important;
    background: transparent !important;
}}
.stTabs [aria-selected="true"] {{
    background: #21262d !important;
    color: #58a6ff !important;
    border: 1px solid #30363d !important;
}}

.stButton > button {{
    background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 8px 20px !important;
}}
.stButton > button:hover {{ opacity: 0.88 !important; transform: translateY(-1px); }}

.stSelectbox > div > div, .stTextInput > div > div > input, .stNumberInput > div > div > input {{
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
}}

.stDataFrame {{ border-radius: 10px !important; overflow: hidden; border: 1px solid #30363d !important; }}
.stDataFrame thead th {{ background: #161b22 !important; color: #8b949e !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.06em; }}
.stDataFrame tbody td {{ background: #0d1117 !important; color: #c9d1d9 !important; border-bottom: 1px solid #21262d !important; }}
.stDataFrame tbody tr:hover td {{ background: #161b22 !important; }}

.stSuccess {{ background: #0d2818 !important; border: 1px solid #238636 !important; border-radius: 8px !important; color: #3fb950 !important; }}
.stError   {{ background: #2d0f0f !important; border: 1px solid #da3633 !important; border-radius: 8px !important; color: #f85149 !important; }}
.stWarning {{ background: #2a1f00 !important; border: 1px solid #9e6a03 !important; border-radius: 8px !important; color: #d29922 !important; }}
.stInfo    {{ background: #0d1f33 !important; border: 1px solid #1f6feb !important; border-radius: 8px !important; color: #58a6ff !important; }}

code, pre, .stCode {{
    font-family: 'JetBrains Mono', monospace !important;
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #79c0ff !important;
}}

.rv-risk-banner {{
    background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
    border: 1px solid #30363d;
    border-left: 4px solid #58a6ff;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 10px 0 18px 0;
    font-size: 1rem;
    font-weight: 500;
    color: #e6edf3;
}}
.rv-stat-row {{
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 0.88rem;
    color: #c9d1d9;
}}

.file-badge {{ display:inline-block; padding:3px 9px; border-radius:5px; font-size:11px; font-family:'JetBrains Mono',monospace; font-weight:600; margin-right:4px; }}
.badge-apex   {{ background:#0d2238; color:#79c0ff; border:1px solid #1f6feb44; }}
.badge-flow   {{ background:#0d2218; color:#56d364; border:1px solid #23863644; }}
.badge-qcp    {{ background:#2d1b3d; color:#d2a8ff; border:1px solid #8957e544; }}
.badge-rule   {{ background:#2d1f0a; color:#ffa657; border:1px solid #9e6a0344; }}
.badge-xml    {{ background:#0d1f2d; color:#39c5cf; border:1px solid #1f8ba744; }}
.badge-meta   {{ background:#2d0f23; color:#ff7eb3; border:1px solid #bf4b8a44; }}
.badge-unknown{{ background:#1c2128; color:#8b949e; border:1px solid #30363d; }}

.streamlit-expanderHeader {{
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #c9d1d9 !important;
    font-weight: 600 !important;
}}
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: #0d1117; }}
::-webkit-scrollbar-thumb {{ background: #30363d; border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: #8b949e; }}
hr {{ border-color: #21262d !important; }}
.stRadio label {{ color: #c9d1d9 !important; }}
.stDownloadButton > button {{ background: #21262d !important; color: #58a6ff !important; border: 1px solid #30363d !important; border-radius: 8px !important; font-weight: 600 !important; }}
@media (max-width: 768px) {{
    .stTabs [data-baseweb='tab'] {{ padding: 5px 8px; font-size: 11px; }}
    h1 {{ font-size: 1.4rem !important; }}
}}

/* ── File uploader fix ── */
[data-testid="stFileUploader"] {{
    background: #161b22 !important;
    border: 2px dashed #30363d !important;
    border-radius: 12px !important;
}}
[data-testid="stFileUploader"] * {{ color: #c9d1d9 !important; }}
[data-testid="stFileUploader"] small {{ color: #8b949e !important; }}
[data-testid="stFileUploaderDropzoneInstructions"] * {{ color: #c9d1d9 !important; }}
[data-testid="stFileUploaderDropzone"] button {{
    background: #21262d !important;
    color: #c9d1d9 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
}}
/* file list items */
[data-testid="stFileUploaderFile"] {{ color: #c9d1d9 !important; }}
[data-testid="stFileUploaderFileName"] {{ color: #c9d1d9 !important; }}
/* Generic text fixes */
.stMarkdown p {{ color: #c9d1d9 !important; }}
.stMarkdown li {{ color: #c9d1d9 !important; }}
label {{ color: #c9d1d9 !important; }}
/* Tab content text */
[data-testid="stTabPanel"] * {{ color: #c9d1d9; }}
[data-testid="stTabPanel"] strong {{ color: #e6edf3 !important; }}
[data-testid="stTabPanel"] code {{ color: #79c0ff !important; }}

</style>
"""

LIGHT_CSS = f"""
<style>
{_FONT_IMPORT}

html, body, [class*='css'], .stApp {{
    font-family: 'DM Sans', system-ui, sans-serif !important;
    background-color: #f6f8fa !important;
    color: #1c2128 !important;
}}
/* Hide Streamlit toolbar/menu to prevent theme switching controls */
[data-testid="stHeader"] {{ display: none !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}
[data-testid="stDecoration"] {{ display: none !important; }}
#MainMenu {{ visibility: hidden !important; }}
.main .block-container {{ background: #f6f8fa !important; padding-top: 1.5rem !important; }}
section[data-testid="stSidebar"] {{ background: #ffffff !important; border-right: 1px solid #d0d7de !important; }}
section[data-testid="stSidebar"] * {{ color: #24292f !important; }}
h1, h2, h3, h4 {{ font-family: 'DM Sans', sans-serif !important; font-weight: 700 !important; }}
h1 {{ color: #1c2128 !important; font-size: 2rem !important; letter-spacing: -0.5px; }}
h2 {{ color: #24292f !important; }}
h3 {{ color: #57606a !important; }}

[data-testid="stMetric"] {{
    background: #ffffff !important;
    border: 1px solid #d0d7de !important;
    border-radius: 12px !important;
    padding: 16px !important;
    box-shadow: 0 1px 3px rgba(27,31,36,0.06) !important;
}}
[data-testid="stMetric"]:hover {{ border-color: #0969da !important; box-shadow: 0 4px 12px rgba(9,105,218,0.1) !important; }}
[data-testid="stMetricLabel"] {{ color: #57606a !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.08em; }}
[data-testid="stMetricValue"] {{ color: #0969da !important; font-family: 'JetBrains Mono', monospace !important; font-size: 1.8rem !important; }}

.stTabs [data-baseweb="tab-list"] {{
    background: #ffffff !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border: 1px solid #d0d7de !important;
    gap: 2px !important;
}}
.stTabs [data-baseweb="tab"] {{
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    color: #57606a !important;
    border-radius: 7px !important;
    padding: 6px 14px !important;
    background: transparent !important;
    border: none !important;
}}
.stTabs [aria-selected="true"] {{
    background: #f6f8fa !important;
    color: #0969da !important;
    border: 1px solid #d0d7de !important;
}}

.stButton > button {{
    background: linear-gradient(135deg, #0969da 0%, #218bff 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 8px 20px !important;
}}
.stButton > button:hover {{ opacity: 0.88 !important; }}

.stSelectbox > div > div, .stTextInput > div > div > input, .stNumberInput > div > div > input {{
    background: #ffffff !important;
    border: 1px solid #d0d7de !important;
    border-radius: 8px !important;
    color: #1c2128 !important;
}}

.stDataFrame {{ border-radius: 10px !important; border: 1px solid #d0d7de !important; overflow: hidden; }}
.stDataFrame thead th {{ background: #f6f8fa !important; color: #57606a !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.06em; }}
.stDataFrame tbody td {{ background: #ffffff !important; color: #1c2128 !important; border-bottom: 1px solid #eaeef2 !important; }}
.stDataFrame tbody tr:hover td {{ background: #f6f8fa !important; }}

.stSuccess {{ background: #dafbe1 !important; border: 1px solid #2da44e !important; border-radius: 8px !important; color: #1a7f37 !important; }}
.stError   {{ background: #ffebe9 !important; border: 1px solid #cf222e !important; border-radius: 8px !important; color: #a40e26 !important; }}
.stWarning {{ background: #fff8c5 !important; border: 1px solid #d4a72c !important; border-radius: 8px !important; color: #7d4e00 !important; }}
.stInfo    {{ background: #ddf4ff !important; border: 1px solid #54aeff !important; border-radius: 8px !important; color: #0550ae !important; }}

code, pre, .stCode {{
    font-family: 'JetBrains Mono', monospace !important;
    background: #f6f8fa !important;
    border: 1px solid #d0d7de !important;
    border-radius: 8px !important;
    color: #953800 !important;
}}

.rv-risk-banner {{
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-left: 4px solid #0969da;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 10px 0 18px 0;
    font-size: 1rem;
    font-weight: 500;
    color: #1c2128;
    box-shadow: 0 1px 3px rgba(27,31,36,0.06);
}}
.rv-stat-row {{
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 0.88rem;
    color: #24292f;
}}

.file-badge {{ display:inline-block; padding:3px 9px; border-radius:5px; font-size:11px; font-family:'JetBrains Mono',monospace; font-weight:600; margin-right:4px; }}
.badge-apex   {{ background:#ddf4ff; color:#0550ae; border:1px solid #54aeff55; }}
.badge-flow   {{ background:#dafbe1; color:#1a7f37; border:1px solid #2da44e55; }}
.badge-qcp    {{ background:#fbefff; color:#7a43b6; border:1px solid #bf8fff55; }}
.badge-rule   {{ background:#fff1e5; color:#953800; border:1px solid #ffa65755; }}
.badge-xml    {{ background:#e6f7ff; color:#0366d6; border:1px solid #79c0ff55; }}
.badge-meta   {{ background:#ffeff7; color:#bf4b8a; border:1px solid #ff7eb355; }}
.badge-unknown{{ background:#f6f8fa; color:#57606a; border:1px solid #d0d7de; }}

.streamlit-expanderHeader {{
    background: #ffffff !important;
    border: 1px solid #d0d7de !important;
    border-radius: 8px !important;
    color: #24292f !important;
    font-weight: 600 !important;
}}
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: #f6f8fa; }}
::-webkit-scrollbar-thumb {{ background: #d0d7de; border-radius: 4px; }}
hr {{ border-color: #eaeef2 !important; }}
.stRadio label {{ color: #24292f !important; }}
.stDownloadButton > button {{ background: #ffffff !important; color: #0969da !important; border: 1px solid #d0d7de !important; border-radius: 8px !important; font-weight: 600 !important; }}
@media (max-width: 768px) {{
    .stTabs [data-baseweb='tab'] {{ padding: 5px 8px; font-size: 11px; }}
    h1 {{ font-size: 1.4rem !important; }}
}}
</style>
"""

SYSTEM_CSS = f"""
<style>
{_FONT_IMPORT}

html, body, [class*='css'], .stApp {{
    font-family: 'DM Sans', system-ui, sans-serif !important;
    background-color: #f6f8fa !important;
    color: #1c2128 !important;
}}
.main .block-container {{ background: #f6f8fa !important; padding-top: 1.5rem !important; }}
section[data-testid="stSidebar"] {{ background: #ffffff !important; border-right: 1px solid #d0d7de !important; }}
section[data-testid="stSidebar"] * {{ color: #24292f !important; }}
h1, h2, h3, h4 {{ font-family: 'DM Sans', sans-serif !important; font-weight: 700 !important; }}
h1 {{ color: #1c2128 !important; font-size: 2rem !important; }}
[data-testid="stMetric"] {{ background: #ffffff !important; border: 1px solid #d0d7de !important; border-radius: 12px !important; padding: 16px !important; }}
[data-testid="stMetricLabel"] {{ color: #57606a !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.08em; }}
[data-testid="stMetricValue"] {{ color: #0969da !important; font-family: 'JetBrains Mono', monospace !important; font-size: 1.8rem !important; }}
.stTabs [data-baseweb="tab-list"] {{ background: #ffffff !important; border-radius: 10px !important; padding: 4px !important; border: 1px solid #d0d7de !important; }}
.stTabs [data-baseweb="tab"] {{ font-weight: 600 !important; color: #57606a !important; border-radius: 7px !important; padding: 6px 14px !important; background: transparent !important; }}
.stTabs [aria-selected="true"] {{ background: #f6f8fa !important; color: #0969da !important; border: 1px solid #d0d7de !important; }}
.stButton > button {{ background: linear-gradient(135deg, #0969da, #218bff) !important; color: #fff !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }}
.stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div {{
    border-color: #d0d7de !important;
    box-shadow: none !important;
}}
.stSelectbox [data-baseweb="select"] > div:focus-within,
.stMultiSelect [data-baseweb="select"] > div:focus-within,
.stSelectbox [data-baseweb="select"] > div[data-focus-visible-added],
.stMultiSelect [data-baseweb="select"] > div[data-focus-visible-added],
.stSelectbox [data-baseweb="select"] > div[aria-expanded="true"],
.stMultiSelect [data-baseweb="select"] > div[aria-expanded="true"] {{
    border-color: #218bff !important;
    box-shadow: 0 0 0 1px #218bff !important;
}}
.stDataFrame {{ border-radius: 10px !important; border: 1px solid #d0d7de !important; overflow: hidden; }}
.stDataFrame thead th {{ background: #f6f8fa !important; color: #57606a !important; }}
.stDataFrame tbody td {{ background: #ffffff !important; color: #1c2128 !important; }}
.rv-risk-banner {{ background:#ffffff; border:1px solid #d0d7de; border-left:4px solid #0969da; border-radius:10px; padding:14px 18px; margin:10px 0 18px 0; color:#1c2128; }}
.file-badge {{ display:inline-block; padding:3px 9px; border-radius:5px; font-size:11px; font-family:'JetBrains Mono',monospace; font-weight:600; margin-right:4px; }}
.badge-apex{{background:#ddf4ff;color:#0550ae;border:1px solid #54aeff55;}}
.badge-flow{{background:#dafbe1;color:#1a7f37;border:1px solid #2da44e55;}}
.badge-qcp{{background:#fbefff;color:#7a43b6;border:1px solid #bf8fff55;}}
.badge-rule{{background:#fff1e5;color:#953800;border:1px solid #ffa65755;}}
.badge-xml{{background:#e6f7ff;color:#0366d6;border:1px solid #79c0ff55;}}
.badge-meta{{background:#ffeff7;color:#bf4b8a;border:1px solid #ff7eb355;}}
.badge-unknown{{background:#f6f8fa;color:#57606a;border:1px solid #d0d7de;}}
code, pre {{ font-family: 'JetBrains Mono', monospace !important; background: #f6f8fa !important; border: 1px solid #d0d7de !important; border-radius: 8px !important; }}
hr {{ border-color: #eaeef2 !important; }}
::-webkit-scrollbar {{ width:6px; height:6px; }}
::-webkit-scrollbar-thumb {{ background: #d0d7de; border-radius: 4px; }}

@media (prefers-color-scheme: dark) {{
html, body, [class*='css'], .stApp {{ background-color: #0d1117 !important; color: #e6edf3 !important; }}
.main .block-container {{ background: #0d1117 !important; }}
section[data-testid="stSidebar"] {{ background: #161b22 !important; border-right: 1px solid #30363d !important; }}
section[data-testid="stSidebar"] * {{ color: #c9d1d9 !important; }}
h1 {{ color: #f0f6fc !important; }}
h2 {{ color: #e6edf3 !important; }}
h3 {{ color: #c9d1d9 !important; }}
[data-testid="stMetric"] {{ background: linear-gradient(135deg,#161b22,#1c2128) !important; border: 1px solid #30363d !important; }}
[data-testid="stMetricLabel"] {{ color: #8b949e !important; }}
[data-testid="stMetricValue"] {{ color: #58a6ff !important; }}
.stTabs [data-baseweb="tab-list"] {{ background: #161b22 !important; border: 1px solid #30363d !important; }}
.stTabs [data-baseweb="tab"] {{ color: #8b949e !important; }}
.stTabs [aria-selected="true"] {{ background: #21262d !important; color: #58a6ff !important; border: 1px solid #30363d !important; }}
.stButton > button {{ background: linear-gradient(135deg,#1f6feb,#388bfd) !important; }}
.stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div {{
    border-color: #30363d !important;
    box-shadow: none !important;
}}
.stSelectbox [data-baseweb="select"] > div:focus-within,
.stMultiSelect [data-baseweb="select"] > div:focus-within,
.stSelectbox [data-baseweb="select"] > div[data-focus-visible-added],
.stMultiSelect [data-baseweb="select"] > div[data-focus-visible-added],
.stSelectbox [data-baseweb="select"] > div[aria-expanded="true"],
.stMultiSelect [data-baseweb="select"] > div[aria-expanded="true"] {{
    border-color: #58a6ff !important;
    box-shadow: 0 0 0 1px #58a6ff !important;
}}
.stDataFrame {{ border: 1px solid #30363d !important; }}
.stDataFrame thead th {{ background: #161b22 !important; color: #8b949e !important; }}
.stDataFrame tbody td {{ background: #0d1117 !important; color: #c9d1d9 !important; border-bottom: 1px solid #21262d !important; }}
.rv-risk-banner {{ background:linear-gradient(135deg,#161b22,#1c2128); border:1px solid #30363d; border-left:4px solid #58a6ff; color:#e6edf3; }}
.badge-apex{{background:#0d2238;color:#79c0ff;border:1px solid #1f6feb44;}}
.badge-flow{{background:#0d2218;color:#56d364;border:1px solid #23863644;}}
.badge-qcp{{background:#2d1b3d;color:#d2a8ff;border:1px solid #8957e544;}}
.badge-rule{{background:#2d1f0a;color:#ffa657;border:1px solid #9e6a0344;}}
.badge-xml{{background:#0d1f2d;color:#39c5cf;border:1px solid #1f8ba744;}}
.badge-meta{{background:#2d0f23;color:#ff7eb3;border:1px solid #bf4b8a44;}}
.badge-unknown{{background:#1c2128;color:#8b949e;border:1px solid #30363d;}}
code, pre {{ background: #161b22 !important; border: 1px solid #30363d !important; color: #79c0ff !important; }}
hr {{ border-color: #21262d !important; }}
::-webkit-scrollbar-track {{ background: #0d1117; }}
::-webkit-scrollbar-thumb {{ background: #30363d; }}
}}
</style>
"""

THEMES: dict[str, str] = {
    "🌙 Dark":   DARK_CSS,
    "☀️ Light":  LIGHT_CSS,
    "💻 System": SYSTEM_CSS,
}

CSS = SYSTEM_CSS

