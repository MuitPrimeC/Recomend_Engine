import sys
import numpy as np
import heapq
import random
import json
import requests
import schedule
import time
from pprint import pprint


def cos_sim(v1, v2):
    """
    2本のベクトルのコサイン類似度計算（ここでは1次元ベクトル同士を想定）
    :param v1: 1次元ベクトル <np.array>
    :param v2: 1次元ベクトル <np.array>
    :return: 上記2本のコサイン類似度 <float>
    """
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def shape_histdata(hist_data):
    """
    ユーザー履歴データの整形。
    履歴がない人は乱数で返す。残った分は最大履歴長に合わせて-1埋めしたのち、intにして配列とdictで返す。
    :param hist_data: user_idと履歴が入った人数分の配列 [{"user_id": <int>}, {"history": [<str>, <str>]}, ...]
    :return: [[<int>, <int>, ...], [], ...] <np.array>, {"user_id": <int>, "history": [<int>, <int>, ...]} <dict>
    """
    # 履歴がない人はデフォルトの値返して、データ消す
    already_return_data = []
    for data in hist_data:
        if len(data['history']) == 0:
            default_data = [{random.randint(1, 10)} for i in range(3)]
            post_recommends(data['user_id'], default_data)
            already_return_data.append(data)
    [hist_data.pop(hist_data.index(d)) for d in already_return_data]

    # もし一個も履歴が残らんかったら終了で
    if len(hist_data) == 0:
        print('All history are flesh!')
        sys.exit(0)

    # userごとの履歴の数を最大値に合わせて−1埋め
    history_list = [hist_dic['history'] for hist_dic in hist_data]
    feature_length = max(map(len, history_list))

    for index in range(len(history_list)):
        delta = feature_length - len(history_list[index])  # delta: 最も履歴が多い人の数と、今のindexの人の履歴数の差
        # 差があれば-1で埋める
        if delta > 0:
            for i in range(delta):
                history_list[index].append(-1)
        # 中身をintにして昇順ソートしてアペンド、dictも合わせて更新。
        hist_elem_array = sorted([int(elem) for elem in history_list[index]])
        history_list[index] = hist_elem_array
        hist_data[index]['history'] = hist_elem_array

    return np.array(history_list), hist_data


def return_recommends(hist_data, history_list):
    """
    shape_histdata()で整形したデータを使って類似度計算し、レコメンド結果をAPIに投げる
    :param hist_data:  [[<int>, <int>, ...], [], ...] <np.array>
    :param history_list: {"user_id": <int>, "history": [<int>, <int>, ...]} <dict>
    :return: None
    """
    for index in range(len(hist_data)):
        user_id = hist_data[index]['user_id']
        user_history = history_list[index]

        # cos類似度をとって格納
        similarity_list = [cos_sim(user_history, history) for history in history_list]
        similarity_list[index] = -np.inf    # 自分自身に対応する部分を0に

        # 降順整列 -> 似てる人のindex調べる
        similar_points = heapq.nlargest(3, similarity_list)
        similar_vec_index = [similarity_list.index(similarity) for similarity in similar_points]    # 似てる人のindex

        # 似てる人のindexから見てない映画を抽出
        recommend_candidate = np.array([history_list[i] for i in similar_vec_index])
        recommend_candidate = np.unique(np.reshape(recommend_candidate, [-1])).tolist()

        for history_movie in user_history:
            if history_movie in recommend_candidate:
                recommend_candidate.pop(recommend_candidate.index(history_movie))
        recommend_list = recommend_candidate

        # おすすめリストの整頓（重複消すなど）
        for i, x in enumerate(recommend_list):
            if x == -1:
                recommend_list[i] = random.randint(1, 10)
        while len(recommend_list) < 3:
            recommend_list.append(random.randint(1, 10))
            recommend_list = list(set(recommend_list))

        print(recommend_list)
        post_recommends(user_id, recommend_list)


def post_recommends(user_id, recommend_list):
    """
    レコメンドデータの書込みAPIへデータをPOST
    :param user_id: そのまま <int>
    :param recommend_list: 映画indexの1次元リスト [<int>, <int>, ...]
    :return: None
    """
    recommend_list_str = [str(movie_id) for movie_id in recommend_list]
    request_url = 'https://revipo.p0x0q.com/api/recommended'
    request_param = {
        "user_id": user_id,
        "recommended_movie_ids": ','.join(recommend_list_str)
    }
    response = requests.post(url=request_url,
                             data=json.dumps(request_param),
                             headers={'Content-Type': 'application/json'})


def create_recommends():
    print('Start recommend.')
    request_url = 'https://revipo.p0x0q.com/api/user/all'
    request_param = {
        "mode": "get_user"
    }
    response = requests.get(url=request_url,
                            data=json.dumps(request_param))
    hist_data = response.json()
    # pprint(hist_data)

    # データを整形（履歴ない人はデフォルトで返す、-1埋め、int型変換）
    history_list, hist_data_edited = shape_histdata(hist_data)
    # pprint(history_list)
    # pprint(hist_data_edited)

    # レコメンドデータをサーバーへ返す
    return_recommends(hist_data_edited, history_list)
    print('Recommend ended.')


# 1分ごと実行
schedule.every(1).minutes.do(create_recommends)
while True:
    schedule.run_pending()
    time.sleep(1)


# if __name__ == '__main__':
#     create_recommends()
