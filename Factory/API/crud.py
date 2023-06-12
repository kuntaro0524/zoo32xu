from typing import Any
import requests,sys
import pandas as pd
import json

class CRUDer:
    def __init__(self, url):
        self.url = url
        self.url = "http://dcha-spx.spring8.or.jp:3001/api1.0.2/zoo_conf/"

        with open("./type.json") as f:
            mapping = json.load(f)

        self.type_mapping = {}
        for key, value in mapping.items():
            if value=="int":
                self.type_mapping[key] = int
            elif value=="float":
                self.type_mapping[key] = float
            elif value=="str":
                self.type_mapping[key] = str
            elif value=="datetime":
                self.type_mapping[key] = pd.Timestamp
            else:
                self.type_mapping[key] = str

        print(self.type_mapping)

    def correctType(self, json_data):
        for key, value in json_data.items():
            # もしも value が str ならば
            if type(value) == str:
                # value を int に変換して、json_data の value に代入する
                # 文字列の長さが0の場合は、Noneを代入する
                if len(value)==0:
                    json_data[key] = None
                else:
                    print("converting!")
                    json_data[key] = self.type_mapping[key](value)

        return json_data

    def get(self, isRaw=False):
        response = requests.get(self.url)

        if response.status_code == 200:
            # リクエストが成功した場合、応答から数値を取得します
            data = response.json()  # 応答データをJSON形式で取得します

            if isRaw:
                return data
            else:
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
            "file": zoo_csv_path
        }
        headers = {"Content-Type": "application/json"}
        # response = requests.post(self.url, headers=headers, data=json_data)
        response = requests.post(self.url, json=data)
        # print(response)
        self.proc(response)

    def getParam(self, id):
        message = f"{self.url}{id}/"
        print(message)
        response = requests.get(message)
        if response.status_code == 200:
            # リクエストが成功した場合、応答から数値を取得します
            data = response.json()
            return data
        else:
            return None

    def delete(self, delete_index_list):
        for p_index in delete_index_list:
            # message
            message = f"{self.url}{p_index}/"
            print(message)
            response = requests.delete(message)
            self.proc(response)
            
    def proc(self, response):
        print(response)
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

    def modParamID(self, id, param):
        message = f"{self.url}{id}/"
        print(message)
        response = requests.put(message, json=param)

        return self.proc(response)

# url = "CRUDサーバーのエンドポイントのURL"
# data = {
#     'key1': 'value1',
#     'key2': 'value2'
# }

# response = requests.post(url, json=data)
# response = requests.get(url)
# data = {
#     'key1': 'new_value1',
#     'key2': 'new_value2'
# }


# response = requests.put(url, json=data)  # または requests.patch(url, json=data)

# if response.status_code == 200:
#     # リクエストが成功した場合の処理
#     result = response.json()  # レスポンスデータを取得
#     print("成功:", result)
# else:
#     # リクエストが失敗した場合のエラーハンドリング
#     print("リクエストが失敗しました。ステータスコード:", response.status_code)

ppp = CRUDer("http://dcha-spx.spring8.or.jp:3001/api1.0.2/zoo_conf/")
# df = ppp.get()
# print(df)

# Dataframeの中で、'root_dir'に "isilon"を含んでいるものの id のリストを作成する
# to_be_deleted = []
# for index, row in df.iterrows():
    # if "isilon" in row['root_dir']:
        # to_be_deleted.append(row['id'])

# ppp.deleteAll()
print("AGAGAGAA")

# for i in [112,113,150,250]:
    # pininfo=ppp.getParam(i)
    # print(pininfo)1

# modify parameters
mod_param = {
    "exp_raster": 1.0,
    "nds_multi": 10,
    "n_mount": 1,
    "p_index": 1,
    "o_index": 10
}

# ppp.modParamID(112, mod_param)
# params = ppp.getParam(112)

# post zoo file
zoofile = sys.argv[1]
ppp.postZooFile(zoofile)
raw_data = ppp.get(isRaw=True)
df_data = ppp.get()
# dataframeに含まれる 'exp_raster'の型を調べる
print(df_data.describe())
print(raw_data)

print("################################")
for d in raw_data:
    print(d)
    corr_data = ppp.correctType(d)
    print(corr_data)