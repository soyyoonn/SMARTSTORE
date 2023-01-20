import threading
import time
import pymysql
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QIntValidator



# ---------------------------------- 송화 ----------------------------------
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
        self.parent.showOrderlist()

class orderRemind(QThread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        while True:
            if self.parent.threadend == True:
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


form_class = uic.loadUiType("smartstore.ui")[0]


class SmartStore(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # ---------------------------------- 소윤 ----------------------------------
        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget_2.setCurrentIndex(1)
        self.log_check = False    # 로그인 체크
        self.checkStatus = False  # 중복확인 체크
        self.btn_home1.clicked.connect(self.move_main)   # 메인 페이지로 이동
        self.btn_home2.clicked.connect(self.move_main)
        self.btn_home3.clicked.connect(self.move_main)
        self.btn_home4.clicked.connect(self.move_main)
        self.btn_home5.clicked.connect(self.move_main)
        self.btn_login.clicked.connect(self.move_login)   # 로그인 페이지로 이동
        self.signup_Button.clicked.connect(self.move_signup)   # 회원가입 페이지로 이동
        self.login_Button.clicked.connect(self.login)    # 로그인 버튼 클릭 후 login 메서드 실행
        self.btn_join.clicked.connect(self.join)         # 가입하기 버튼 클릭 후 join 메서드 실행
        self.btn_duplication.clicked.connect(self.double_Check)   # 중복확인 버튼 클릭 후 double_Check 메서드 실행
        self.onlyInt = QIntValidator()
        self.phone.setValidator(self.onlyInt)    # 연락처 값 숫자로만 입력받기
        self.joinid.textChanged.connect(self.double_change)    # 중복체크 하고 아이디 바꿀 시 다시 중복체크 하기
        self.cstable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 문의관리 테이블 위젯 헤더 조절
        self.btn_cs.clicked.connect(self.move_cs)  # 문의관리 페이지로 이동
        self.btn_check3.clicked.connect(self.cslist)  # 문의 내역을 보여준다
        self.btn_answer.clicked.connect(self.check_answer)  # 답변 등록 완료 실행
        self.btn_test.clicked.connect(self.start_test)  # 테스트 버튼 누르면 스레드 시작
        self.btn_end.clicked.connect(self.end_test)    # 종료 버튼 누르면 스레드 종료
        self.btn_qna.clicked.connect(self.move_testqna) # 문의 알림 온 버튼 누르면 페이지 이동
        self.btn_qna.hide()  # 처음 실행 시 문의 알림 버튼 안보이게
        self.end = False  # 스레드 종료 체크
        self.thr_cs = thread_cs(self)
        # 빈리스트 넣어주기
        self.testcslist = []

        # ---------------------------------- 송화 ----------------------------------
        self.list = []
        self.threadend = False  # 스레드 종료

        # 쓰레드
        self.oa = orderAlarm(self)
        self.oa.start()

        # 페이지 이동
        self.stackedWidget.setCurrentIndex(0)
        self.btn_order.clicked.connect(self.goStock)  # 홈페이지 - 주문관리버튼
        self.btn_home3.clicked.connect(self.goHome)  # 상품등록페이지 - 홈버튼

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

        # ---------------------------------- 연수 ----------------------------------
        self.btn_product.clicked.connect(lambda method_moveProductWidget: self.stackedWidget.setCurrentIndex(4))  # 홈페이지 - 상품등록버튼

        # 테이블 위젯의 헤더 정렬(헤더별 맞추기)
        self.table_recipe.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_BoM.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 테이블 위젯의 헤더 정렬(데이터 길이별 맞추기)
        self.table_productinfo.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # 재료 리스트 위젯에 재료 종류 출력
        self.method_printMaterial()
        # 상품 테이블 위젯에 상품 정보 출력
        self.method_printProduct()

        # 순재료가, 판매가에는 숫자만 입력 가능
        self.onlyInt = QIntValidator()
        self.product_price.setValidator(self.onlyInt)
        self.product_sellingPrice.setValidator(self.onlyInt)

        # 콤보박스 선택하면 테이블 위젯에 BoM 보여주기
        self.cbb_productName.currentIndexChanged.connect(self.method_showBom)

        # 콤보박스에 상품이름 DB가져와서 모두 넣는 함수 실행
        self.method_cbbProductSetting()

        # ---------------------- 상품등록 시그널 ----------------------
        # 레시피의 전체 재료가 들어갈 리스트
        self.recipeMaterial = []

        # 재료 목록에서 재료를 선택하면 선택 재료 lineEdit 박스에 출력
        self.list_material.itemClicked.connect(self.method_printToMaterialChoose)

        # 넣기 버튼 누르면 레세피에 들어갈 재료를 확인하는 메서드 실행
        self.btn_productInput.clicked.connect(self.method_checkWeight)

        # 상품 빼기 버튼 눌렀을 때
        self.btn_productOutput.clicked.connect(self.method_popMaterial)

        # 상품등록 버튼을 눌렀을 때 적어야 하는 것들 다 적었는지 확인하는 함수 실행
        self.btn_registration.clicked.connect(self.method_checkRegistration)

    # ---------------------------------- 소윤 ----------------------------------
    # 메인 페이지로 이동
    def move_main(self):
        self.stackedWidget.setCurrentIndex(0)

    # 로그인 페이지로 이동
    def move_login(self):
        self.stackedWidget.setCurrentIndex(1)
        self.clear_check()
        if self.log_check == True:
            self.logout()

    # 회원가입 페이지로 이동
    def move_signup(self):
        self.stackedWidget.setCurrentIndex(2)
        self.joinid.clear()
        self.joinpw.clear()
        self.joinpw2.clear()
        self.name.clear()
        self.phone.clear()
        self.address.clear()

    # 문의관리 페이지로 이동
    def move_cs(self):
        if self.log_check == False:
            QMessageBox.information(self, '알림', '로그인을 해주세요')
            self.stackedWidget.setCurrentIndex(1)
            self.clear_check()
        elif self.log_check == True:
            self.stackedWidget.setCurrentIndex(5)

    def move_testqna(self):
        self.stackedWidget.setCurrentIndex(5)
        self.btn_qna.hide()

    # 테스트 버튼 누르면
    def start_test(self):
        # 종료 버튼으로 변경 된다
        self.stackedWidget_2.setCurrentIndex(0)
        # thread 시작
        self.thr_cs.start()

    # 종료 버튼 누르면
    def end_test(self):
        # 테스트 버튼으로 변경 된다
        self.stackedWidget_2.setCurrentIndex(1)
        self.end = True

    # 아이디, 비밀번호 클리어
    def clear_check(self):
        self.id.clear()
        self.pw.clear()

    # 로그인 실행
    def login(self):
        id = self.id.text()
        pw = self.pw.text()
        if id == '' or pw == '':  # 아이디나 비밀번호를 입력하지 않았을 때
            QMessageBox.information(self, '알림', '모두 입력해주세요')
            return
        conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000', db='malatang',
                               charset='utf8')
        # conn = pymysql.connect(host='localhost', port=3306, user='root', password='00000000', db='sy',
        #                        charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM account_info WHERE account_id='{id}' AND account_pw='{pw}'")
        self.log = cursor.fetchall()

        if bool(self.log) == False:  # 아이디나 비밀번호가 맞지 않을 때
            QMessageBox.information(self, '알림', '아이디 또는 비밀번호를 확인해주세요')

        elif self.log[0][2] == id:  # 입력한 아이디가 DB에 저장된 아이디와 일치할 때
            QMessageBox.information(self, '알림', f'{self.log[0][1]}님 로그인 되었습니다')
            self.log_check = True
            self.btn_login.setText('로그아웃')  # 로그인 버튼 텍스트 로그아웃으로 변경
            self.move_main()

    # 로그아웃 실행
    def logout(self):
        QMessageBox.information(self, '알림', f'{self.log[0][1]}님 로그아웃 되었습니다')
        self.log_check = False
        self.btn_login.setText('로그인')  # 로그아웃 버튼 텍스트 로그인으로 변경
        self.move_main()

    # 회원가입 아이디 중복 확인
    def double_Check(self):
        id = self.joinid.text()  # 아이디에 입력되는 텍스트
        conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000', db='malatang',
                               charset='utf8')
        # conn = pymysql.connect(host='localhost', port=3306, user='root', password='00000000', db='sy',
        #                        charset='utf8')
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM account_info WHERE account_id = '{id}'")
        check = cursor.fetchall()
        conn.close()
        if check != ():
            QMessageBox.critical(self, "알림", "중복된 아이디입니다")
        else:
            QMessageBox.information(self, "알림", "사용 가능한 아이디입니다")
            self.checkStatus = True
            self.id.textChanged.connect(self.move_signup)

    # 아이디 중복 체크
    def double_change(self):
        self.checkStatus = False

    # 회원가입 실행
    def join(self):
        joinid = self.joinid.text()  # 아이디
        joinpw = self.joinpw.text()  # 비밀번호
        joinpw2 = self.joinpw2.text()  # 비밀번호 확인
        name = self.name.text()  # 이름
        phone = self.phone.text()  # 연락처
        address = self.address.text()  # 주소
        # 회원가입 시 필요한 조건
        if joinpw != joinpw2:  # 입력된 비밀번호가 다를 때
            QMessageBox.critical(self, "알림", "비밀번호가 일치하지 않습니다. 다시 확인해주세요")
        elif self.checkStatus == False:  # 아이디 중복 확인 안했을때
            QMessageBox.critical(self, "알림", "아이디 중복 확인을 해주세요")
        elif joinid == '' or joinpw == '' or name == '' or phone == '' or address == '':  # 입력 되지 않은 정보가 있을때
            QMessageBox.critical(self, "알림", "정보를 입력하세요")
        else:
            conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000', db='malatang',
                                   charset='utf8')
            # conn = pymysql.connect(host='localhost', port=3306, user='root', password='00000000', db='sy',
            #                        charset='utf8')
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT INTO account_info (account_name, account_id, account_pw) VALUES('{name}','{joinid}','{joinpw}')")
            conn.commit()
            conn.close()
            QMessageBox.information(self, "알림", "회원가입 완료")
            # 회원가입에 입력된 정보 클리어 해주기
            self.joinid.clear()
            self.joinpw.clear()
            self.joinpw2.clear()
            self.name.clear()
            self.phone.clear()
            self.address.clear()
            self.stackedWidget.setCurrentIndex(1)

    # 문의관리 내역 보여주는 메서드
    def cslist(self):
        conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000', db='malatang',
                               charset='utf8')

        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM customerservice WHERE division = '고객'")  # 구분이 고객인 정보만 불러온다
        self.cs = cursor.fetchall()
        conn.close()
        for i in range(len(self.cs)):
            print(self.cs[i])
        self.cstable.setRowCount(len(self.cs))

        Row = 0
        for i in self.cs:
            self.cstable.setItem(Row, 0, QTableWidgetItem(str(i[0])))  # 날짜
            self.cstable.setItem(Row, 1, QTableWidgetItem(i[3]))  # 고객이름
            self.cstable.setItem(Row, 2, QTableWidgetItem(i[4]))  # 주문번호
            self.cstable.setItem(Row, 3, QTableWidgetItem(i[6]))  # 상품이름
            self.cstable.setItem(Row, 4, QTableWidgetItem(i[7]))  # 문의내용
            self.cstable.setItem(Row, 5, QTableWidgetItem(i[8]))  # 답변
            Row += 1

    # 답변 완료 시 실행되는 메서드
    def check_answer(self):
        # 선택된 셀이 없을 경우
        if self.cstable.currentRow() == -1:
            QMessageBox.information(self, '알림', '선택된 값이 없습니다.')
            return
        self.data = self.cs[self.cstable.currentRow()]  # 테이블 위젯의 값을 data에 저장
        print(self.data)
        self.row = self.cstable.selectedItems()  # 테이블 위젯의 항목 리스트 형식으로 반환된 값을 row에 저장
        print(self.row)
        self.date = self.row[0].text()  # 날짜
        self.account_name = self.row[1].text()  # 고객이름
        self.order_code = self.row[2].text()  # 주문번호
        self.product_name = self.row[3].text()  # 상품이름
        self.question = self.row[4].text()  # 문의내용
        self.answer = self.row[5].text()  # 답변
        print(self.date)
        print(self.account_name)
        print(self.order_code)
        print(self.product_name)
        print(self.question)
        print(self.answer)
        ck_chage = QMessageBox.question(self, '알림', '답변을 작성하겠습니까?', QMessageBox.Yes | QMessageBox.No, )
        if ck_chage == QMessageBox.Yes:
            self.customer_answer()
        else:
            return

    # 답변 데이터 업로드 및 답변완료 메시지 박스
    def customer_answer(self):
        try:
            self.cstable.setEditTriggers(QAbstractItemView.AllEditTriggers)  # 테이블 위젯 수정 가능하게 변경

            conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000', db='malatang',
                                   charset='utf8')
            # conn = pymysql.connect(host='localhost', port=3306, user='root', password='00000000', db='sy',
            #                        charset='utf8')
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE customerservice SET answer='{self.answer}' WHERE order_code='{self.order_code}'")
            conn.commit()
            conn.close()
            QMessageBox.information(self, '알림', '답변이 등록됐습니다.')
        except:
            pass

    # --------------------------------------------------------------------

    def testmaketable(self):
        # 테이블 위젯 헤더를 제외하고 한 번 초기화
        self.cstable.clearContents()

        # table_recipe 테이블 위젯의 row 개수 정해주기
        self.cstable.setRowCount(len(self.testcslist))

        Row = 0
        for i in self.testcslist:
            self.cstable.setItem(Row, 0, QTableWidgetItem(str(i[0])))  # 날짜
            self.cstable.setItem(Row, 1, QTableWidgetItem(i[3]))  # 고객이름
            self.cstable.setItem(Row, 2, QTableWidgetItem(i[4]))  # 주문번호
            self.cstable.setItem(Row, 3, QTableWidgetItem(i[6]))  # 상품이름
            self.cstable.setItem(Row, 4, QTableWidgetItem(i[7]))  # 문의내용
            self.cstable.setItem(Row, 5, QTableWidgetItem(i[8]))  # 답변
            Row += 1

    # ---------------------------------- 송화 ----------------------------------

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
        self.showOrderlist()

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
            self.stock_tableWidget.setItem(row, 2, QTableWidgetItem(str(i[2])))  # type = int
            self.stock_tableWidget.setItem(row, 3, QTableWidgetItem(str(i[3])))  # type = decimal
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
            sql2 = f"update order_info set order_state = '발송완료' where order_code = {(int(item[1].text()))}"
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
            outofstock = a.fetchall()  # 소진된 재고량 ((재료명, 수량*주문수))
            # 인벤토리 테이블에 주문량 만큼 재고 차감
            for i in range(len(outofstock)):
                # 재료의 남아 있는 양 불러옴
                sql1 = f"SELECT total_amount FROM inventory where material_name = '{outofstock[i][0]}'"  # 재료명
                a.execute(sql1)
                stock_info = a.fetchall()  # 현재 재고량
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
            sql = f"SELECT material_name, amount FROM recipe where product_name = '{self.bill_info[j][0]}'"  # 주문 받은 상품명 넣을 예정
            a.execute(sql)
            amount_1 = a.fetchall()  # 1인분 ((재료명, 수량))
            for i in range(len(amount_1)):
                # 만들 수 있는 양(필요한 재료 양) = 현재 재고량 / 1인분량 의 최솟값
                sql1 = f"SELECT round(total_amount/{int(amount_1[i][1])}, 0) FROM inventory where material_name = '{amount_1[i][0]}'"  # 재료명
                a.execute(sql1)
                stock_info = a.fetchall()
                list.append(stock_info)
        cancook = min(list)  # 최솟값 만큼 만들 수 있다!

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
        item = self.orderlist.selectedItems()  # 선택한 셀의 행을 반환(qt에서 행 선택으로 바꿔야함)
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
            QMessageBox.information(self, "알림", "고객주문을 선택해주세요")
        else:
            self.confirmStock()

    # ---------------------------------- 연수 ----------------------------------
    # 콤보박스 선택하면 테이블 위젯에 BoM 보여주기
    def method_showBom(self):
        # 콤보박스로 선택한 상품이름 변수에 저장
        productName = self.cbb_productName.currentText()

        # DB 열기
        get_bom = pymysql.connect(host='10.10.21.102', user='malatang', password='0000', db='malatang',
                                      charset='utf8')
        # DB와 상호작용하기 위해 연결해주는 cursor 객체 만듬
        product = get_bom.cursor()

        # recipe DB에서 BoM 정보를 가져오고 싶어
        sql = f"SELECT material_name, amount FROM recipe WHERE product_name = '{productName}'"

        # execute 메서드로 db에 sql 문장 전송
        product.execute(sql)
        data_bom = product.fetchall()  # 재료 데이터에서 재료들의 이름만 모두 가져온 정보 2중 튜플로 저장
        # DB 닫아주기
        get_bom.close()

        # 테이블 위젯 헤더를 제외하고 한 번 초기화
        self.table_BoM.clearContents()

        # table_recipe 테이블 위젯의 row 개수 정해주기
        self.table_BoM.setRowCount(len(data_bom))

        for i in range(len(data_bom)):
            for j in range(len(data_bom[i])):
                self.table_BoM.setItem(i, j, QTableWidgetItem(str(data_bom[i][j])))

        print(data_bom)

    # 콤보박스에 상품이름 DB가져와서 모두 넣는 메서드
    def method_cbbProductSetting(self):
        # 상품 이름만 가져오는 함수 실행, return값 productName에 담아주기
        productName = self.method_getProductName()

        # for문으로 콤보박스에 상품이름 넣어주기
        for i in productName:
            self.cbb_productName.addItem(i)

    # 상품 테이블 위젯에 상품 정보 가져오기
    def method_printProduct(self):
        data_product = self.method_getProduct()

        # 테이블 위젯 헤더를 제외하고 한 번 초기화
        self.table_productinfo.clearContents()

        # table_recipe 테이블 위젯의 row 개수 정해주기
        self.table_productinfo.setRowCount(len(data_product))

        for i in range(len(data_product)):
            for j in range(len(data_product[i])):
                self.table_productinfo.setItem(i, j, QTableWidgetItem(str(data_product[i][j])))

    # 상품 정보 DB 가져오기
    def method_getProduct(self):
        # DB 열기
        get_product = pymysql.connect(host='10.10.21.102', user='malatang', password='0000', db='malatang',
                                       charset='utf8')
        # DB와 상호작용하기 위해 연결해주는 cursor 객체 만듬
        product = get_product.cursor()

        # 상품 데이터에서 상품이름과 상품가격 상품상태를 가져오고싶어
        sql = f"SELECT product_name, product_price, product_stat FROM product_info"

        # execute 메서드로 db에 sql 문장 전송
        product.execute(sql)
        data_product = product.fetchall()  # 재료 데이터에서 재료들의 이름만 모두 가져온 정보 2중 튜플로 저장
        # DB 닫아주기
        get_product.close()

        # 재료 데이터에서 재료 정보를 가져와서 return 해줌
        return data_product

    # 재료 종류 DB에서 가져오기
    def method_getMaterial(self):
        # DB 열기
        get_material = pymysql.connect(host='10.10.21.102', user='malatang', password='0000', db='malatang', charset='utf8')
        # DB와 상호작용하기 위해 연결해주는 cursor 객체 만듬
        material = get_material.cursor()

        # 재료 데이터에서 재료들의 이름만 모두 가져오고싶어
        sql = f"SELECT material_name FROM inventory"

        # execute 메서드로 db에 sql 문장 전송
        material.execute(sql)
        data_material = material.fetchall()  # 재료 데이터에서 재료들의 이름만 모두 가져온 정보 2중 튜플로 저장
        # DB 닫아주기
        get_material.close()

        # 재료 데이터에서 재료 정보를 가져와서 return 해줌
        return data_material

    # 리스트 위젯에 재료 정보 저장
    def method_printMaterial(self):
        material_info = self.method_getMaterial()

        # for문으로 리스트 위젯에 재료 정보 저장해주기
        for one_material in material_info:
            self.list_material.addItem(one_material[0])

    # 재료 목록 리스트 위젯에서 재료를 선택하면 선택한 재료를 lineEdit 박스에 출력하게 함(lamda로 할까?)
    def method_printToMaterialChoose(self):
        self.led_materialChoose.setText(self.list_material.currentItem().text())
        print(self.list_material.currentItem().text())

    # 레시피에 들어갈 재료를 확인하는 메서드(넣기버튼)
    def method_checkWeight(self):
        # 재료 이름 변수에 저장
        material_name = self.led_materialChoose.text()
        # 재료의 양을 정수로 줄 수 있으면 정수로 주고
        try:
            material_weight = int(self.led_materialWeight.text())
        # 타입 에러가 뜬다면 그냥 str형태로 둔다
        except ValueError:
            material_weight = self.led_materialWeight.text()

        # 입력란에 적지 않았을 때
        if not bool(material_name):
            QMessageBox.information(self, '입력 오류', '레시피에 담을 재료를 정해주세요')
        elif not bool(material_weight):
            QMessageBox.information(self, '입력 오류', '레시피에 담을 재료의 양을 정해주세요')
        # 재료의 양을 정수로 입력하지 않았을 때
        elif type(material_weight) == str or material_weight <= 0:
            QMessageBox.information(self, '입력 오류', '레시피에 담을 재료의 양을 양수로 적어주세요')
        # 개발자의 요구대로 입력했을 때
        else:
            # 재료당 가격 구하는 함수 실행해서 재료당 가격 변수에 저장
            pricePerMaterial = self.method_pricePerMaterial()
            print('재료 이름:', material_name, '무게(g):', material_weight, '재료당가격:', pricePerMaterial)

            # 레시피 재료 리스트에 재료이름, 무게, 재료당가격 넣어주기
            self.recipeMaterial.append([material_name, material_weight, pricePerMaterial])

            # table_recipe 테이블 위젯에 item 넣어주기 함수 실행
            self.method_table_recipeAdditem()

            # 리스트 위젯에서 테이블 위젯에 넣은 재료의 row 번호 찾기
            row = 0
            while True:
                if material_name == self.list_material.item(row).text():
                    break
                else:
                    row += 1

            # 리스트 위젯에서 테이블 위젯에 넣은 재료의 이름 빼주기
            self.list_material.takeItem(row)

            # 테이블에 넣고 나면 클리어 해주기
            self.led_materialChoose.clear()
            self.led_materialWeight.clear()

    # 상품 빼기 버튼 눌렀을 때 실행되는 메서드(빼기버튼)
    def method_popMaterial(self):
        # 테이블 위젯의 상품을 row로 선택(선택한 항목들을 리스트 형식으로 반환)
        selected_material = self.table_recipe.selectedItems()

        # 선택하지 않고 빼기 버튼 눌렀을 시
        if not bool(selected_material):
            QMessageBox.information(self, '입력 오류', '빼고싶은 항목을 선택해주세요')
        else:
            i = 0
            while True:
                # 선택한 상품 다시 리스트 위젯에 넣어주기 & 테이블 위젯에서 빼기
                if self.recipeMaterial[i][0] == selected_material[0].text():
                    self.list_material.addItem(selected_material[0].text())
                    self.recipeMaterial.remove(self.recipeMaterial[i])
                    break
                else:
                    i += 1

        # 테이블 위젯 다시 출력하기
        self.method_table_recipeAdditem()

    # table_recipe 테이블 위젯에 item 넣어주기 메서드
    def method_table_recipeAdditem(self):
        # 순 재료가 변수
        allMaterialPrice = 0

        # 테이블 위젯 헤더를 제외하고 한 번 초기화
        self.table_recipe.clearContents()

        # table_recipe 테이블 위젯의 row 개수 정해주기
        self.table_recipe.setRowCount(len(self.recipeMaterial))

        # table_recipe 테이블 위젯에 item 넣어주기
        for i in range(len(self.recipeMaterial)):
            for j in range(len(self.recipeMaterial[i])):
                # 재료 무게당 가격 정산
                if j == 2:
                    allMaterialPrice += self.recipeMaterial[i][j]
                self.table_recipe.setItem(i, j, QTableWidgetItem(str(self.recipeMaterial[i][j])))

        # 순 재료가 lineEdit product_price박스에 넣어주기(문자열형태로)
        self.product_price.setText(str(allMaterialPrice))

    # 레시피에 들어갈 재료의 1g당 가격 가져와서 재료당가격 구해주기
    def method_pricePerMaterial(self):
        material_name = self.led_materialChoose.text()
        # 바로 int형으로 바꿔주는 이유: 이 함수를 실행시킬 곳은 이미 try, except 문으로 int문으로 바꿀 수 있게 구분해놨기 때문
        material_weight = int(self.led_materialWeight.text())

        # DB 열기
        get_material = pymysql.connect(host='10.10.21.102', user='malatang', password='0000', db='malatang',
                                       charset='utf8')
        # DB와 상호작용하기 위해 연결해주는 cursor 객체 만듬
        material = get_material.cursor()
        # 재료 데이터에서 재료의 이름이 material_name인데 그 재료의 1g당 가격에 material_weight만큼 곱한 값을 가져오고싶어
        sql = f"SELECT unit_price*{material_weight} FROM inventory WHERE material_name = '{material_name}'"
        # execute 메서드로 db에 sql 문장 전송
        material.execute(sql)
        data_recipe = material.fetchall()  # 재료 데이터에서 재료들의 이름만 모두 가져온 정보 2중 튜플로 저장
        # DB 닫아주기
        get_material.close()

        # decimal 모듈 형태로 return 하기
        return data_recipe[0][0]

    # 상품 정보의 이름만 가져오는 메서드(이게 맞나..)
    def method_getProductName(self):
        # DB 열기
        get_product = pymysql.connect(host='10.10.21.102', user='malatang', password='0000', db='malatang',
                                      charset='utf8')
        # DB와 상호작용하기 위해 연결해주는 cursor 객체 만듬
        product = get_product.cursor()

        # 상품 데이터에서 상품이름과 상품가격 상품상태를 가져오고싶어
        sql = f"SELECT product_name FROM product_info"

        # execute 메서드로 db에 sql 문장 전송
        product.execute(sql)
        data_productName = product.fetchall()  # 재료 데이터에서 재료들의 이름만 모두 가져온 정보 2중 튜플로 저장
        # DB 닫아주기
        get_product.close()

        productName = []

        # 2중 튜플 -> 보기 좋게 리스트화
        for i in data_productName:
            productName.append(i[0])

        # 재료 데이터에서 재료 정보를 가져와서 return 해줌
        return productName

    # 상품 등록 버튼을 누르면 적어야 하는 것들 다 적었는지 확인, 데이터에 넣는 메서드
    def method_checkRegistration(self):
        distinct = False

        print(f'입력: {self.product_price.text()}, {self.product_sellingPrice.text()}, {self.productname.text()}')
        productName = self.method_getProductName()

        for i in productName:
            # 입력한 상품명이 이미 상품명에 있는 이름이면 중복 변수 True로 바꿔줌
            if i == self.productname.text():
                distinct = True
                break

        # 레시피 입력하기
        if not bool(self.table_recipe.rowCount()):
            QMessageBox.information(self, '입력 오류', '레시피를 입력해주세요')
        # 판매가격 입력하기
        elif not bool(self.product_sellingPrice.text()):
            QMessageBox.information(self, '입력 오류', '판매가격을 입력해주세요')
        # 판매가격 순 재료가보다 낮으면 판매 불가
        elif int(self.product_sellingPrice.text()) <= float(self.product_price.text()):
            QMessageBox.information(self, '판매 경고', '순 재료가보다 더 낮은 가격으로 팔 수 없습니다')
        # 상품이름 입력하기
        elif not bool(self.productname.text()):
            QMessageBox.information(self, '입력 오류', '상품명을 입력해주세요')
        # 상품명 중복 입력 불가
        elif distinct == True:
            QMessageBox.information(self, '상품명 중복', '동일한 상품명이 있습니다')
        else:
            # 등록한 상품 정보 DB에 넣어주기
            self.method_insertProductInfo()     # product_info DB에 insert
            self.method_insertRecipe()          # recipe DB에 insert

            # ui 초기화해주기
            self.product_price.setText('0')
            self.product_sellingPrice.clear()
            self.productname.clear()

            # 레시피 정보 지우기
            self.recipeMaterial.clear()

            # table_recipe 테이블 불러오는 함수 실행
            self.method_table_recipeAdditem()

            # DB들어간 테이블 위젯 초기화
            self.method_printProduct()

            # 재료 리스트 위젯 초기화
            self.list_material.clear()
            # 리스트 위젯에 다시 재료 넣어주기
            self.method_printMaterial()

            # 콤보박스 정보 업데이트
            self.cbb_productName.clear()
            self.method_cbbProductSetting()

    # 상품 등록하면 상품의 BoM정보 recipe DB에 insert하기
    def method_insertRecipe(self):
        # DB 열기
        add_recipe = pymysql.connect(host='10.10.21.102', user='malatang', password='0000', db='malatang',
                                         charset='utf8')
        # DB와 상호작용하기 위해 연결해주는 cursor 객체 만듬
        recipe = add_recipe.cursor()

        for i in range(len(self.recipeMaterial)):
            print(self.recipeMaterial[i][1])
            # 프로시저로 insert문 넣어주기
            insert_sql = f"call addRecipe('{self.productname.text()}', '{self.recipeMaterial[i][0]}', {self.recipeMaterial[i][1]})"
            # execute 메서드로 db에 sql 문장 전송
            recipe.execute(insert_sql)

        # insert문 실행
        add_recipe.commit()

        # DB 닫아주기
        add_recipe.close()

    # 상품 등록하면 product_info DB에 insert하기
    def method_insertProductInfo(self):
        # DB 열기
        get_productNum = pymysql.connect(host='10.10.21.102', user='malatang', password='0000', db='malatang',
                                      charset='utf8')
        # DB와 상호작용하기 위해 연결해주는 cursor 객체 만듬
        product = get_productNum.cursor()

        # 상품 데이터에서 최대 상품번호(max)를 가져오고싶어(이것도 프로시져 안에 넣고 싶은데 아직 DECLARE 개념도 잘 모르겠고 프로젝트 기간이 별로 안남았으므로 다음 기회에 시도해보겠음)
        find_maxNumSql = f"SELECT MAX(`상품번호`) AS '최대상품번호' FROM (SELECT SUBSTR(product_code, 2, 4) AS '상품번호' FROM product_info) 상품번호테이블"

        # execute 메서드로 db에 sql 문장 전송
        product.execute(find_maxNumSql)
        maxNum_product1 = product.fetchall()  # 최대 상품 번호 저장

        # 최대 상품번호에서 1 더해주고 다시 s000 형태로 만들어주기
        nextNum_product = 's'+(str(int(maxNum_product1[0][0])+1).zfill(3))

        # 프로시저로 insert문 넣어주기
        insert_sql = f"call procedure_addProduct('{nextNum_product}', '{self.productname.text()}', {int(self.product_sellingPrice.text())}, '판매중')"

        # execute 메서드로 db에 sql 문장 전송
        product.execute(insert_sql)

        # insert문 실행
        get_productNum.commit()

        # DB 닫아주기
        get_productNum.close()
        # print(data_product)

# ---------------------------------- 소윤 ----------------------------------
class thread_cs(threading.Thread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        while True:
            if self.parent.end:
                print('쓰레드 종료')
                return
            time.sleep(2)
            conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000', db='malatang',
                                   charset='utf8')
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM customerservice ORDER BY RAND() LIMIT 1")
            testcslist = cursor.fetchall()
            # 2중 튜플
            print(testcslist)
            if testcslist != None:
                self.parent.testcslist.append(list(testcslist[0]))
                self.parent.testmaketable()

                self.parent.btn_qna.show()
                self.parent.btn_qna.setText(f'새로운 문의가 들어왔습니다')

                time.sleep(5)

            conn.commit()
            conn.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    myWindow = SmartStore()

    myWindow.show()

    app.exec_()