# レコメンドエンジン
## 概要
- 映画情報の閲覧履歴から履歴の似ている人を抽出
- 1人あたり3つ程度でデータを返す
- これを1分に1回繰り返す
## 仕様
- 閲覧履歴取得API: `https://revipo.p0x0q.com/api/user/all`  
上記APIにGETすると以下のデータがくるので、`data['history']`をこねくり回してコサイン類似度をとる。
```
{
    "data": [
        {
            "user_id": 1 <int>
            "history": ["1", "2", ...] <なぜかstr>
        },
        {
            :
        },
        :
        :
    ]
}
```
- レコメンドデータ登録API: `https://revipo.p0x0q.com/api/recommended`  
こねくり回してレコメンドする映画のIDリストができたら、一人のデータずつ以下のフォーマットで上記APIにPOST。
```
{
    "user_id": user_id, <int>
    "recommended_movie_ids": ["1", "2", ...] <なぜかstr>
}
```
## 使用ライブラリ等
- python == 3.7.6
- numpy == 1.19.5
- requests
- schedule
- time
## 今後の展望
- 今回は履歴が少ない人に対して決め撃ち気味に映画を選んだが、トレンドデータなどから推薦できればなお良し。