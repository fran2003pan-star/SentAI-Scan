import requests
import pandas as pd
import time

def fetch_reddit_data(subreddit, limit):
    posts = []
    after = None
    # Reddit solo da máximo 100 por petición, así que iteramos
    for i in range(0, limit, 100):
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=100"
        if after:
            url += f"&after={after}"
        
        headers = {'User-agent': 'InnoRadar_System_v5'}
        res = requests.get(url, headers=headers)
        
        if res.status_code == 200:
            data = res.json()
            for p in data['data']['children']:
                posts.append([
                    p['data']['title'], 
                    p['data']['score'], 
                    p['data']['num_comments']
                ])
            
            after = data['data']['after']
            if not after: break # Si no hay más posts, paramos
            time.sleep(0.5) # Pausa técnica para que Reddit no nos bloquee
        else:
            break

    df = pd.DataFrame(posts, columns=['titulo', 'puntuacion', 'num_comentarios'])
    # Recortamos al límite exacto que pidió el usuario
    return df.head(limit)