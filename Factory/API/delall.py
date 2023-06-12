from typing import Any
import requests,sys
import pandas as pd

class CRUDer:
    def __init__(self, url):
        self.url = url
        self.url = "http://dcha-spx.spring8.or.jp:3001/api1.0.2/zoo_conf/"

    def get(self):
        response = requests.get(self.url)

        if response.status_code == 200:
            # リクエストが成功した場合、応答から数値を取得します
            data = response.json()  # 応答データをJSON形式で取得します
            # print(data)
            # 受け取ったJSONをPandas DataFrameに変換します
            df = pd.DataFrame(data) 
            
            #value = data['exp_raster']  # 応答データから必要な数値を取得します（'key'は実際のデータのキーに置き換えてください）
            #print("取得した数値:", value)
        else:
            # リクエストが失敗した場合のエラーハンドリング
            print("リクエストが失敗しました。ステータスコード:", response.status_code)

        return df

    def postZooFile(self, zoo_csv_path):
        # CSVファイル情報を定義するJSON
        data = {
            'file': zoo_csv_path
        }
        print(data)
        response = requests.post(self.url, json=data)
        # print(response)
        self.proc(response)

    def delete(self, delete_index_list):
        for p_index in delete_index_list:
            # message
            message = f"{self.url}{p_index}/"
            print(message)
            response = requests.delete(message)
            self.proc(response)
            
    def proc(self, response):
        if response.status_code == 200:
            # リクエストが成功した場合の処理
            result = response.json()  # レスポンスデータを取得
            print("成功:", result)
        else:
            # リクエストが失敗した場合のエラーハンドリング
            print("リクエストが失敗しました。ステータスコード:", response.status_code)

    def deleteAll(self):
        df = self.get()
        # DataFrameの中で、すべてのidを取得する
        delete_index_list = []
        delete_index_list = df['id']
        self.delete(delete_index_list)

ppp = CRUDer("http://dcha-spx.spring8.or.jp:3001/api1.0.2/zoo_conf/")
ppp.deleteAll()
