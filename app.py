import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly
import psutil
import pandas as pd
import random
import json
import os
from collections import deque
import plotly.graph_objs as go
import math
import numpy as np
import re
from subprocess import check_output


def get_pids(port):
    command = "sudo lsof -i :%s | awk '{print $2}'" % port
    pids = check_output(command, shell=True)
    pids = pids.strip()
    if pids:
        pids = re.sub(' +', ' ', pids.decode("utf-8"))
        for pid in pids.split('\n'):
            try:
                yield int(pid)
            except:
                pass


def convert_size(size_bytes, index=None):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i) if index is None else math.pow(1024, index)
    s = round(size_bytes / p, 2)
    return s if index is not None else "%s %s" % (s, size_name[i])


frame_len = 60

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.Div(className='row',  # Define the row element
             children=[
                 html.Div(className='three columns div-user-controls',
                          children=[
                              html.H2('Performance monitoring'),
                              html.P(
                                  '''Visualizes resource usage of a process and the system'''),
                              html.P(
                                  '''Please enter the port of the process you want to monitor (default is this app)'''),
                              dcc.Input(
                                  id='input_pid', type='number', placeholder='Input port', debounce=True, value="8050"),
                          ]),  # Define the left element
                 html.Div(className='columns div-for-charts bg-grey',
                          children=[
                              dcc.Graph(
                                  id='sys-cpu-usage-line',
                                  config={
                                      'displayModeBar': False},
                                  animate=True,
                                  figure=go.Figure(data=[go.Scatter(x=list(reversed(range(0, frame_len))), y=[0], name=f"CPU {i}", mode='lines', line_shape='spline') for i in range(len(psutil.cpu_percent(percpu=True)))],
                                                   layout=go.Layout(xaxis=dict(range=[frame_len, 0]),
                                                                    yaxis=dict(range=[0, 100], ticksuffix='%'))
                                                   ).update_layout(title_text="System CPU usage (%)", template='plotly_dark', paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)', hovermode='x')

                              ),
                              dcc.Graph(
                                  id='process-cpu-usage-line',
                                  config={
                                      'displayModeBar': False},
                                  animate=True,
                                  figure=go.Figure(data=[go.Scatter(x=list(reversed(range(frame_len))), y=[0], name=f"Scatter", mode='lines', line_shape='spline')],
                                                   layout=go.Layout(xaxis=dict(range=[frame_len, 0]),
                                                                    yaxis=dict(range=[0, 100], ticksuffix='%'))
                                                   ).update_layout(title_text="Process CPU usage (%)", template='plotly_dark', paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)', hovermode='x')
                              ),
                              dcc.Interval(
                                  id='interval-component',
                                  interval=1*1000,  # in milliseconds
                                  n_intervals=0
                              ),
                              dcc.Interval(
                                  id='sys-interval-component',
                                  interval=1*1000,  # in milliseconds
                                  n_intervals=0
                              )
                          ]
                          ),  # Define CPU column
                 html.Div(className='columns div-for-charts bg-grey',
                          children=[
                              dcc.Graph(
                                  id='sys-mem-usage-line',
                                  config={
                                      'displayModeBar': False},
                                  animate=True,
                                  figure=go.Figure(data=[go.Scatter(x=list(reversed(range(frame_len))), y=[0], name=f"Scatter", mode='lines', line_shape='spline')],
                                                   layout=go.Layout(xaxis=dict(range=[frame_len, 0]),
                                                                    yaxis=dict(range=[0, 100], ticksuffix='%'))
                                                   ).update_layout(title_text="System memory usage (%)", template='plotly_dark', paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)', hovermode='x')
                              ),
                              dcc.Graph(
                                  id='process-mem-usage-percent-line',
                                  config={
                                      'displayModeBar': False},
                                  animate=True,
                                  figure=go.Figure(data=[go.Scatter(x=list(reversed(range(frame_len))), y=[0], name=f"Scatter", mode='lines', line_shape='spline')],
                                                   layout=go.Layout(xaxis=dict(range=[frame_len, 0]),
                                                                    yaxis=dict(range=[0, 100], ticksuffix='%'))
                                                   ).update_layout(title_text="Process memory utilization in percentage relative to total memory", template='plotly_dark', paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)', hovermode='x')
                              ),
                          ]
                          ),  # Define percent memory column
                 html.Div(className='columns div-for-charts bg-grey',
                          children=[
                              dcc.Graph(
                                  id='sys-mem-usage-mb-line',
                                  config={
                                      'displayModeBar': False},
                                  animate=True,
                                  figure=go.Figure(data=[go.Scatter(x=list(reversed(range(frame_len))), y=[0], name=f"Scatter", mode='lines', line_shape='spline')],
                                                   layout=go.Layout(xaxis=dict(range=[frame_len, 0]),
                                                                    yaxis=dict(range=[0, convert_size(psutil.virtual_memory().total, index=3)], ticksuffix='GB'))
                                                   ).update_layout(title_text="System memory usage in GB", template='plotly_dark', paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)', hovermode='x')
                              ),
                              dcc.Graph(
                                  id='process-mem-usage-mb-line',
                                  config={
                                      'displayModeBar': False},
                                  animate=True,
                                  figure=go.Figure(data=[go.Scatter(x=list(reversed(range(frame_len))), y=[0], name=f"Scatter", mode='lines', line_shape='spline')],
                                                   layout=go.Layout(xaxis=dict(range=[frame_len, 0]), yaxis=dict(
                                                       ticksuffix='MB', rangemode='tozero'))
                                                   ).update_layout(title_text="Process memory usage in MB", template='plotly_dark', paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)', hovermode='x')
                              ),
                          ]
                          ),  # Define MB memory column
             ])
])

# Setup all system callbacks


@app.callback(Output('sys-cpu-usage-line', 'extendData'),
              [Input('sys-interval-component', 'n_intervals')])
def update_extendData(n_intervals):
    cpu_usage = psutil.cpu_percent(percpu=True)
    y_new = [[cpu_usage[i]] for i in range(len(cpu_usage))]
    return (dict(y=y_new), list(range(len(cpu_usage))), frame_len)


@app.callback(Output('sys-mem-usage-line', 'extendData'),
              [Input('sys-interval-component', 'n_intervals')])
def update_extendData(n_intervals):
    y_new = [[psutil.virtual_memory().percent]]
    return (dict(y=y_new), [0], frame_len)


@app.callback(Output('sys-mem-usage-mb-line', 'extendData'),
              [Input('sys-interval-component', 'n_intervals')])
def update_extendData(n_intervals):
    sys_mem = psutil.virtual_memory()
    y_new = [[convert_size(sys_mem.total - sys_mem.available, index=3)]]
    return (dict(y=y_new), [0], frame_len)

# Setup all process callbacks


@app.callback(Output('process-cpu-usage-line', 'extendData'),
              [Input('interval-component', 'n_intervals')],
              [Input("input_pid", "value")])
def update_extendData(n_intervals, value):
    if len(list(get_pids(value))) > 0:
        process = psutil.Process(list(get_pids(value))[0])
    else:
        process = psutil.Process(list(get_pids("8050"))[0])
    y_new = [[process.cpu_percent(interval=0.5)]]
    return (dict(y=y_new), [0], frame_len)


@app.callback(Output('process-mem-usage-percent-line', 'extendData'),
              [Input('interval-component', 'n_intervals')],
              [Input("input_pid", "value")])
def update_extendData(n_intervals, value):
    if len(list(get_pids(value))) > 0:
        process = psutil.Process(list(get_pids(value))[0])
    else:
        process = psutil.Process(list(get_pids("8050"))[0])
    y_new = [[process.memory_percent()]]
    return (dict(y=y_new), [0], frame_len)


@app.callback(Output('process-mem-usage-mb-line', 'extendData'),
              [Input('interval-component', 'n_intervals')],
              [Input("input_pid", "value")])
def update_extendData(n_intervals, value):
    if len(list(get_pids(value))) > 0:
        process = psutil.Process(list(get_pids(value))[0])
    else:
        process = psutil.Process(list(get_pids("8050"))[0])
    y_new = [[convert_size(process.memory_info()[0], index=2)]]
    return (dict(y=y_new), [0], frame_len)


if __name__ == '__main__':
    app.run_server(debug=False, host='127.0.0.2')
