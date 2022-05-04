import folium
import io
from PIL import Image
from geopy.geocoders import Nominatim
import numpy as np
import matplotlib.pyplot as plt
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvas

class GetGeoMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        self.addressLayout = QHBoxLayout()
        self.addressLayout.addWidget(QLabel("address"))
        self.addressLineEdit = QLineEdit()
        self.addressLayout.addWidget(self.addressLineEdit)
        self.mainLayout.addLayout(self.addressLayout)
        self.figureCanvas = FigureCanvas()
        self.plot = self.figureCanvas.figure.add_subplot(111)
        self.mainLayout.addWidget(self.figureCanvas)

    def keyPressEvent(self, event):
        if event.key()==Qt.Key_Return:
            self.addressToMap()

    def addressToMap(self):
        axis = self.geocoding(self.addressLineEdit.text())
        print(axis)
        latitude = axis[0]
        longitude = axis[1]
        m = folium.Map(location=[latitude, longitude],
                       zoom_start=14,
                       width=600,
                       height=640,
                       tiles='stamenwatercolor',
                       zoom_control=False
                      )
        img_data = m._to_png(5)
        img = Image.open(io.BytesIO(img_data))
        img_np = np.array(img)[20:620,:600,:]
        data = img_np.mean(axis=2)
        if 'image' not in self.__dict__:
            self.image = self.plot.imshow(data,cmap="gray")
        else:
            self.image.set_data(data)
        self.figureCanvas.draw()

    # 위도, 경도 반환하는 함수
    def geocoding(self,address):
        geo_local = Nominatim(user_agent='South Korea')
        geo = geo_local.geocode(address)
        x_y = [geo.latitude, geo.longitude]
        return x_y

if __name__=="__main__":
    app = QApplication()
    mainWindow = GetGeoMain()
    mainWindow.show()
    app.exec_()
