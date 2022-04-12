import utilds_data as ud
import json
import numpy as np
import pandas as pd
from plotly import graph_objs as go
import utilds_data as ud
from logzero import logger
from plotly.subplots import make_subplots

fig = make_subplots(rows=1,cols=2,shared_yaxes=True,vertical_spacing=0.25)

fig.append_trace( go.Bar(
    x = [1,2],
    y = [2,3],
),
row=1,
col=1)

fig.append_trace( go.Bar(
    x = [1,2],
    y = [2,3],
),
row=1,
col=2)


fig.show()