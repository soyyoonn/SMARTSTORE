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

        # 콤보박스에 상품이름 DB가져와서 모두 넣는 함수 실행
        self.method_cbbProductSetting()

        # 콤보박스 선택하면 테이블 위젯에 BoM 보여주기
        self.cbb_productName.currentIndexChanged.connect(self.method_showBom)

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


if __name__ == "__main__":

    app = QApplication(sys.argv)

    widget = QtWidgets.QStackedWidget()

    mainWindow = Search()

    widget.addWidget(mainWindow)

    widget.setFixedHeight(835)
    widget.setFixedWidth(1059)
    widget.show()
    app.exec_()