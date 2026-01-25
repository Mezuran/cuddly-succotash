import streamlit as st
import folium
from streamlit_folium import st_folium

def render_map(df):
    st.caption("Sebaran lokasi penjual.")
    
    map_data = df['Provinsi'].value_counts().reset_index()
    map_data.columns = ['propinsi', 'count']
    
    m = folium.Map(location=[-2.5489, 118.0149], zoom_start=4)
    geojson_url = "https://raw.githubusercontent.com/ans-4175/peta-indonesia-geojson/refs/heads/master/indonesia-prov.geojson"
    
    if not map_data.empty:
        folium.Choropleth(
            geo_data=geojson_url,
            name="choropleth",
            data=map_data,
            columns=["propinsi", "count"],
            key_on="feature.properties.Propinsi",
            fill_color="YlOrRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            nan_fill_color="white"
        ).add_to(m)
        
    st_folium(m, use_container_width=True, height=500, returned_objects=[])