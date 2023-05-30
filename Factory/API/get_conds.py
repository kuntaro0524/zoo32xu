import requests
import pandas as pd

url = "http://dcha-spx.spring8.or.jp:3001/api1.0.2/zoo_conf/"
response = requests.get(url)
if response.status_code == 200:
    # リクエストが成功した場合、応答から数値を取得します
    data = response.json()  # 応答データをJSON形式で取得します
    # print(data)
    # 受け取ったJSONをPandas DataFrameに変換します
    df = pd.DataFrame(data) 
    print(df)
    # DataFrameに含まれている数値をすべて表示
    # 1行ごとに
    for index, row in df.iterrows():
        print(row['exp_raster'])
    
    #value = data['exp_raster']  # 応答データから必要な数値を取得します（'key'は実際のデータのキーに置き換えてください）
    #print("取得した数値:", value)
else:
    # リクエストが失敗した場合のエラーハンドリング
    print("リクエストが失敗しました。ステータスコード:", response.status_code)

# Pandas Data Frame を sqlite3 の DB に変換する
# まず、sqlite3のデータベースを作成する
# その後、dfをデータベースに書き込む
# その際、columnsの名前をそのまま項目の名称として利用する
# また、indexは無視する
# その後、データベースを読み込んで、内容を表示する
# python dict として読む
import sqlite3
conn = sqlite3.connect('test.db')
c = conn.cursor()
conn.commit()
df.to_sql('test', conn, if_exists='replace', index=False)
conn.commit()
conn.close()
