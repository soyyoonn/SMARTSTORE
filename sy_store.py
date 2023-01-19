import pymysql
import sys
import time
import random
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
import threading

# conn = pymysql.connect(host='localhost', port=3306, user='root', password='00000000', db='sy',
#                                charset='utf8')

form_class = uic.loadUiType("smartstore.ui")[0]


class smartstore(QMainWindow,form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget_2.setCurrentIndex(0)
        self.log_check = False   # 로그인 체크
        self.checkStatus = False  # 중복확인 체크
        self.btn_home1.clicked.connect(self.move_main)   # 메인 페이지로 이동
        self.btn_home2.clicked.connect(self.move_main)
        self.btn_home3.clicked.connect(self.move_main)
        self.btn_home4.clicked.connect(self.move_main)
        self.btn_home5.clicked.connect(self.move_main)
        self.btn_login.clicked.connect(self.move_login)  # 로그인 페이지로 이동
        self.signup_Button.clicked.connect(self.move_signup)  # 회원가입 페이지로 이동
        self.login_Button.clicked.connect(self.login)   # 로그인 버튼 클릭 후 login 메서드 실행
        self.btn_join.clicked.connect(self.join)        # 가입하기 버튼 클릭 후 join 메서드 실행
        self.btn_duplication.clicked.connect(self.double_Check)  # 중복확인 버튼 클릭 후 double_Check 메서드 실행
        self.onlyInt = QIntValidator()
        self.phone.setValidator(self.onlyInt)   # 연락처 값 숫자로만 입력받기
        self.joinid.textChanged.connect(self.double_change)   # 중복체크 하고 아이디 바꿀 시 다시 중복체크 하기
        self.cstable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # 문의관리 테이블 위젯 헤더 조절
        self.btn_cs.clicked.connect(self.move_cs) # 문의관리 페이지로 이동
        self.btn_check3.clicked.connect(self.cslist) # 문의 내역을 보여준다
        self.btn_answer.clicked.connect(self.check_answer) # 답변 등록 완료 실행
        self.btn_test.clicked.connect(self.start_test)
        self.btn_end.clicked.connect(self.end_test)
        self.btn_qna.clicked.connect(self.move_testqna)
        self.btn_qna.hide()
        self.end = False
        self.thr_cs = thread_cs(self)

        # 빈리스트 넣어주기
        self.testcslist = []

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
        # if self.log_check == False:
        #     QMessageBox.information(self, '알림', '로그인을 해주세요')
        #     self.stackedWidget.setCurrentIndex(1)
        #     self.clear_check()
        # elif self.log_check == True:
        self.stackedWidget.setCurrentIndex(5)

    def move_testqna(self):
        self.stackedWidget.setCurrentIndex(5)
        self.btn_qna.hide()


    def start_test(self):
        self.stackedWidget_2.setCurrentIndex(1)
        # thread 시작
        self.thr_cs.start()

    def end_test(self):
        self.stackedWidget_2.setCurrentIndex(0)
        self.end = True

    # 아이디, 비밀번호 클리어
    def clear_check(self):
        self.id.clear()
        self.pw.clear()

    # 로그인 실행
    def login(self):
        id = self.id.text()
        pw = self.pw.text()
        if id == '' or pw == '': # 아이디나 비밀번호를 입력하지 않았을 때
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
        if joinpw != joinpw2: # 입력된 비밀번호가 다를 때
            QMessageBox.critical(self, "알림", "비밀번호가 일치하지 않습니다. 다시 확인해주세요")
        elif self.checkStatus == False: # 아이디 중복 확인 안했을때
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
        cursor.execute(f"SELECT * FROM customerservice WHERE division = '고객'") # 구분이 고객인 정보만 불러온다
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
        self.row = self.cstable.selectedItems()        # 테이블 위젯의 항목 리스트 형식으로 반환된 값을 row에 저장
        print(self.row)
        self.date = self.row[0].text()   # 날짜
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
            self.cstable.setEditTriggers(QAbstractItemView.AllEditTriggers)    # 테이블 위젯 수정 가능하게 변경

            conn = pymysql.connect(host='10.10.21.102', port=3306, user='malatang', password='0000', db='malatang',
                                   charset='utf8')
            # conn = pymysql.connect(host='localhost', port=3306, user='root', password='00000000', db='sy',
            #                        charset='utf8')
            cursor = conn.cursor()
            cursor.execute(f"UPDATE customerservice SET answer='{self.answer}' WHERE order_code='{self.order_code}'")
            conn.commit()
            conn.close()
            QMessageBox.information(self, '알림', '답변이 등록됐습니다.')
        except: pass

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

    myWindow = smartstore()

    myWindow.show()

    app.exec_()