import plotly.express as px
import pydeck as pdk
import streamlit as st


url = 'https://factpages.npd.no/ReportServer_npdpublic?/FactPages/tableview/wellbore_development_all&rs:Command=Render&rc:Toolbar=false&rc:Parameters=f&IpAddress=not_used&CultureCode=en&rs:Format=CSV&Top100=false'
fields_url = 'https://factpages.npd.no/ReportServer_npdpublic?/FactPages/tableview/field_activity_status_hst&rs:Command=Render&rc:Toolbar=false&rc:Parameters=f&IpAddress=not_used&CultureCode=en&rs:Format=CSV&Top100=false'

colors={'Blues':px.colors.sequential.Blues,
        'RdPu':px.colors.sequential.RdPu, 
        'Burgyl':px.colors.sequential.Burgyl,
        'BuGn':px.colors.sequential.BuGn,
        'BuPu':px.colors.sequential.BuPu,
        'algae':px.colors.sequential.algae,
         }

        
map_style = {'Carto Dark':pdk.map_styles.CARTO_DARK,
             'Carto Light':pdk.map_styles.CARTO_LIGHT,
             'Carto Road':pdk.map_styles.CARTO_ROAD,
             'Mapbox Light':pdk.map_styles.MAPBOX_LIGHT,
             'Mapbox Dark':pdk.map_styles.MAPBOX_DARK,
             'Mapbox Light':pdk.map_styles.MAPBOX_ROAD,
             'Mapbox Satellite':pdk.map_styles.MAPBOX_SATELLITE,
             }

def initialize_states():
    if 'map_bar_color_def' not in st.session_state:
        st.session_state.map_bar_color_def = '#FFFFFF'
    if 'map_text_color_def' not in st.session_state:
        st.session_state.map_text_color_def = '#F7B000'
    if 'map_theme' not in st.session_state:
        st.session_state.map_theme = list(map_style.keys())[-1]