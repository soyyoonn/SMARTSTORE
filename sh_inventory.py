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

class orderAlarm(QThread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        while True:
            time.sleep(5)
            if self.parent.stackedWidget.currentIndex() == 3:
                self.parent.orderAlarm_label.setText('')
            elif self.parent.stackedWidget.currentIndex() != 3:
                print(self.parent.stackedWidget.currentIndex())
                self.parent.orderAlarm_label.setText('주문이 들어왔습니다')

class Delivary(QThread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        item = self.parent.orderlist.selectedItems()
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000',
                               db='malatang')
        a = conn.cursor()
        # 레시피 테이블에서 상품명에 해당하는 재료, 수량(1인분) 가져움
        sql2 = f"update order_info set order_state = '배송완료' where order_code = {(int(item[1].text()))}"

        # 2초 뒤에 배송 완료로 바꿔주기
        time.sleep(2)

        a.execute(sql2)
        conn.commit()
        conn.close()
        # self.parent.showOrderlist()

class orderRemind(QThread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        while True:
            if self.parent.threadend:
                print('쓰레드 종료')
                return
            time.sleep(5)
            # self.parent.orderAlarm_label.setText('주문이 들어왔습니다')

            # MySQL에서 import 해오기
            conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000',
                                   db='malatang')
            a = conn.cursor()
            sql = f"SELECT distinct account_name, order_code, order_state FROM order_info where order_state = '준비중' ORDER BY RAND() LIMIT 1"
            a.execute(sql)
            live_order = a.fetchall()
            self.parent.list.append(live_order)
            row = 0
            self.parent.orderlist.setRowCount(len(self.parent.list))
            for i in self.parent.list:
                self.parent.orderlist.setItem(row, 0, QTableWidgetItem(str(i[0][0])))
                self.parent.orderlist.setItem(row, 1, QTableWidgetItem(str(i[0][1])))  # type = int
                self.parent.orderlist.setItem(row, 2, QTableWidgetItem(str(i[0][2])))
                row += 1
            conn.close()

class shortageAlarm(QThread):
    # 매개변수로 스레드가 선언되는 클래스에서 shortageAlarm(self)라고 하여 상위 클래스를 부모로 지정
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
            list = []  # 빈 리스트 생성, 만들 수 있는 양 넣어줄 예정
            for j in range(len(self.parent.bill_info)):
                # 레시피 테이블에서 상품명에 해당하는 재료, 수량(1인분) 가져움
                sql = f"SELECT material_name, amount FROM recipe where product_name = '{self.parent.bill_info[j][0]}'"  # 주문 받은 상품명 넣을 예정
                a.execute(sql)
                amount_1 = a.fetchall()  # 1인분 ((재료명, 수량))
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

        self.list = []
        self.threadend = False  # 스레드 종료

        # 쓰레드
        self.oa = orderAlarm(self)
        self.oa.start()

        # 페이지 이동
        self.stackedWidget.setCurrentIndex(0)
        self.btn_order.clicked.connect(self.goStock)  # 홈페이지 - 주문관리버튼
        self.btn_home3.clicked.connect(self.goHome)    # 상품등록페이지 - 홈버튼

        # 메서드 연결
        self.orderlist.cellClicked.connect(self.showProduct)
        self.btn_check2.clicked.connect(self.sendProduct)
        self.btn_test2.clicked.connect(self.start_thread)
        self.btn_end2.clicked.connect(self.end_thread)


        # tableWidget 열 넓이 조정
        self.stock_tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.orderlist.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 실험용
        self.showStock_table()
        self.showOrderlist()
        # self.comboboxSetting()
        # self.minusStock()
        # self.canMake()
        # self.sendProduct()


    def goHome(self):
        self.stackedWidget.setCurrentIndex(0)

    def goStock(self):
        self.stackedWidget.setCurrentIndex(3)

    def pageIndex(self):
        page = self.stackedWidget.currentIndex()
        return page

    def start_thread(self):
        # 종료 버튼으로 변경 된다
        self.stackedWidget_3.setCurrentIndex(1)
        # thread 시작
        self.lo = orderRemind(self)
        self.lo.start()
        self.orderlist.clearContents()  # 페이지 넘어가기전 주문 테이블 클리어

    def end_thread(self):
        # 실시간 주문 버튼으로 변경됨
        self.stackedWidget_3.setCurrentIndex(0)
        self.threadend = True

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

    def confirmStock(self):
        cannot = 0
        item = self.orderlist.selectedItems()
        conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000',
                               db='malatang')
        a = conn.cursor()
        # 레시피 테이블에서 상품명에 해당하는 재료, 수량(1인분) 가져움
        list = []  # 빈 리스트 생성, 만들 수 있는 양 넣어줄 예정
        for j in range(len(self.bill_info)):
            sql = f"SELECT material_name, amount FROM recipe where product_name = '{self.bill_info[j][0]}'"  # 주문 받은 상품명 넣을 예정
            a.execute(sql)
            amount_1 = a.fetchall()  # 1인분 ((재료명, 수량))
            for i in range(len(amount_1)):
                sql1 = f"SELECT total_amount FROM inventory where material_name = '{amount_1[i][0]}'"  # 재료명
                a.execute(sql1)
                stock_info = a.fetchall()  # ((수량,),)
                if int(stock_info[0][0]) < int(amount_1[i][1]):
                    list.append(amount_1[i][0])
                    cannot = 1
                    break
        if cannot == 0:
            QMessageBox.information(self, '알림', '발송 되었습니다')
            sql2= f"update order_info set order_state = '발송완료' where order_code = {(int(item[1].text()))}"
            a.execute(sql2)
            conn.commit()
            # self.showOrderlist()
            self.minusStock()
            # 쓰레드
            self.testThread = Delivary(self)
            self.testThread.start()
        else:
            QMessageBox.information(self, '알림', f'{list}의 재고가 부족합니다')

    def minusStock(self):
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000',
                               db='malatang')
        a = conn.cursor()
        for j in range(len(self.bill_info)):
            # 레시피 테이블에서 재료, 수량 가져움       (↓주문수)
            sql = f"SELECT material_name, amount*{int(self.bill_info[j][1])} FROM recipe where product_name = '{self.bill_info[j][0]}'"
            a.execute(sql)
            outofstock = a.fetchall()   # 소진된 재고량 ((재료명, 수량*주문수))
            # 인벤토리 테이블에 주문량 만큼 재고 차감
            for i in range(len(outofstock)):
                # 재료의 남아 있는 양 불러옴
                sql1 = f"SELECT total_amount FROM inventory where material_name = '{outofstock[i][0]}'" # 재료명
                a.execute(sql1)
                stock_info = a.fetchall()   # 현재 재고량
                # 남은 재고량 = 현재 재고량 - 사용량
                remain_stock = int(stock_info[0][0]) - int(outofstock[i][1])
                # 남은 재고량으로 업데이트
                sql2 = f"update inventory set total_amount = {remain_stock} where material_name = '{outofstock[i][0]}'"
                a.execute(sql2)
                conn.commit()
        self.showStock_table()

    def canMake(self):
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000',
                               db='malatang')
        a = conn.cursor()
        list = []  # 빈 리스트 생성, 만들 수 있는 양 넣어줄 예정
        for j in range(len(self.bill_info)):
            # 레시피 테이블에서 상품명에 해당하는 재료, 수량 가져움
            sql = f"SELECT material_name, amount FROM recipe where product_name = '{self.bill_info[j][0]}'" # 주문 받은 상품명 넣을 예정
            a.execute(sql)
            amount_1 = a.fetchall()  # 1인분 ((재료명, 수량))
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
        sql = f"SELECT distinct account_name, order_code, order_state FROM order_info"
        a.execute(sql)
        self.stock_info = a.fetchall()
        # ((고객, 주문 번호, 주문 상태))
        row = 0
        self.orderlist.setRowCount(len(self.stock_info))
        for i in self.stock_info:
            self.orderlist.setItem(row, 0, QTableWidgetItem(str(i[0])))
            self.orderlist.setItem(row, 1, QTableWidgetItem(str(i[1])))  # type = int
            self.orderlist.setItem(row, 2, QTableWidgetItem(str(i[2])))
            row += 1

    # 테이블 위젯 클릭 하면 주문정보 보이게 하기
    def showProduct(self, row, column):
        item = self.orderlist.selectedItems()   # 선택한 셀의 행을 반환(qt에서 행 선택으로 바꿔야함)
        # MySQL에서 import 해오기
        conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000',
                               db='malatang')
        a = conn.cursor()
        sql1 = f"SELECT product_name, product_quantity FROM order_info where order_code = {int(item[1].text())}"
        a.execute(sql1)
        self.bill_info = a.fetchall()
        row1 = 0
        self.bill_tableWidget.setRowCount(len(self.bill_info))
        for i in self.bill_info:
            self.bill_tableWidget.setItem(row1, 0, QTableWidgetItem(str(i[0])))
            self.bill_tableWidget.setItem(row1, 1, QTableWidgetItem(str(i[1])))  # type = int
            row1 += 1
        # 쓰레드 시작
        self.ira = shortageAlarm(self)
        self.ira.start()

    def sendProduct(self):
        if not bool(self.bill_tableWidget.rowCount()):
            QMessageBox.information(self,"알림", "고객주문을 선택해주세요")
        else:
            self.confirmStock()



if __name__ == "__main__":

    app = QApplication(sys.argv)

    widget = QtWidgets.QStackedWidget()

    mainWindow = Search()

    widget.addWidget(mainWindow)

    widget.setFixedHeight(831)
    widget.setFixedWidth(1061)
    widget.show()
    app.exec_()