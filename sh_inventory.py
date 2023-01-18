import datetime
import time

import pymysql
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import font_manager, rc
# 한글 폰트 사용을 위해서 세팅, 폰트 경로 설정
font_path = "C:\\Windows\\Fonts\\gulim.ttc"
# 폰트 패스를 통해 폰트 세팅해 폰트 이름 반환받아 font 변수에 삽입
font = font_manager.FontProperties(fname=font_path).get_name()
# 폰트 설정
rc('font', family=font)

class shortageAlarm(QThread):
    # 매개변수로 스레드가 선언되는 클래스에서 inventory_renew_alarm(self)라고 하여 상위 클래스를 부모로 지정
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        while True:
            # MySQL에서 import 해오기
            print('쓰레드')
            time.sleep(1)
            conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000',
                                   db='malatang')
            a = conn.cursor()
            # 레시피 테이블에서 상품명에 해당하는 재료, 수량(1인분) 가져움
            sql = f"SELECT material_name, amount FROM recipe where product_name = '마라탕'"  # 주문 받은 상품명 넣을 예정
            a.execute(sql)
            amount_1 = a.fetchall()  # 1인분 ((재료명, 수량))
            list = []  # 빈 리스트 생성, 만들 수 있는 양 넣어줄 예정
            for i in range(len(amount_1)):
                sql1 = f"SELECT total_amount FROM inventory where material_name = '{amount_1[i][0]}'"  # 재료명
                a.execute(sql1)
                stock_info = a.fetchall()   # ((수량,),)
                if int(stock_info[0][0]) < int(amount_1[i][1]):
                    list.append(amount_1[i][0])
                    self.parent.thread_label.setText(f"{list} 재고 부족")
                    time.sleep(2)
                else:
                    self.parent.thread_label.setText('')


form_widget = uic.loadUiType('smartstore.ui')[0]
class Search(QWidget, form_widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # 쓰레드
        self.ira = shortageAlarm(self)
        self.ira.start()

        self.stackedWidget.setCurrentIndex(0)
        self.btn_product.clicked.connect(self.goStock)  # 홈페이지 - 상품등록버튼
        self.btn_home3.clicked.connect(self.goHome)    # 상품등록페이지 - 홈버튼

        # tableWidget 열 넓이 조정
        self.stock_tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.orderlist.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 실험용
        self.showStock_table()
        # self.comboboxSetting()
        # self.minusStock()
        self.canMake()
        self.showOrderlist()
        self.order()

    def goHome(self):
        self.stackedWidget.setCurrentIndex(0)
    def goStock(self):
        self.stackedWidget.setCurrentIndex(3)

# 미사용중
    def comboboxSetting(self):
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000',
                               db='malatang')
        a = conn.cursor()
        # 재료이름 불러오기
        sql = f"SELECT material_name FROM inventory"
        a.execute(sql)
        material_info = a.fetchall()
        for i in material_info:
            self.material5.addItem(i[0])
        # 1인분 양 불러오기
        sql1 = f"SELECT amount FROM recipe"
        a.execute(sql1)
        price_info = a.fetchall()
        for i in price_info:
            self.material6.addItem(str(i[0]))
        # 단가 불러오기
        sql2 = f"SELECT unit_price FROM inventory"
        a.execute(sql2)
        price_info = a.fetchall()
        for i in price_info:
            self.material7.addItem(str(i[0]))

    def selectMatarial(self):
        # 콤보박스 값 라인에딧에 할당
        m_name = self.material5.currentText()
        self.stock5.setText(m_name)
        m_amount = self.material6.currentText()
        self.stock6.setText(m_amount)
        m_price = self.material7.currentText()
        self.stock7.setText(m_price)

# 재고관리
    def showStock_table(self):
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000',
                               db='malatang')
        a = conn.cursor()
        # 재고 정보 모두 불러오기
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

    def minusStock(self):
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000',
                               db='malatang')
        a = conn.cursor()
        # 레시피 테이블에서 재료, 수량 가져움     (↓주문수)
        sql = f"SELECT material_name, amount*3 FROM recipe where product_name = '마라탕'"
        a.execute(sql)
        outofstock = a.fetchall()   # 소진된 재고량 ((재료명, 수량*3))
        # 인벤토리 테이블에 주문량 만큼 재고 차감
        for i in range(len(outofstock)):
            # 재료의 남아 있는 양 불러옴
            sql1 = f"SELECT total_amount FROM inventory where material_name = '{outofstock[i][0]}'" # 재료명
            a.execute(sql1)
            stock_info = a.fetchall()   # 현재 재고량
            # 남은 재고량 = 현재 재고량 - 사용량
            remain_stock = int(stock_info[i][0]) - int(outofstock[i][1])
            # 남은 재고량으로 업데이트
            sql2 = f"update inventory set total_amount = {remain_stock} where material_name = '{outofstock[i][0]}'"
            a.execute(sql2)
            conn.commit()
        self.showstock_table()

    def canMake(self):
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000',
                               db='malatang')
        a = conn.cursor()
        # 레시피 테이블에서 상품명에 해당하는 재료, 수량 가져움
        sql = f"SELECT material_name, amount FROM recipe where product_name = '마라탕'" # 주문 받은 상품명 넣을 예정
        a.execute(sql)
        amount_1 = a.fetchall()  # 1인분 ((재료명, 수량))
        list = []   # 빈 리스트 생성, 만들 수 있는 양 넣어줄 예정
        for i in range(len(amount_1)):
            # 만들 수 있는 양(필요한 재료 양) = 현재 재고량 / 1인분량 의 최솟값
            sql1 = f"SELECT round(total_amount/{int(amount_1[i][1])}, 0) FROM inventory where material_name = '{amount_1[i][0]}'"  # 재료명
            a.execute(sql1)
            stock_info = a.fetchall()
            list.append(stock_info)
        cancook = min(list)   #최솟값 만큼 만들 수 있다!

# 주문관리
    def showOrderlist(self):
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000',
                               db='malatang')
        a = conn.cursor()
        # 재고 정보 모두 불러오기
        sql = f"SELECT account_name, order_code, order_state FROM order_info"
        a.execute(sql)
        stock_info = a.fetchall()
        # ((고객, 주문 번호, 주문 상태))
        row = 0
        self.orderlist.setRowCount(len(stock_info))
        for i in stock_info:
            self.orderlist.setItem(row, 0, QTableWidgetItem(str(i[0])))
            self.orderlist.setItem(row, 1, QTableWidgetItem(str(i[1])))  # type = int
            self.orderlist.setItem(row, 2, QTableWidgetItem(str(i[2])))
            row += 1

        # 테이블 위젯 클릭 하면 주문정보 보이게 하기

        sql1 = f"SELECT product_name, product_quantity FROM order_info"
        a.execute(sql1)
        bill_info = a.fetchall()
        row1 = 0
        self.bill_tableWidget.setRowCount(len(bill_info))
        for i in stock_info:
            self.bill_tableWidget.setItem(row, 0, QTableWidgetItem(str(i[0])))
            self.bill_tableWidget.setItem(row, 1, QTableWidgetItem(str(i[1])))  # type = int
            row1 += 1
    def order(self):
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000',
                               db='malatang')
        a = conn.cursor()
        # 재고 정보 모두 불러오기
        sql = f"select distinct order_code from order_info where order_state = '준비중'"
        a.execute(sql)
        order_check = a.fetchall()
        print(order_check)
        ordercode_list=[]
        for x in order_check:
            ordercode_list.append(x[0])
        for i in ordercode_list:
            sql1 = f"select * from order_info where order_code = {i}"
            a.execute(sql1)
            order_check1 = a.fetchall()
            print(order_check1)

if __name__ == "__main__":

    app = QApplication(sys.argv)

    widget = QtWidgets.QStackedWidget()

    mainWindow = Search()

    widget.addWidget(mainWindow)

    widget.setFixedHeight(835)
    widget.setFixedWidth(1059)
    widget.show()
    app.exec_()