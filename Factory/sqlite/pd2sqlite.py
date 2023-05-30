import os,sys
import numpy as np
import pandas as pd
import sqlite3

# CSVファイルを読み込む
df = pd.read_csv(sys.argv[1])

# dfをqlite3のデータベースに変換する
# まず、sqlite3のデータベースを作成する
# その後、dfをデータベースに書き込む
# その際、columnsの名前をそのまま項目の名称として利用する
# また、indexは無視する
conn = sqlite3.connect('test.db')
c = conn.cursor()
conn.commit()
df.to_sql('test', conn, if_exists='replace', index=False)
conn.commit()
conn.close()

# データベースを読み込んで、内容を表示する
# python dict として読む
conn = sqlite3.connect('test.db')
c = conn.cursor()
c.execute('SELECT * FROM test')
column_names = [description[0] for description in c.description]

results = []
for row in c.fetchall():
    results.append(dict(zip(column_names, row)))

print(results)