import sys
import numpy as np
import heapq
import random
import json
import requests


def cos_sim(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def shape_histdata(hist_data):
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
        recommend_list = [recommend_candidate.pop(recommend_candidate.index(i)) for i in user_history]

        # おすすめリストの整頓（重複消すなど）
        for i, x in enumerate(recommend_list):
            if x == -1:
                recommend_list[i] = random.randint(1, 10)
        while len(recommend_list) < 3:
            recommend_list.append(random.randint(1, 10))
            recommend_list = list(set(recommend_list))

        post_recommends(user_id, recommend_list)


def post_recommends(user_id, recommend_list):
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
    request_url = 'https://revipo.p0x0q.com/api/user/all'
    request_param = {
        "mode": "get_user"
    }
    response = requests.get(url=request_url,
                            data=json.dumps(request_param))
    hist_data = response.json()

    # データを整形（履歴ない人はデフォルトで返す、-1埋め、int型変換）
    history_list, hist_data_edited = shape_histdata(hist_data)

    # レコメンドデータをサーバーへ返す
    return_recommends(hist_data_edited, history_list)


if __name__ == '__main__':
    create_recommends()
