import pandas as pd
import streamlit as st
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px
import helper as h

# https://yeshwanthrams-midmarks3-first-sxmyrk.streamlit.app/

st.set_page_config(layout='wide')
sb = st.sidebar
sbex = lambda title : sb.expander(title)

dfdata = pd.read_excel('Data/marks.xlsx')
clean_data = h.clean(dfdata)

def get_compare_state():
    with sbex('Compare state'):
        compare_state = st.radio(
            'Compare State', ['pick', 'Slide'], label_visibility='collapsed')
    return compare_state

def get_graph_style():
    want_names = False
    with sbex('Graph style'):
        # NOTE: Just for the graphs, selection of student will only happpen with registration numbers
        if st.checkbox('Display Names'):
            want_names = True
        graphy = st.radio(
            'Graphing', ['Line', 'Bar'], label_visibility='collapsed')

    obdata = {'Line':go.Line,'Bar':go.Bar}
    return obdata[graphy],want_names

def get_data_state():
    with sbex('Data state'):
        data_state = st.radio(
            'nothing', ['DataFrame', 'table'], label_visibility='collapsed')
        
    obdata = {'DataFrame':st.dataframe,'table':st.table}
    return obdata[data_state]

compare_state = get_compare_state()
graphy,want_names = get_graph_style()
data_state = get_data_state()

def cchartf(figure: px._chart_types) -> px._chart_types:
    """
    Updates the layout and axes of a specified plotly chart.

    Arguments:
        figure (px.Figure): The plotly chart to be updated.

    Returns:
        px.Figure: The updated plotly chart.
    """
    figure.update_layout(
        legend=dict(
            y=1.1,
            orientation="h"
        )
    )
    # figure.update_layout(plot_bgcolor="#000000") figure.update_xaxes(showgrid=False) figure.update_yaxes(showgrid=False)
    return figure

def get_averages():
    rdata = clean_data
    c = rdata.columns.tolist()
    results = [element for element in c if element.endswith("_Avg")]
    mand = ['Roll.No', 'Name of the Student', 'Section']
    return rdata[mand+results]

def get_names(rollno: str):
    rdata = clean_data
    if rollno:
        r_name = rdata[rdata['Roll.No'] == rollno]['Name of the Student']
        r_name = r_name.tolist()[0].split(" ")
        r_name.pop(0)
        r_name = ' '.join(r_name)
        return r_name

def get_avg_marks(rollno: str):
    avgs = get_averages()
    est = avgs[avgs['Roll.No'] == rollno].reset_index(drop=True)
    marks_list = est[est['Roll.No'] == rollno].loc[0,"PDSM_Avg":"Biology for Engineers (BE)_Avg"].tolist()
    return marks_list

def averages():
    c = st.columns(3)
    if compare_state == 'pick':
        c = st.columns([1,2])

    avgs = get_averages()

    subjects = avgs.columns.tolist()
    subjects = [n.split('_')[0] for n in subjects[3:]]

    with c[0]:
        section_selection = st.selectbox(
            'section: ', list(set(avgs['Section'])))

    savg = avgs[avgs['Section'] == section_selection]['Roll.No'].tolist()
    
    students = []
    if compare_state == 'Slide':
        with c[1]:
            students.append(st.select_slider('First rollno', savg))
        with c[2]:
            students.append(st.select_slider('second rollno', savg))

    elif compare_state == 'pick':
        with c[1]:
            students = st.multiselect(
                'Students selection',
                savg,
                default=savg[0],
                max_selections=7,
                help='can select upto 4 students'
            )

    datastudents = []
    if students:
        for n in students:
            est = avgs[avgs['Roll.No'] == n].reset_index(drop=True)
            marks_list = est[est['Roll.No'] == n].loc[0,
                                                      "PDSM_Avg":"Biology for Engineers (BE)_Avg"].tolist()
            if want_names:
                n = get_names(n)
            datastudents.append(graphy(name=n, x=subjects, y=marks_list))

    if students and datastudents:
        fig = go.Figure(data=datastudents)
        with st.expander('Graph', expanded=True):
            st.plotly_chart(cchartf(fig), use_container_width=True)
    
    with st.expander('Averages'):
        data_state(get_averages())
        
class totals:
    tdata = None 
    subjects = None

    def __init__(self,cdata : pd.DataFrame):
        self.tdata = self.get_totals(cdata)

    def get_totals(self,cdata) -> pd.DataFrame:
        rdata = cdata
        c = rdata.columns.tolist()
        mid1 = [element for element in c if element.endswith("_TOT1") ]
        mid2 = [element for element in c if element.endswith("_TOT2") ]
        mand = ['Roll.No', 'Name of the Student', 'Section']
        return rdata[mand+mid1+mid2]

    def show_totals(self):
        data_state(self.tdata)

    def get_mid_marks(self,student: pd.DataFrame):
        rdata = student
        c = rdata.columns.tolist()
        mid1 = [element for element in c if element.endswith("1")]
        self.subjects = [n.split('_')[0] for n in mid1]
        mid1 = rdata.loc[0,mid1[0]:mid1[-1]].tolist()
        mid2 = [element for element in c if element.endswith("2")]
        mid2 = rdata.loc[0,mid2[0]:mid2[-1]].tolist()
        return mid1,mid2

    def totals_graph(self,student: str,want_avg = None):
        rdata = self.tdata
        est = rdata[rdata['Roll.No'] == student].reset_index(drop=True)
        data = []
        mid1, mid2 = self.get_mid_marks(est)
        data.append(graphy(name='Mid1',x=self.subjects,y=mid1))
        data.append(graphy(name='Mid2',x=self.subjects,y=mid2))
        marks_list = None
        if want_avg:
            marks_list = get_avg_marks(student)
            data.append(go.Scatter(name='avg',x = self.subjects,y=marks_list,line_color='#F8F9F9'))
        fig = go.Figure(data=data)
        st.plotly_chart(cchartf(fig),use_container_width=True)

es = lambda message : st.write(message)

mks,a, cd = st.tabs(['Marks','Avg', 'Data'])

with a:
    averages()

with mks:
    rms = totals(clean_data)

    with st.expander('Graph'):
        c = st.columns([1,9])

    with c[0]:
        for n in range(3):
            es("")
        add_averages = st.checkbox('averages')
        section_selection = st.selectbox(
            'sections: ', list(set(clean_data['Section'])))
        stotal = clean_data[clean_data['Section'] == section_selection]['Roll.No'].tolist()
        sselection = st.selectbox('Students: ',stotal)

    with c[1]:
        rms.totals_graph(sselection,add_averages)
    with st.expander("Total's Data"):
        rms.show_totals()
    
with cd:
    with st.expander('Data'):
        data_state(clean_data)