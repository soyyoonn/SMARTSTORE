import datetime
import pymysql
import sys

from PyQt5.QtGui import QIntValidator
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

        # ---------------------- 상품등록 UI 세팅 ----------------------
        # (임시) 위젯 인덱스 3번에서 바로 보이게 함
        self.stackedWidget.setCurrentIndex(4)
        # 테이블 위젯의 헤더 정렬
        self.table_recipe.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 재료 리스트 위젯에 재료 종류 출력
        self.method_printMaterial()

        # 순재료가, 판매가에는 숫자만 입력 가능
        self.onlyInt = QIntValidator()
        self.product_price.setValidator(self.onlyInt)
        self.product_sellingPrice.setValidator(self.onlyInt)

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
        elif type(material_weight) == str:
            QMessageBox.information(self, '입력 오류', '레시피에 담을 재료의 양을 정수로 적어주세요')
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

    # 상품 등록 버튼을 누르면 적어야 하는 것들 다 적었는지 확인하는 메서드(임시)
    def method_checkRegistration(self):
        print(f'입력: {self.product_price.text()}, {self.product_sellingPrice.text()}, {self.productname.text()}')
        self.recipeMaterial.clear()
        self.method_table_recipeAdditem()
        self.product_price.clear()
        self.product_sellingPrice.clear()
        self.productname.clear()


if __name__ == "__main__":

    app = QApplication(sys.argv)

    widget = QtWidgets.QStackedWidget()

    mainWindow = Search()

    widget.addWidget(mainWindow)

    widget.setFixedHeight(835)
    widget.setFixedWidth(1059)
    widget.show()
    app.exec_()