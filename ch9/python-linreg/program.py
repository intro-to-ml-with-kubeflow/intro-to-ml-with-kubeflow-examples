

import pandas as pd
from sklearn.linear_model import LinearRegression
from requests import get
import sys

"""
python program.py <url-of-data> <last-col-to-regress-on>

Will regress first column on next 3 columns (they'd all better be numeric...)

For iris dataset:
https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data
4
"""

with open("/data/data.csv", 'wb') as f:
    r = get(sys.argv[1])
    f.write(r.content)


lastCol = int(sys.argv[2])
data = pd.read_csv("/data/data.csv")
columnNames = data.columns

y = pd.DataFrame(data[columnNames[0]])
x = data[columnNames[1:lastCol]]

model = LinearRegression()
model.fit(x, y)

print(model.coef_)
