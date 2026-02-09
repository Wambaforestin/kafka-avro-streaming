import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, UTC
import os
import time

# Configuration Page
st.set_page_config(
    page_title="Kafka Analytics",
    layout="wide"
)

# Configuration MongoDB
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = 'streaming_db'
COLLECTION_NAME = 'events'

# Connexion MongoDB
@st.cache_resource
def get_mongo_client():
    return pymongo.MongoClient(MONGO_URI)

# Connexion MongoDB
@st.cache_resource
def get_mongo_client():
    return pymongo.MongoClient(MONGO_URI)

def get_data():
    client = get_mongo_client()
    collection = client[DB_NAME][COLLECTION_NAME]
    data = list(collection.find().sort("received_at", -1).limit(5000))
    
    if data:
        df = pd.DataFrame(data)
        if 'received_at' in df.columns:
            df['received_at'] = pd.to_datetime(df['received_at'])
        return df
    return pd.DataFrame()

# Header
st.markdown("# Kafka-Avro Dashboard")
st.markdown("**Real-time Event Stream Analytics**")
st.markdown("---")

# Récupération données
df = get_data()

if df.empty:
    st.warning("Aucune donnée. Lancez le producer et consumer.")
    st.stop()

# KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Événements", f"{len(df):,}")

with col2:
    unique_users = df['user_id'].nunique() if 'user_id' in df.columns else 0
    st.metric("Utilisateurs Uniques", unique_users)

with col3:
    v2_pct = (len(df[df['schema_version'] == 'v2']) / len(df) * 100) if len(df) > 0 else 0
    st.metric("Adoption V2", f"{v2_pct:.1f}%")

with col4:
    if 'event_type' in df.columns:
        peak = df['event_type'].mode()[0] if len(df) > 0 else "N/A"
        st.metric("Action Principale", peak)

st.markdown("---")

# Graphiques
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Événements par Minute")
    if 'received_at' in df.columns:
        df_time = df.copy()
        df_time['minute'] = df_time['received_at'].dt.floor('1min')
        time_series = df_time.groupby('minute').size().reset_index(name='count')
        
        fig = px.line(time_series, x='minute', y='count', 
                     labels={'minute': 'Temps', 'count': 'Événements'})
        fig.update_traces(line_color='#1f77b4', line_width=2)
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Types d'Événements")
    if 'event_type' in df.columns:
        event_counts = df['event_type'].value_counts().reset_index()
        event_counts.columns = ['Type', 'Count']
        
        fig = px.pie(event_counts, values='Count', names='Type', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("Browsers (V2 vs V1)")
    if 'browser' in df.columns:
        browser_data = df.copy()
        browser_data['browser_display'] = browser_data['browser'].fillna('V1 (sans browser)')
        browser_counts = browser_data['browser_display'].value_counts().reset_index()
        browser_counts.columns = ['Browser', 'Count']
        
        fig = px.bar(browser_counts, x='Browser', y='Count', 
                    color='Count', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)

with col_right2:
    st.subheader("Devices")
    if 'metadata' in df.columns:
        devices = df['metadata'].apply(lambda x: x.get('device') if isinstance(x, dict) else None)
        devices = devices.dropna()
        
        if len(devices) > 0:
            device_counts = devices.value_counts().reset_index()
            device_counts.columns = ['Device', 'Count']
            
            fig = px.bar(device_counts, x='Device', y='Count',
                        color='Device')
            st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Tableau
st.subheader("Derniers Événements")
display_cols = ['user_id', 'event_type', 'schema_version', 'received_at']
if 'browser' in df.columns:
    display_cols.append('browser')

available_cols = [col for col in display_cols if col in df.columns]
recent = df[available_cols].head(20).copy()

if 'received_at' in recent.columns:
    recent['received_at'] = recent['received_at'].dt.strftime('%Y-%m-%d %H:%M:%S')

st.dataframe(recent, use_container_width=True)

# Auto-refresh
if st.sidebar.checkbox("Auto-refresh (5s)", value=False):
    time.sleep(5)
    st.rerun()
