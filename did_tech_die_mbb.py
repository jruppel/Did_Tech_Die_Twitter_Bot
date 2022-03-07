import time
import pandas as pd

now = time.localtime()
year = now.tm_year
last_year = year - 1
current_date = time.strftime("%B%e, %Y (%A)",now)

def get_games_today():
    url_year = str(last_year) + "-" + str(year)[2:]
    url = 'https://latechsports.com/sports/mens-basketball/schedule/{}?grid=true'.format(url_year)
    df = pd.read_html(url, header=0)[0]
    games_today = df[df.Date.isin([current_date])]
    if games_today.empty:
        print("Tech does not play today!")
        return
    return games_today

   
#get_games_today()