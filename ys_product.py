import datetime
import pymysql
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtWidgets

from matplotlib import font_manager, rc
# 한글 폰트 사용을 위해서 세팅, 폰트 경로 설정
font_path = "C:\\Windows\\Fonts\\gulim.ttc"
# 폰트 패스를 통해 폰트 세팅해 폰트 이름 반환받아 font 변수에 삽입
font = font_manager.FontProperties(fname=font_path).get_name()
# 폰트 설정
rc('font', family=font)

form_widget = uic.loadUiType('smartTest.ui')[0]


class Search(QWidget, form_widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # (임시) 위젯 인덱스 3번에서 바로 보이게 함
        self.stackedWidget.setCurrentIndex(3)
        self.productname.returnPressed.connect(self.method_productname)

    def method_productname(self):
        print('hi')


if __name__ == "__main__":

    app = QApplication(sys.argv)

    widget = QtWidgets.QStackedWidget()

    mainWindow = Search()

    widget.addWidget(mainWindow)

    widget.setFixedHeight(835)
    widget.setFixedWidth(1059)
    widget.show()
    app.exec_()