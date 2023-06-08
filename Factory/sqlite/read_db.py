import os,sys
import numpy as np
import pandas as pd
import sqlite3

# データベースを読み込んで、内容を表示する
# python dict として読む
conn = sqlite3.connect(sys.argv[1])
c = conn.cursor()
c.execute('SELECT * FROM test')
column_names = [description[0] for description in c.description]

# cのデータをDataframeに格納する
# df = pd.DataFrame(c.fetchall(), columns=column_names)
# print(df)

results = []
for row in c.fetchall():
    results.append(dict(zip(column_names, row)))

print(results)