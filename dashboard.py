import warnings
warnings.filterwarnings('ignore')

import openpyxl
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

st.set_page_config(page_title="Agro Intelligence — SLCE3", layout="wide")

@st.cache_data
def load_data():
    wb = openpyxl.load_workbook('dados.xlsx', read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    df = pd.DataFrame(rows[1:], columns=rows[0])
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values('data').reset_index(drop=True)
    num_cols = [
        'preco_abertura','preco_maximo','preco_minimo','preco_fechamento',
        'volume','retorno_diario','media_movel_7d','temperatura_media',
        'temperatura_maxima','temperatura_minima','precipitacao_mm',
        'velocidade_vento','chuva_acumulada_7d','precipitacao_lag_7d'
    ]
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')
    df['drawdown'] = ((df['preco_fechamento'] - df['preco_fechamento'].cummax()) / df['preco_fechamento'].cummax() * 100).round(4)
    df['volatilidade_7d'] = df['retorno_diario'].rolling(7).std() * 100
    df['month_name'] = df['mes'].map({1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun'})
    return df

df = load_data()

CLIMATE_VARS = {
    'temperatura_media':   'Avg Temperature (°C)',
    'temperatura_maxima':  'Max Temperature (°C)',
    'temperatura_minima':  'Min Temperature (°C)',
    'precipitacao_mm':     'Daily Rainfall (mm)',
    'chuva_acumulada_7d':  '7d Accumulated Rain (mm)',
    'precipitacao_lag_7d': 'Rainfall Lag 7d (mm)',
    'velocidade_vento':    'Wind Speed (km/h)',
}

MONTHS = {0:'All Periods', 1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June'}
CFG = dict(use_container_width=True, config={'displayModeBar': False})
H = 320

with st.sidebar:
    st.markdown("### **Market Intelligence**")
    st.caption("Asset: SLCE3 (SLC Agrícola)")
    st.divider()
    page = st.radio("Navigation", ["Market Overview", "Climate Impact", "Statistical Correlation", "Dataset Explorer"],
                    label_visibility="collapsed")
    st.divider()
    st.markdown("**Timeframe Filter**")
    month_label = st.pills("Period", list(MONTHS.values()), default="All Periods", label_visibility="collapsed")
    month_sel = [k for k, v in MONTHS.items() if v == month_label][0] if month_label else 0
    st.divider()
    st.caption("Developed by Gabriel Pires")

df_v = df if month_sel == 0 else df[df['mes'] == month_sel].copy()

if len(df_v) < 2:
    st.warning("Insufficient data for the selected period.")
    st.stop()

monthly = df.groupby('mes').agg(
    month=('month_name','first'),
    avg_price=('preco_fechamento','mean'),
    total_volume=('volume','sum'),
    total_rain=('precipitacao_mm','sum'),
    avg_temp=('temperatura_media','mean'),
    avg_drawdown=('drawdown','mean')
).reset_index()

period_desc = MONTHS[month_sel] if month_sel != 0 else "H1 2025 (Jan–Jun)"

if page == "Market Overview":
    st.title("Executive Summary — SLCE3")
    st.caption(f"Analysis Period: {period_desc} · {len(df_v)} Trading Sessions")

    change = ((df_v.iloc[-1]['preco_fechamento'] / df_v.iloc[0]['preco_fechamento']) - 1) * 100
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Current Price",    f"R$ {df_v.iloc[-1]['preco_fechamento']:.2f}")
    c2.metric("Period Return",    f"{change:+.2f}%", delta=f"{change:+.2f}%")
    c3.metric("Max Drawdown",     f"{df_v['drawdown'].min():.2f}%")
    c4.metric("Volatility (SD)",  f"{df_v['retorno_diario'].std()*100:.2f}%")
    c5.metric("Peak Daily Gain",  f"{df_v['retorno_diario'].max()*100:+.2f}%")
    c6.metric("Peak Daily Loss",  f"{df_v['retorno_diario'].min()*100:+.2f}%")

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_v['data'], y=df_v['preco_fechamento'],
        name='Close Price', line=dict(width=2, color='#1f77b4')))
    fig1.add_trace(go.Scatter(x=df_v['data'], y=df_v['media_movel_7d'],
        name='7d Moving Average', line=dict(dash='dash', width=1.5, color='#2ca02c')))
    fig1.update_layout(title='Price Action & 7-Day Moving Average',
        hovermode='x unified', height=H, xaxis_title='', yaxis_title='Price (BRL)')
    st.plotly_chart(fig1, **CFG)

    col1, col2 = st.columns(2)
    with col1:
        colors = ['#2ca02c' if v >= 0 else '#d62728' for v in df_v['retorno_diario'].fillna(0)]
        fig2 = go.Figure(go.Bar(x=df_v['data'], y=df_v['retorno_diario']*100, marker_color=colors))
        fig2.update_layout(title='Daily Performance (%)', height=H, xaxis_title='', yaxis_title='Percentage Change')
        st.plotly_chart(fig2, **CFG)

    with col2:
        fig3 = go.Figure(go.Scatter(x=df_v['data'], y=df_v['drawdown'],
            fill='tozeroy', line=dict(color='#d62728', width=2),
            fillcolor='rgba(214,39,40,0.1)', name='Drawdown'))
        fig3.update_layout(title='Equity Drawdown Profile (%)', height=H, xaxis_title='', yaxis_title='Drawdown %')
        st.plotly_chart(fig3, **CFG)

    col1, col2 = st.columns(2)
    with col1:
        fig4 = px.bar(monthly, x='month', y='total_volume', title='Monthly Trading Volume',
            labels={'month':'Month','total_volume':'Total Volume'})
        fig4.update_layout(height=H)
        st.plotly_chart(fig4, **CFG)
    with col2:
        fig5 = px.bar(monthly, x='month', y='avg_price', title='Average Price by Month',
            labels={'month':'Month','avg_price':'Price (BRL)'})
        fig5.update_layout(height=H)
        st.plotly_chart(fig5, **CFG)

elif page == "Climate Impact":
    st.title("Climate Variable Analysis")
    st.caption(f"Regional Data: Sorriso, MT · Reporting Period: {period_desc}")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Mean Temperature",    f"{df_v['temperatura_media'].mean():.1f}°C")
    c2.metric("Recorded Peak Temp",  f"{df_v['temperatura_maxima'].max():.1f}°C")
    c3.metric("Cumulative Rainfall", f"{df_v['precipitacao_mm'].sum():.0f} mm")
    c4.metric("Mean Daily Rain",     f"{df_v['precipitacao_mm'].mean():.1f} mm")

    var_sel = st.selectbox("Select Climate Metric for Price Comparison:",
        list(CLIMATE_VARS.keys()), format_func=lambda x: CLIMATE_VARS[x])

    fig6 = make_subplots(specs=[[{'secondary_y': True}]])
    fig6.add_trace(go.Scatter(x=df_v['data'], y=df_v['preco_fechamento'],
        name='Stock Price', line=dict(width=2, color='#1f77b4')), secondary_y=False)
    fig6.add_trace(go.Scatter(x=df_v['data'], y=df_v[var_sel],
        name=CLIMATE_VARS[var_sel], line=dict(width=1.5, color='#ff7f0e')), secondary_y=True)
    fig6.update_layout(title=f'Overlay: {CLIMATE_VARS[var_sel]} vs. Close Price',
        hovermode='x unified', height=H)
    fig6.update_yaxes(title_text='Price (BRL)', secondary_y=False)
    fig6.update_yaxes(title_text=CLIMATE_VARS[var_sel], secondary_y=True)
    st.plotly_chart(fig6, **CFG)

    col1, col2 = st.columns(2)
    with col1:
        fig7 = make_subplots(specs=[[{'secondary_y': True}]])
        fig7.add_trace(go.Scatter(x=df_v['data'], y=df_v['preco_fechamento'],
            name='Price', line=dict(width=2, color='#1f77b4')), secondary_y=False)
        fig7.add_trace(go.Bar(x=df_v['data'], y=df_v['precipitacao_mm'],
            name='Rainfall (mm)', marker_color='rgba(31,119,180,0.3)'), secondary_y=True)
        fig7.add_trace(go.Scatter(x=df_v['data'], y=df_v['chuva_acumulada_7d'],
            name='7d Accum. Rain', line=dict(dash='dot', color='#2ca02c', width=1.5)), secondary_y=True)
        fig7.update_layout(title='Rainfall Dynamics vs. Asset Valuation', hovermode='x unified', height=H)
        fig7.update_yaxes(title_text='Price (BRL)', secondary_y=False)
        fig7.update_yaxes(title_text='Precipitation (mm)', secondary_y=True)
        st.plotly_chart(fig7, **CFG)

    with col2:
        sub = df_v[[var_sel,'preco_fechamento']].dropna()
        if len(sub) > 2:
            x, y = sub[var_sel].values, sub['preco_fechamento'].values
            m, b = np.polyfit(x, y, 1)
            xl = np.linspace(x.min(), x.max(), 100)
            fig8 = px.scatter(sub, x=var_sel, y='preco_fechamento',
                labels={var_sel:CLIMATE_VARS[var_sel],'preco_fechamento':'Price (BRL)'},
                title=f'Linear Regression: {CLIMATE_VARS[var_sel].split("(")[0].strip()} Effect')
            fig8.add_trace(go.Scatter(x=xl, y=m*xl+b, mode='lines', name='Trendline',
                line=dict(color='black', dash='dash', width=1.5)))
            fig8.update_layout(height=H)
            st.plotly_chart(fig8, **CFG)

    col1, col2 = st.columns(2)
    with col1:
        fig9 = px.bar(monthly, x='month', y='avg_temp', title='Avg Temperature by Month (°C)',
            labels={'month':'Month','avg_temp':'°C'})
        fig9.update_layout(height=H)
        st.plotly_chart(fig9, **CFG)
    with col2:
        fig10 = px.bar(monthly, x='month', y='total_rain', title='Total Rainfall by Month (mm)',
            labels={'month':'Month','total_rain':'mm'})
        fig10.update_layout(height=H)
        st.plotly_chart(fig10, **CFG)

    fig11 = make_subplots(specs=[[{'secondary_y': True}]])
    fig11.add_trace(go.Scatter(x=df_v['data'], y=df_v['volatilidade_7d'],
        name='7d Volatility (%)', line=dict(color='#ff7f0e', width=2)), secondary_y=False)
    fig11.add_trace(go.Scatter(x=df_v['data'], y=df_v['chuva_acumulada_7d'],
        name='7d Accum. Rain (mm)', line=dict(color='#1f77b4', dash='dot', width=1.5)), secondary_y=True)
    fig11.update_layout(title='7d Volatility vs Accumulated Rain — Climate × Risk',
        hovermode='x unified', height=H)
    fig11.update_yaxes(title_text='Volatility (%)', secondary_y=False)
    fig11.update_yaxes(title_text='Rain (mm)', secondary_y=True)
    st.plotly_chart(fig11, **CFG)

elif page == "Statistical Correlation":
    st.title("Cross-Asset Correlation Matrix")
    st.caption("Quantifying the statistical relationship between Climate and Market performance.")

    corr_rows = []
    for col, label in CLIMATE_VARS.items():
        sub = df_v[[col,'preco_fechamento','retorno_diario']].dropna()
        if len(sub) < 5:
            continue
        r_p, p_p = stats.pearsonr(sub[col], sub['preco_fechamento'])
        r_r, _   = stats.pearsonr(sub[col], sub['retorno_diario'])
        abs_r = abs(r_p)
        strength = 'Negligible' if abs_r<0.1 else 'Weak' if abs_r<0.3 else 'Moderate' if abs_r<0.5 else 'Strong'
        corr_rows.append({
            'Metric': label.split('(')[0].strip(),
            'Pearson r (Price)': round(r_p,4),
            'Pearson r (Return)': round(r_r,4),
            'p-value': round(p_p,4),
            'Strength': strength,
            'Sentiment': 'Positive' if r_p>0 else 'Negative'
        })

    df_corr = pd.DataFrame(corr_rows).sort_values('Pearson r (Price)', key=abs, ascending=False)
    top = df_corr.iloc[0]

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Primary Driver",       top['Metric'])
    c2.metric("Coefficient (r)",      f"{top['Pearson r (Price)']:+.4f}")
    c3.metric("Assessed Strength",    top['Strength'])
    c4.metric("Statistical Sig. (p)", f"{top['p-value']:.4f}")

    df_ord = df_corr.sort_values('Pearson r (Price)')
    colors = ['#d62728' if v < 0 else '#2ca02c' for v in df_ord['Pearson r (Price)']]

    col1, col2 = st.columns([3,2])
    with col1:
        fig12 = go.Figure(go.Bar(
            x=df_ord['Pearson r (Price)'], y=df_ord['Metric'], orientation='h',
            marker_color=colors,
            text=df_ord['Pearson r (Price)'].apply(lambda v: f'{v:+.4f}'),
            textposition='outside'
        ))
        fig12.update_layout(title='Correlation Coefficients: Climate vs. Valuation',
            xaxis=dict(range=[-0.8,0.8]), height=H)
        st.plotly_chart(fig12, **CFG)
    with col2:
        st.markdown("**Detailed Statistics**")
        st.dataframe(df_corr.set_index('Metric'), use_container_width=True, height=H)

    st.divider()
    st.markdown("### Key Analytical Findings")

    r_rain = df_corr[df_corr['Metric'].str.contains('Daily')]['Pearson r (Price)'].values
    r_lag  = df_corr[df_corr['Metric'].str.contains('Lag')]['Pearson r (Price)'].values
    dd_jun = monthly[monthly['mes']==6]['avg_drawdown'].values

    findings = {
        "Dominant Climate Factor":   f"{top['Metric']} (r={top['Pearson r (Price)']}) — {top['Strength']} {top['Sentiment']}",
        "Precipitation Sensitivity": f"r={r_rain[0]:+.4f} — Inverse relationship noted" if len(r_rain) else "N/A",
        "Temporal Lag Analysis":     f"r lag 7d={r_lag[0]:+.4f} — Reactiveness is near-immediate" if len(r_lag) else "N/A",
        "Risk Profile (Seasonality)":f"Avg drawdown in June: {dd_jun[0]:.1f}% (semi-annual peak risk)" if len(dd_jun) else "N/A",
        "Volatility Index":          f"{df_v['retorno_diario'].std()*100:.2f}% standard deviation in daily returns",
    }

    for k, v in findings.items():
        c1, c2 = st.columns([2,3])
        c1.markdown(f"**{k}**")
        c2.write(v)

elif page == "Dataset Explorer":
    st.title("Source Data Explorer")
    st.caption(f"Full Dataset Access · {len(df_v)} Records for {period_desc}")

    col1, col2 = st.columns(2)
    with col1:
        search = st.text_input("Filter Results", placeholder="Search by month, price or condition...")
    with col2:
        col_sel = st.multiselect("Data Points", list(df_v.columns),
            default=['data','month_name','preco_fechamento','retorno_diario',
                     'volume','temperatura_media','precipitacao_mm','drawdown'])

    df_tab = df_v.copy()
    if search:
        mask = df_tab.astype(str).apply(
            lambda c: c.str.contains(search, case=False, na=False)
        ).any(axis=1)
        df_tab = df_tab[mask]

    cols_show = [c for c in col_sel if c in df_tab.columns]
    if cols_show:
        df_tab = df_tab[cols_show]

    st.caption(f"Showing {len(df_tab)} filtered entries")
    st.dataframe(df_tab.reset_index(drop=True), use_container_width=True, height=480)

    csv = df_tab.to_csv(index=False).encode('utf-8')
    st.download_button("Download Report (CSV)", csv, "slce3_market_climate_report.csv", "text/csv")
