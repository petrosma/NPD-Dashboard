from altair.vegalite.v4.schema.core import DateTime
from numpy.ma.core import count
import pandas as pd
import streamlit as st 
from st_aggrid import AgGrid
import numpy as np
import pydeck as pdk
from pydeck.types import String
import plotly.express as px
from PIL import ImageColor
from constants import url, fields_url, colors, map_style
from datetime import date, datetime as dt 

pd.options.mode.chained_assignment = None  

@st.cache(show_spinner=False, suppress_st_warning=True, allow_output_mutation=True, persist=True)
def get_data(url):
    return pd.read_csv(url,encoding='utf-8')


def prepare_df():
    df = get_data(url)
    df.dropna(subset=['wlbField'], inplace=True)
    df = df.rename(columns={'wlbNsDecDeg':'lat', 'wlbEwDesDeg':'lon'})
    df = df[['wlbField', 'wlbWell', 'wlbWellboreName','wlbDrillingOperator',
    'wlbPurpose','wlbStatus', 'lat', 'lon', 'wlbPurposePlanned', 'wlbContent', 'wlbWellType', 'wlbContentPlanned']]
    return df

def map_overview(df: pd.DataFrame,colname:str, zoom, map_text_color, map_bar_color, map_theme):
    df= df[[colname, 'wlbField', 'lat', 'lon']]
    if colname == 'wlbWellboreName':
        df.drop_duplicates(subset=colname, keep='first', inplace=True)
        df['count']= df.groupby('wlbField')[colname].transform(count)
        df = df.drop_duplicates(subset='wlbField', keep='first')
       
    elif colname == 'wlbWell':
        df.drop_duplicates(subset=colname, keep='first', inplace=True)
        df['count'] = df.groupby('wlbField')[colname].transform(count)
        df = df.drop_duplicates(subset='wlbField', keep='first')
       
    elif colname == 'wlbDrillingOperator':
        df['field_operator'] = df['wlbField'].astype('str') + df[colname].astype('str')
        df.drop_duplicates(subset='field_operator', keep='first', inplace=True)
        df['count'] = df.groupby('wlbField')[colname].transform(count)
        df = df.drop_duplicates(subset='wlbField', keep='first')
    else:
        return None
      
    scale = float(df['count'].min() * 5000) if float(df['count'].max()) < 10 else 200
    map = pdk.Deck(
        map_style=map_style[map_theme], 
        initial_view_state={
            'latitude':np.average(df['lat']),
            'longitude':np.average(df['lon']),
            'zoom':zoom,
            'pitch':50
        }, 
       
        layers=[
            pdk.Layer(
                'ColumnLayer', 
                data=df, 
                get_position=['lon', 'lat'],
                get_elevation = 'count', 
                radius=1000, 
                get_color = ImageColor.getrgb(map_bar_color),
                elevation_scale = scale,
                pickable = True, 
                auto_highlight = True
                ), 

            pdk.Layer(
                "TextLayer",
                data = df,
                pickable=False,
                get_position=['lon', 'lat'],
                get_text="wlbField",
                get_size=15,
                get_color=ImageColor.getrgb(map_text_color),
                get_angle=20,
                get_text_anchor=String("start"),
                get_alignment_baseline=String("top")
            )
        ],
    )
    return map

def pie_chart(df:pd.DataFrame, colname:str, colvalue:str,title:str, color_style):
    dp= df.groupby(colname).count()
    dp['argument'] = dp.index
    dp['count'] = dp[colvalue]
    fig = px.pie(dp, values='count', names='argument', title=title,
    color_discrete_sequence=colors[color_style])
    return fig

def content(df):
    map_set_expander = st.sidebar.expander('Map Settings', expanded=True)
    with map_set_expander:
        col1, col2 , col3= st.columns((1,1,3))
        with col1:
            map_text_color = st.color_picker('Text Color', value=st.session_state.map_text_color_def)
            st.session_state.map_text_color_def = map_text_color
        with col2:
            map_bar_color = st.color_picker('Bar Color', value = st.session_state.map_bar_color_def)
            st.session_state.map_bar_color_def = map_bar_color
        with col3:
            map_theme = st.selectbox('Map Theme', options=map_style.keys(), index = list(map_style.keys()).index(st.session_state.map_theme))
    
    pie_set_expander = st.sidebar.expander('Pie Chart Settings:', expanded=True)
    with pie_set_expander:
        color_style = st.selectbox('select color:', options=colors.keys())

    map_expander = st.expander(label='Map Overview', expanded=True)
    with map_expander:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write('Number of Wells')
            st.write(map_overview(df, 'wlbWell', 4, map_text_color, map_bar_color, map_theme))
        with col2:
            st.write('Number of Wellbores')
            st.write(map_overview(df, 'wlbWellboreName', 4,map_text_color, map_bar_color, map_theme))
        with col3:
            st.write('Number of Drilling Operators')
            st.write(map_overview(df, 'wlbDrillingOperator', 4,map_text_color, map_bar_color, map_theme))

    pie_expander = st.expander(label='Pie Charts - Well Status & Purpose', expanded=True)
    with pie_expander:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(pie_chart(df, 'wlbStatus', 'wlbWell','Wellbore Status', color_style), use_container_width=True)
        with col2:
            st.plotly_chart(pie_chart(df, 'wlbPurpose','wlbWell' ,'Wellbore Purpose', color_style), use_container_width=True)

    pie_expander1 = st.expander(label='Pie Charts - Well Fluid', expanded=True)
    with pie_expander1:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(pie_chart(df, 'wlbContent', 'wlbWell','Fluid Content', color_style), use_container_width=True)
        with col2:
            st.plotly_chart(pie_chart(df, 'wlbContentPlanned', 'wlbWell','Fluid Content Planned', color_style), use_container_width=True)
    
    timeline_expander = st.expander('Field Status Timeline & Pie Chart', expanded=True)

    with timeline_expander:
        df_fields = get_data(fields_url).copy()
        df_fields['fldStatusToDate'] = df_fields['fldStatusToDate'].apply(lambda x:dt.today().strftime('%d.%m.%Y') if len(str(x))<10 else x)
        df_fields['fldStatusToDate'] = pd.to_datetime(df_fields['fldStatusToDate'])
        df_fields['fldStatusFromDate'] = pd.to_datetime(df_fields['fldStatusFromDate'])

        fig = px.timeline(df_fields, x_start = 'fldStatusFromDate', x_end='fldStatusToDate', y='fldName',title='Field Status Timeline',
                          text = 'fldStatus', color='fldStatus', height=700, facet_col_spacing=0.2, 
                          labels={'fldName':'Field Name', 'fldStatus':'Field Status', 'fldStatusFromDate':'From', 'fldStatusToDate':'To'}
                          ,color_discrete_map={'Approved for production':'Blue','Producing':'Green','Shut down':'Red'}
                          )
        st.plotly_chart(fig, use_container_width=True)
        dp1 = df_fields[df_fields['fldStatusToDate'].dt.date == dt.today().date()]
        st.plotly_chart(pie_chart(dp1, 'fldStatus', 'fldName','Current Field Status', color_style), use_container_width=True)
     
def detail_view(df: pd.DataFrame):
    field = st.sidebar.selectbox('Field: ', options=df['wlbField'].unique())
    operators = st.sidebar.multiselect('Drilling Operators: ', 
    options = df[df['wlbField'] == field]['wlbDrillingOperator'].unique(), 
    default=df[df['wlbField'] == field]['wlbDrillingOperator'].unique())
    df = df[df['wlbDrillingOperator'].isin(operators) & df['wlbField'].isin([field])]
    df = df[['wlbField', 'wlbWell', 'wlbWellboreName', 'wlbStatus', 'wlbPurpose']]
    AgGrid(df)
    st.download_button('Download data', data = df.to_csv().encode('utf-8'), file_name='data.csv', mime='text/csv')

def sidebar():
    st.set_page_config(layout='wide')
    view = st.sidebar.radio('Choose Main View:', options=['Overview', 'Detail View'])
    if view == 'Overview':
        df = prepare_df()
        content(df)
    elif view == "Detail View":
        df = prepare_df()
        detail_view(df)


