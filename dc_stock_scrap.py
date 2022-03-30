import time
import requests
from bs4 import BeautifulSoup
from konlpy.tag import Okt
from collections import Counter
from wordcloud import WordCloud

okt = Okt()
infos = [
    {"gall_type":"n", "id":"neostock"},
    {"gall_type":"minor", "id":"kospi"},
    {"gall_type":"minor", "id":"tenbagger"},
    {"gall_type":"minor", "id":"vanguard"},
    {"gall_type":"minor", "id":"stockus"},
    {"gall_type":"minor", "id":"dow100"},
    {"gall_type":"mini", "id":"snp500"}]

for info in infos:
    total_text = ""
    for i in range(1,50):
        titles = []
        if info["gall_type"]=="n":
            BASE_URL = "https://gall.dcinside.com/board/lists/"
        elif info["gall_type"]=="minor":
            BASE_URL = "https://gall.dcinside.com/mgallery/board/lists/"
        elif info["gall_type"]=="mini":
            BASE_URL = "https://gall.dcinside.com/mini/board/lists/"

        params = {'id': info['id'],'page':str(i)}
        headers = {'User-Agent' : "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36"}
        try:
            resp = requests.get(BASE_URL, params=params, headers=headers)
            soup = BeautifulSoup(resp.content, "lxml")
            article1 = soup.find("tr",attrs={"class":"ub-content us-post"})
            print(article1.find("td",attrs={"class":"gall_tit ub-word"}).a.text)
            for i in range(46):
                article1 = article1.find_next_sibling("tr")
                titles.append(article1.find("td",attrs={"class":"gall_tit ub-word"}).a.text)
            text = ". ".join(titles)
            total_text += text +"."
            time.sleep(1)
        except AttributeError:
            print("error")
    noun = okt.nouns(okt.normalize(total_text))
    for i, v in enumerate(noun):
        if len(v)<2:
            noun.pop(i)
    count = Counter(noun)
    wc = WordCloud(font_path="C:\\Windows\\Fonts\\맑은 고딕\\malgun.ttf",background_color="white")
    wc.generate_from_frequencies(dict(count.most_common(100)))
    wc.to_file(info['id']+'_wc.png')
