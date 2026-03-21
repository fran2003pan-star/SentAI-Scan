import requests
import pandas as pd
import time
import os

def fetch_reddit_data(subreddit, limit):
    posts = []
    after = None

    for i in range(0, limit, 100):
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=100"
        if after:
            url += f"&after={after}"

        headers = {'User-agent': 'InnoRadar_System_v5'}
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                for p in data['data']['children']:
                    posts.append([
                        p['data']['title'],
                        p['data']['score'],
                        p['data']['num_comments']
                    ])
                after = data['data']['after']
                if not after:
                    break
                time.sleep(0.5)
            else:
                break
        except Exception:
            break

    if len(posts) < 10:
        # Reddit no disponible — cargamos dataset de demo
        csv_path = f"database/demo_{subreddit}.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            return df.head(limit)
        return pd.DataFrame()

    df = pd.DataFrame(posts, columns=['titulo', 'puntuacion', 'num_comentarios'])
    return df.head(limit)