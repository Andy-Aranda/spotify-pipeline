# scripts/visualizations.py
import plotly.graph_objects as go

def generar_top_tracks(df):
    top_tracks = df.groupby("track_name")["popularity"].mean().sort_values(ascending=False).head(10)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top_tracks.index,
        y=top_tracks.values,
        marker_color=['#1DB954', '#1ED760', '#1AA34A', '#18A558', '#149E5C', '#128C63', '#0F7A6F', '#0B5F73', '#064B6D', '#003C5E']
    ))

    fig.update_layout(
        title="Top Tracks por Popularidad",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#FFFFFF")
    )

    return fig.to_html(full_html=False)


import plotly.express as px

def generar_popularidad_artistas(df_tracks):
    artistas_df = (
        df_tracks
        .explode('artists')  # si guardaste los artistas como lista
        .groupby('artists')['popularity']
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        artistas_df,
        x='artists',
        y='popularity',
        title='Artistas más escuchados por popularidad',
        color='artists',
        template='plotly_dark'
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )

    return fig.to_html(full_html=False)
