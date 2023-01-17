import datetime
import pymysql
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtWidgets
from datetime import *
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import font_manager, rc
# 한글 폰트 사용을 위해서 세팅, 폰트 경로 설정
font_path = "C:\\Windows\\Fonts\\gulim.ttc"
# 폰트 패스를 통해 폰트 세팅해 폰트 이름 반환받아 font 변수에 삽입
font = font_manager.FontProperties(fname=font_path).get_name()
# 폰트 설정
rc('font', family=font)

form_widget = uic.loadUiType('smartstore.ui')[0]
class Search(QWidget, form_widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.btn_product.clicked.connect(self.goStock)  # 홈페이지 - 상품등록버튼
        self.btn_home3.clicked.connect(self.goStock)    # 상품등록페이지 - 홈버튼

        self.stock_tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 실험용
        # self.showStock_table()
        # self.comboboxSetting()
        # self.minusStock()
        self.canMake()

    def goHome(self):
        self.stackedWidget.setCurrentIndex(0)
    def goStock(self):
        self.stackedWidget.setCurrentIndex(3)

    def comboboxSetting(self):
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000',
                               db='malatang')
        a = conn.cursor()
        sql = f"SELECT material_name FROM inventory"
        a.execute(sql)
        material_info = a.fetchall()
        for i in material_info:
            self.material5.addItem(i[0])

        sql1 = f"SELECT amount FROM recipe"
        a.execute(sql1)
        price_info = a.fetchall()
        for i in price_info:
            self.material6.addItem(str(i[0]))

        sql2 = f"SELECT unit_price FROM inventory"
        a.execute(sql2)
        price_info = a.fetchall()
        for i in price_info:
            self.material7.addItem(str(i[0]))


    def showStock_table(self):
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000',
                               db='malatang')
        a = conn.cursor()
        sql = f"SELECT * FROM inventory"
        a.execute(sql)
        stock_info = a.fetchall()
        row = 0
        self.stock_tableWidget.setRowCount(len(stock_info))
        for i in stock_info:
            self.stock_tableWidget.setItem(row, 0, QTableWidgetItem(i[0]))
            self.stock_tableWidget.setItem(row, 1, QTableWidgetItem(i[1]))
            self.stock_tableWidget.setItem(row, 2, QTableWidgetItem(str(i[2])))     # type = int
            self.stock_tableWidget.setItem(row, 3, QTableWidgetItem(str(i[3])))     # type = decimal
            row += 1

    def selectMatarial(self):
        # 콤보박스 값 라인에딧에 할당
        m_name = self.material5.currentText()
        self.stock5.setText(m_name)
        m_amount = self.material6.currentText()
        self.stock6.setText(m_amount)
        m_price = self.material7.currentText()
        self.stock7.setText(m_price)

    def minusStock(self):
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000',
                               db='malatang')
        a = conn.cursor()
        # 레시피 테이블에서 재료, 수량 가져움     (↓주문수)
        sql = f"SELECT material_name, amount*3 FROM recipe where product_name = '마라탕'"
        a.execute(sql)
        outofstock = a.fetchall()   # 소진된 재고량 ((재료명, 수량*3))
        for i in range(len(outofstock)):
            # 인벤토리 테이블에 주문량 만큼 재고 차감
            sql1 = f"SELECT total_amount FROM inventory where material_name = '{outofstock[i][0]}'" # 재료명
            a.execute(sql1)
            stock_info = a.fetchall()
            remain_stock = int(stock_info[i][0]) - int(outofstock[i][1])
            sql2 = f"update inventory set total_amount = {remain_stock} where material_name = '{outofstock[i][0]}'"
            a.execute(sql2)
            conn.commit()
        self.showstock_table()


    def canMake(self):
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000',
                               db='malatang')
        a = conn.cursor()
        # 레시피 테이블에서 재료, 수량 가져움
        sql = f"SELECT material_name, amount FROM recipe where product_name = '마라탕'"
        a.execute(sql)
        amount_1 = a.fetchall()  # 1인분 ((재료명, 수량))
        list = []
        print(amount_1)
        for i in range(len(amount_1)):
            sql1 = f"SELECT round(total_amount/{int(amount_1[i][1])}, 0) FROM inventory where material_name = '{amount_1[i][0]}'"  # 재료명
            a.execute(sql1)
            stock_info = a.fetchall()
            list.append(stock_info)
        min(list)   #최솟값 만큼 만들 수 있다!

    def shortageAlarm(self):
        pass



if __name__ == "__main__":

    app = QApplication(sys.argv)

    widget = QtWidgets.QStackedWidget()

    mainWindow = Search()

    widget.addWidget(mainWindow)

    widget.setFixedHeight(835)
    widget.setFixedWidth(1059)
    widget.show()
    app.exec_()