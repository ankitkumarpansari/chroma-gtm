#!/usr/bin/env python3
"""
Chroma Signal - Lightweight viewer using HTTP API
Run: streamlit run chroma_viewer.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# === PAGE CONFIG ===
st.set_page_config(page_title="Chroma Signal", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")

# === SECRETS HELPER ===
def get_secret(key, default):
    try:
        return st.secrets[key]
    except:
        return default

# === CONFIG ===
APP_PASSWORD = get_secret("APP_PASSWORD", "chroma2024")
CHROMA_API_KEY = get_secret("CHROMA_API_KEY", "ck-2i6neFLSKhd5pEqLP3jZKUkG6tX3yo4RVUZEeRxs4fHm")
CHROMA_TENANT = get_secret("CHROMA_TENANT", "aa8f571e-03dc-4cd8-b888-723bd00b83f0")
CHROMA_DATABASE = get_secret("CHROMA_DATABASE", "customer")
CHROMA_API_URL = f"https://api.trychroma.com/v1/tenants/{CHROMA_TENANT}/databases/{CHROMA_DATABASE}"

# === PASSWORD PROTECTION ===
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("### 🔐 Chroma Signal")
        password = st.text_input("Enter password", type="password")
        if st.button("Login"):
            if password == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
        st.stop()

check_password()

# === CHROMA HTTP CLIENT ===
class ChromaHTTPClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {CHROMA_API_KEY}",
            "Content-Type": "application/json"
        }
    
    def list_collections(self):
        try:
            resp = requests.get(f"{CHROMA_API_URL}/collections", headers=self.headers)
            if resp.status_code == 200:
                return [c["name"] for c in resp.json()]
            return []
        except:
            return []
    
    def get_collection_count(self, name):
        try:
            resp = requests.get(f"{CHROMA_API_URL}/collections/{name}/count", headers=self.headers)
            if resp.status_code == 200:
                return resp.json()
            return 0
        except:
            return 0
    
    def get_collection_data(self, name, limit=250, offset=0):
        try:
            resp = requests.post(
                f"{CHROMA_API_URL}/collections/{name}/get",
                headers=self.headers,
                json={"limit": limit, "offset": offset, "include": ["metadatas"]}
            )
            if resp.status_code == 200:
                return resp.json().get("metadatas", [])
            return []
        except:
            return []
    
    def query(self, name, query_text, n_results=100):
        try:
            resp = requests.post(
                f"{CHROMA_API_URL}/collections/{name}/query",
                headers=self.headers,
                json={
                    "query_texts": [query_text],
                    "n_results": n_results,
                    "include": ["metadatas", "distances"]
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("metadatas", [[]])[0], data.get("distances", [[]])[0]
            return [], []
        except:
            return [], []

# === STYLING ===
st.markdown("""
<style>
    .block-container {padding: 2rem 3rem; max-width: 1400px;}
    html, body, [class*="css"] {font-size: 15px; color: #0a0a0a;}
    .stTextInput > div > div > input {border: 1px solid #e5e5e5; border-radius: 8px; padding: 0.6rem 1rem; font-size: 0.95rem; background: #fafafa;}
    .stTextInput > div > div > input:focus {border-color: #a3a3a3; box-shadow: none; background: #fff;}
    .stMultiSelect > div > div {border-radius: 8px; font-size: 0.85rem; border-color: #e5e5e5;}
    .stMultiSelect label, .stSelectbox label {font-size: 0.75rem; color: #737373; font-weight: 500; text-transform: uppercase;}
    .stSelectbox > div > div {border-radius: 8px; font-size: 0.9rem; border-color: #e5e5e5;}
    .stDataFrame {border: 1px solid #e5e5e5; border-radius: 10px;}
    .stButton > button, .stDownloadButton > button {border: 1px solid #e5e5e5; border-radius: 8px; font-size: 0.85rem; font-weight: 500; padding: 0.5rem 1rem; background: #fff; color: #0a0a0a;}
    [data-testid="stMetricValue"] {font-size: 1.8rem; font-weight: 600; color: #0a0a0a;}
    [data-testid="stMetricLabel"] {font-size: 0.8rem; color: #737373;}
    hr {border: none; border-top: 1px solid #e5e5e5; margin: 1rem 0;}
    #MainMenu, footer, header {visibility: hidden;}
    .text-muted {color: #737373; font-size: 0.85rem;}
    .section-title {font-size: 1rem; font-weight: 600; margin-bottom: 0.75rem; color: #0a0a0a;}
    .filter-pill {display: inline-block; background: #0a0a0a; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; margin-right: 0.5rem;}
</style>
""", unsafe_allow_html=True)

# === COLUMN CONFIG ===
COL_NAMES = {
    'company_name': 'Company', 'category': 'Type', 'vector_db_used': 'Vector DB',
    'source_channel': 'Source', 'source': 'Source', 'use_case': 'Use Case',
    'industry': 'Industry', 'company_size': 'Size', 'notes': 'Notes', 'relevance': 'Score',
}
HIDDEN = ['source_section', 'added_at', 'date_found', 'updated_at', 'last_verified_at', 
          'source_url', 'video_title', 'context', 'extracted_from', 'added_date', 
          'confidence', 'selection_rationale']

def format_df(df):
    df = df.drop(columns=[c for c in HIDDEN if c in df.columns], errors='ignore')
    df = df.rename(columns={k: v for k, v in COL_NAMES.items() if k in df.columns})
    priority = ['Score', 'Company', 'Type', 'Vector DB', 'Source', 'Use Case', 'Industry']
    return df[[c for c in priority if c in df.columns] + [c for c in df.columns if c not in priority]]

# === INIT CLIENT ===
@st.cache_resource
def get_client():
    return ChromaHTTPClient()

client = get_client()

# === LOAD DATA ===
@st.cache_data(ttl=30)
def load_all_data(collection_name):
    count = client.get_collection_count(collection_name)
    all_data = []
    batch_size = 250
    offset = 0
    while offset < count:
        batch = client.get_collection_data(collection_name, limit=batch_size, offset=offset)
        all_data.extend(batch)
        offset += batch_size
    return pd.DataFrame(all_data) if all_data else pd.DataFrame()

# === MAIN APP ===
collections = client.list_collections()

if not collections:
    st.error("❌ Could not connect to Chroma. Check API credentials.")
    st.stop()

# Header
h1, h2 = st.columns([6, 1])
with h1:
    st.markdown("### ◈ Chroma Signal")
with h2:
    selected = st.selectbox("Collection", collections, label_visibility="collapsed")

all_df = load_all_data(selected)
src_col = 'source_channel' if 'source_channel' in all_df.columns else 'source' if 'source' in all_df.columns else None

# Stats
s1, s2, s3, s4, s5 = st.columns(5)
s1.metric("Records", len(all_df))
s2.metric("Companies", all_df['company_name'].nunique() if 'company_name' in all_df.columns else 0)
s3.metric("Vector DBs", all_df['vector_db_used'].nunique() if 'vector_db_used' in all_df.columns else 0)
s4.metric("Types", all_df['category'].nunique() if 'category' in all_df.columns else 0)
s5.metric("Sources", all_df[src_col].nunique() if src_col else 0)

st.markdown("---")

# Search
search_col, clear_col = st.columns([6, 1])
with search_col:
    query = st.text_input("Search", placeholder="🔍 Semantic search...", label_visibility="collapsed")
with clear_col:
    if st.button("Clear", use_container_width=True):
        st.rerun()

# Filters
st.markdown("<p style='font-size:0.8rem; color:#737373; margin: 1rem 0 0.5rem 0; font-weight:500;'>FILTERS</p>", unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns(4)

def get_options_with_counts(df, col):
    if col not in df.columns:
        return []
    counts = df[col].value_counts()
    return [f"{val} ({count})" for val, count in counts.items()]

def extract_value(option):
    if '(' in option:
        return option.rsplit(' (', 1)[0]
    return option

with f1:
    cat_options = get_options_with_counts(all_df, 'category')
    cat_selected = st.multiselect("Type", cat_options, placeholder="All types")
with f2:
    db_options = get_options_with_counts(all_df, 'vector_db_used')
    db_selected = st.multiselect("Vector DB", db_options, placeholder="All databases")
with f3:
    src_options = get_options_with_counts(all_df, src_col) if src_col else []
    src_selected = st.multiselect("Source", src_options, placeholder="All sources") if src_options else []
with f4:
    company_filter = st.text_input("Company", placeholder="Filter by name...", label_visibility="visible")

# Apply search
if query:
    metadatas, distances = client.query(selected, query, n_results=200)
    if metadatas:
        df = pd.DataFrame(metadatas)
        df.insert(0, 'relevance', [f"{max(0,1-d)*100:.0f}%" for d in distances])
    else:
        df = pd.DataFrame()
else:
    df = all_df.copy()

# Apply filters
if not df.empty:
    if cat_selected:
        df = df[df['category'].isin([extract_value(x) for x in cat_selected])]
    if db_selected:
        df = df[df['vector_db_used'].isin([extract_value(x) for x in db_selected])]
    if src_selected and src_col:
        df = df[df[src_col].isin([extract_value(x) for x in src_selected])]
    if company_filter:
        df = df[df['company_name'].str.contains(company_filter, case=False, na=False)]

# Results
st.markdown(f"<p class='text-muted' style='margin:0.5rem 0;'>Showing <b>{len(df)}</b> of {len(all_df)} records</p>", unsafe_allow_html=True)

if not df.empty:
    st.dataframe(format_df(df), use_container_width=True, height=380, hide_index=True)
    c1, c2, c3, _ = st.columns([1, 1, 1, 5])
    c1.download_button("📥 CSV", format_df(df).to_csv(index=False), f"{selected}.csv")
    c2.download_button("📥 JSON", format_df(df).to_json(orient='records'), f"{selected}.json")
    with c3:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()
else:
    st.info("No results match your filters")

# Insights
st.markdown("---")
st.markdown("<p class='section-title'>Insights</p>", unsafe_allow_html=True)

if not df.empty:
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        if 'vector_db_used' in df.columns:
            counts = df['vector_db_used'].value_counts().head(8)
            fig = px.pie(values=counts.values, names=counts.index, hole=0.5, color_discrete_sequence=px.colors.qualitative.Set2, title="Vector DB")
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(margin=dict(t=40, b=20, l=20, r=20), height=280, showlegend=False, title_x=0.5, title_font_size=14)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with c2:
        if 'category' in df.columns:
            counts = df['category'].value_counts()
            fig = px.pie(values=counts.values, names=counts.index, hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel, title="Type")
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(margin=dict(t=40, b=20, l=20, r=20), height=280, showlegend=False, title_x=0.5, title_font_size=14)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with c3:
        if src_col and src_col in df.columns:
            counts = df[src_col].value_counts().head(6)
            fig = px.bar(x=counts.values, y=counts.index, orientation='h', color=counts.index, color_discrete_sequence=px.colors.qualitative.Safe, title="Source")
            fig.update_traces(texttemplate='%{x}', textposition='outside')
            fig.update_layout(margin=dict(t=40, b=20, l=20, r=20), height=280, showlegend=False, title_x=0.5, title_font_size=14, xaxis_title="", yaxis_title="", yaxis=dict(categoryorder='total ascending'))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with c4:
        if 'industry' in df.columns:
            counts = df['industry'].dropna().value_counts().head(6)
            if not counts.empty:
                fig = px.bar(x=counts.values, y=counts.index, orientation='h', color=counts.index, color_discrete_sequence=px.colors.qualitative.Vivid, title="Industry")
                fig.update_traces(texttemplate='%{x}', textposition='outside')
                fig.update_layout(margin=dict(t=40, b=20, l=20, r=20), height=280, showlegend=False, title_x=0.5, title_font_size=14, xaxis_title="", yaxis_title="", yaxis=dict(categoryorder='total ascending'))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

