import math
import datetime as dt

import numpy as np
import yfinance as yf

from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import TextInput, Button, DatePicker, MultiChoice 

def fetch_and_process_data(main_stock, comparison_stock, start, end):
    # Download data for both stocks
    df1 = yf.download(main_stock, start=start, end=end)
    df2 = yf.download(comparison_stock, start=start, end=end)
    
    return df1, df2

def calculate_indicators(df):
    gain = df.Close > df.Open
    loss = df.Open > df.Close
    df['SMA30'] = df['Close'].rolling(30).mean()
    df['SMA100'] = df['Close'].rolling(100).mean()
    
    return df, gain, loss

def update_plot(df, gain, loss, indicators, sync_axis=None):
    width = 12 * 60 * 60 * 1000  # half day in ms

    if sync_axis is not None:
        p = figure(x_axis_type="datetime", tools="pan,wheel_zoom,box_zoom,reset,save", width=1000, x_range=sync_axis)
    else:
        p = figure(x_axis_type="datetime", tools="pan,wheel_zoom,box_zoom,reset,save", width=1000)

    p.xaxis.major_label_orientation = math.pi / 4
    p.grid.grid_line_alpha = 0.3

    p.segment(df.index, df.High, df.index, df.Low, color="black")
    p.vbar(df.index[gain], width, df.Open[gain], df.Close[gain], fill_color="#00ff00", line_color="#00ff00")
    p.vbar(df.index[loss], width, df.Open[loss], df.Close[loss], fill_color="#ff0000", line_color="#ff0000")

    for indicator in indicators:
        if indicator == "30 Day SMA":
            p.line(df.index, df['SMA30'], color="purple", legend_label="30 Day SMA")
        elif indicator == "100 Day SMA":
            p.line(df.index, df['SMA100'], color="blue", legend_label="100 Day SMA")

    p.legend.location = "top_left"
    p.legend.click_policy = "hide"

    return p

def on_button_click(main_stock, comparison_stock, start, end, indicators):
    df1, df2 = fetch_and_process_data(main_stock, comparison_stock, start, end)
    df1, gain1, loss1 = calculate_indicators(df1)
    df2, gain2, loss2 = calculate_indicators(df2)
    p = update_plot(df1, gain1, loss1, indicators)
    p2 = update_plot(df2, gain2, loss2, indicators, sync_axis=p.x_range)
    curdoc().clear()
    curdoc().add_root(row(p, p2))

# Widgets
stock1_text = TextInput(title="Main Stock")
stock2_text = TextInput(title="Comparison Stock")
date_picker_from = DatePicker(title='Start Date', value="2020-01-01", min_date="2000-01-01", max_date=dt.datetime.now().strftime("%Y-%m-%d"))
date_picker_to = DatePicker(title='End Date', value="2020-02-01", min_date="2000-01-01", max_date=dt.datetime.now().strftime("%Y-%m-%d"))
indicator_choice = MultiChoice(options=["100 Day SMA", "30 Day SMA"])

load_button = Button(label="Load Data", button_type="success")
load_button.on_click(lambda: on_button_click(stock1_text.value, stock2_text.value, date_picker_from.value, date_picker_to.value, indicator_choice.value))

layout = column(stock1_text, stock2_text, date_picker_from, date_picker_to, indicator_choice, load_button)

curdoc().clear()
curdoc().add_root(layout)
