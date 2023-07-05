import time, requests
from functools import partial

from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *

from bs4 import BeautifulSoup
from konlpy.tag import Okt
from collections import Counter
from wordcloud import WordCloud

from lib.state import State, setStateFunc
from lib.task import Tasks, AbstractTask

from components.basic import *

class MainWindow(QMainWindow):
    def __init__(self):    
        super().__init__()

        #본 프로그램에서 Widget과 Component 들이 공유할 데이터 등록
        State().use("gall_type","minor")
        State().use("gall_id","kospi")
        State().use("num_page_collect","2")
        State().use("collected_result_image")
        State().use("statusbar_msg","Ready")

        #Widget 등록        
        self.addToolBar(ToolBar(self))
        self.setCentralWidget(CentralWidget())
        self.setSideWidget("Set Gallery",GallerySelectionWidget(), Qt.LeftDockWidgetArea)
        self.setSideWidget("Set parameter",ParameterSettingWidget(), Qt.RightDockWidgetArea)
        self.setStatusBar(StatusBar(self))
        
    def setSideWidget(self, title, widget, area):
        dockwidget = QDockWidget(title, self)
        dockwidget.setWidget(widget)
        self.addDockWidget(area, dockwidget)

#class MenuBar(QMenuBar):
#    pass

class ToolBar(QToolBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.addAction("execute_crawler")
        self.actionTriggered.connect(self.execute_action)

    def execute_action(self, action):
        if action.text() == "execute_crawler":
            execute_crawler()

class StatusBar(QStatusBar):
    def __init__(self, parent):
        super().__init__(parent)
        State().bind("statusbar_msg","statusbar_text", self.showMessage)


class GallerySelectionWidget(QWidget):
    def __init__(self):   
        super().__init__()

        #레이아웃 등록
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        #Component 등록
        infos = [
            {"gall_type":"n", "id":"neostock"},
            {"gall_type":"minor", "id":"kospi"},
            {"gall_type":"minor", "id":"tenbagger"},
            {"gall_type":"minor", "id":"vanguard"},
            {"gall_type":"minor", "id":"stockus"},
            {"gall_type":"minor", "id":"dow100"},
            {"gall_type":"mini", "id":"snp500"}]
        for info in infos:
            gall_type = info["gall_type"]
            gall_id = info["id"]
            ButtonComponent(id="set_gallery_as_"+gall_id, label=gall_id, layout=mainLayout,
                onClick = partial(self.set_gallery, gall_type, gall_id))

    #Method 정의
    def set_gallery(self, gall_type, gall_id):
        State().set("gall_type",gall_type)
        State().set("gall_id",gall_id)
        execute_crawler()

class CentralWidget(QWidget):
    def __init__(self):   
        super().__init__()

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        #Component 등록
        ImageComponent(id="result_image", label="수집 결과", layout=mainLayout,
            model_id = "collected_result_image")


class ParameterSettingWidget(QWidget):
    def __init__(self):   
        super().__init__()

        #레이아웃 등록
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        #Component 등록
        LineEditComponent(id="gall_type_edit", label="갤러리 구분", layout=mainLayout,
            onChange = lambda x : State().set("gall_type",x),
            model_id = "gall_type")
        LineEditComponent(id="gall_id_edit", label="갤러리 ID", layout=mainLayout,
            onChange = lambda x : State().set("gall_id",x),
            model_id = "gall_id")
        LineEditComponent(id="num_page_collect_edit", label="수집할 페이지 수", layout=mainLayout,
            onChange = lambda x : State().set("num_page_collect",x),
            model_id = "num_page_collect")

def execute_crawler():
    gall_type = State().value("gall_type")
    gall_id = State().value("gall_id")
    num_collect = int(State().value("num_page_collect"))

    def set_results(value):
        State().set("collected_result_image",value[0])
        State().set("statusbar_msg",value[1])

    Tasks().set("collect_gallery",
        CollectGallery(gall_type,gall_id,num_collect), 
        func_update=set_results,
        func_return=set_results)


class CollectGallery(AbstractTask):
    def run(self):
        gall_type = self.args[0]
        gall_id = self.args[1]
        num_collect = self.args[2]

        okt = Okt()

        total_text = ""
        for i in range(1,num_collect+1):
            titles = []            
            if gall_type=="n":
                BASE_URL = "https://gall.dcinside.com/board/lists/"
            elif gall_type=="minor":
                BASE_URL = "https://gall.dcinside.com/mgallery/board/lists/"
            elif gall_type=="mini":
                BASE_URL = "https://gall.dcinside.com/mini/board/lists/"
            params = {'id':gall_id,'page':str(i)}
            headers = {'User-Agent' : "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36"}

            try:
                resp = requests.get(BASE_URL, params=params, headers=headers)
                soup = BeautifulSoup(resp.content, "lxml")
                article1 = soup.find("tr",attrs={"class":"ub-content us-post"})
                titles.append(article1.find("td",attrs={"class":"gall_tit ub-word"}).a.text)
                for j in range(46):
                    article1 = article1.find_next_sibling("tr")
                    title = article1.find("td",attrs={"class":"gall_tit ub-word"}).a.text
                    titles.append(title)
                text = "\n".join(titles)
                total_text += text +"."
                time.sleep(1)                              

                noun = okt.nouns(okt.normalize(total_text))
                for j, v in enumerate(noun):
                    if len(v)<2:
                        noun.pop(j)
                count = Counter(noun)
                wc = WordCloud(font_path="C:\\Windows\\Fonts\\맑은 고딕\\malgun.ttf",background_color="white")
                wc.generate_from_frequencies(dict(count.most_common(100)))
                img = wc.to_image()            

                self.update_value = [img, gall_id +" 페이지 : "+str(i)+"/"+str(num_collect) + "에서 제목을 수집 중..."]

            except AttributeError:
                print("error")  

        noun = okt.nouns(okt.normalize(total_text))
        for i, v in enumerate(noun):
            if len(v)<2:
                noun.pop(i)
        count = Counter(noun)
        wc = WordCloud(font_path="C:\\Windows\\Fonts\\맑은 고딕\\malgun.ttf",background_color="white")
        wc.generate_from_frequencies(dict(count.most_common(100)))
        img = wc.to_image()            

        self.return_value = [img, "Ready"]
        return None

if __name__=="__main__":
    app = QApplication()
    window = MainWindow()
    window.show()
    app.setStyle('Fusion')
    app.exec()