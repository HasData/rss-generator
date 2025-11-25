import streamlit as st
import urllib.parse
import pandas as pd
import feedparser
from io import BytesIO, StringIO

st.set_page_config(page_title="Google News Scraper", layout="wide")

st.markdown("<h1 style='text-align: center;'>Google News RSS Generator & Exporter</h1>", unsafe_allow_html=True)

col4, col5 = st.columns([1, 1], gap="small")

time_options = {
    "Any time": "",
    "Last 1 hour": "when:1h",
    "Last 12 hours": "when:12h",
    "Last 1 day": "when:1d",
    "Last 7 days": "when:7d"
}

with col4:
    hl = st.selectbox("Interface Language (hl)", ["en-US", "en-GB", "fr-FR", "de-DE"], index=0)
    site_filter = st.text_input("Site filter (optional)", value="", placeholder="Enter site, e.g., bbc.com")
    exclude_word = st.text_input("Exclude word (optional)", value="", placeholder="Word to exclude, e.g., -rumor")


with col5:
    gl = st.selectbox("Region (gl)", ["US", "GB", "FR", "DE", "IN"], index=0)
    time_label = st.selectbox("Time filter", list(time_options.keys()))
    time_filter = time_options[time_label]
    exact_phrase = st.text_input("Exact phrase (optional)", value="", placeholder='Exact phrase, e.g., "new release"')


ceid = f"{gl}:{hl.split('-')[0]}"

keyword = st.text_input("Keyword", value="", placeholder="Enter main keyword, e.g., tech")

query_parts = [keyword] if keyword else []
if site_filter:
    query_parts.append(f"site:{site_filter}")
if time_filter:
    query_parts.append(time_filter)
if exclude_word:
    query_parts.append(exclude_word)
if exact_phrase:
    query_parts.append(exact_phrase)

query = " ".join(part for part in query_parts if part)
encoded_query = urllib.parse.quote(query)
encoded_ceid = urllib.parse.quote(ceid)

base_url = "https://news.google.com/rss/search"
rss_url = f"{base_url}?q={encoded_query}&hl={hl}&gl={gl}&ceid={encoded_ceid}"

st.subheader("Generated RSS URL")
st.code(rss_url)
st.markdown(f"[Open RSS feed]({rss_url})")

feed = feedparser.parse(rss_url)
items = []
for entry in feed.entries:
    items.append({
        "title": entry.get("title", ""),
        "link": entry.get("link", ""),
        "pubDate": entry.get("published", ""),
        "source": entry.get("source", {}).get("title", "") if entry.get("source") else "",
        "description": entry.get("description", "")
    })

df = pd.DataFrame(items)

st.subheader("RSS Items")
st.dataframe(df)

st.subheader("Export RSS Data")


col1, col2, col3 = st.columns([1, 1, 1], gap="small")

with col1:
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="Download CSV",
        data=csv_buffer.getvalue(),
        file_name="rss_feed.csv",
        mime="text/csv"
    )
with col2:
    json_buffer = df.to_json(orient="records", force_ascii=False)
    st.download_button(
        label="Download JSON",
        data=json_buffer,
        file_name="rss_feed.json",
        mime="application/json"
    )

with col3:
    xlsx_buffer = BytesIO()
    with pd.ExcelWriter(xlsx_buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="RSS Feed")
    st.download_button(
        label="Download XLSX",
        data=xlsx_buffer.getvalue(),
        file_name="rss_feed.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
