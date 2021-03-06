# from CONFIG import * # 개인개발용
from UTIL import * # Publish
import time
import random

def get_board_list():
    titleList = []
    linkList = []
    bs4 = get_bs_by_txt('html.txt')
    uls = bs4.find_all('ul', class_='cafe-menu-list')
    idx = 1
    for ul in uls:
        lis = ul.find_all('li')
        for li in lis:
            if idx in [25,26,27,28,30,31,32,34,38]:
                titleList.append(li.a.get_text().strip())
                linkList.append('https://cafe.naver.com/imsanbu' + li.a['href'])
            idx +=1
    return titleList,linkList
def switch_cafe_main():
    isChange = False
    time.sleep(1)
    while not isChange:
        iframes = driver.find_elements_by_tag_name('iframe')
        for iframe in iframes:
            if iframe.get_attribute('id') == 'cafe_main':
                driver.switch_to.frame(iframe)
                isChange = True
                break
        time.sleep(0.5)


def get_url():
    f = open("{}_{}~{}.txt".format(titleList[inputNum],startDate,endDate).replace('-',''),'w')
    pageIdx = urlStart
    cnt = 0
    while True:
        try:
            log('i',"{} page url extract...".format(pageIdx))
            url = urlFormat.format(startDate, endDate, cafeIdList[inputNum], pageIdx)
            driver.get(url)
            time.sleep(random.randint(urlMin, urlMax))
            switch_cafe_main()
            bs4 = BeautifulSoup(driver.page_source, 'lxml')
            trs = bs4.find('div', class_='article-board m-tcol-c').find_all('tr', align='center')
            for tr in trs:
                cnt += 1
                f.write(iframeUrl + tr.a['href']+'\n')
            driver.switch_to.default_content()
            pageIdx += 1
        except:  # 없으면 터짐
            driver.switch_to.default_content()
            break
    log('s',"{} 개 수집완료".format(cnt))
    f.close()

def get_parsing():
    log('i','파싱 시작 ')
    f = open("{}_{}~{}.txt".format(titleList[inputNum], startDate, endDate).replace('-', ''), 'r')
    lines = f.readlines()
    f.close()
    log('i',"{}개의 URL 존재".format(len(lines)))
    urlIndex = 1
    for url in lines:
        try:
            driver.get(url)
            time.sleep(random.randint(parsingMin, parsingMax))
            switch_cafe_main()
            bs4 = BeautifulSoup(driver.page_source, 'lxml')
            driver.switch_to.default_content()

            id = bs4.find('a', id='linkUrl').get_text().strip().split('/')[-1]
            datetime = bs4.find('td', class_='m-tcol-c date').get_text().strip()
            author = bs4.find("div", class_='etc-box').find('td', class_='p-nick').a.get_text().strip()
            title = bs4.find('div', class_='tit-box').find('span', class_='b m-tcol-c').get_text().strip()
            contentDiv = bs4.find('div', id='tbody')
            # try:
            #     contentDiv.find('div', class_='NHN_Writeform_Main').decompose()
            # except:
            #     pass
            content = contentDiv.get_text().strip()
            content = content.replace('1) 임신여부문의글(피검수치 50이상,2줄 임테기)은 임신중질문방 또는 테스터질문방 이용바랍니다.', '')
            content = content.replace('2) 난자/정자공여 게시물(게시글,덧글,쪽지,채팅 등등)은 금지하고 있습니다.', '')
            content = content.replace('3) 의약품 판매나 드림은 법적으로 금지 대상입니다.', '')
            content = content.replace('★ 잠깐! 게시글 작성 전, 필독 공지! ★', '')
            content = content.replace('- 카페규정 : http://cafe.naver.com/imsanbu/28123090', '')
            content = content.replace('- 게시판별 운영 정책 : http://cafe.naver.com/imsanbu/35756864', '')

            commentList = ['', '', '', '', '']
            commentCnt = 0
            lis = bs4.find('ul', id='cmt_list').find_all('li', class_='')[:5]
            for li in lis:
                commentList[commentCnt] = li.find('span', class_='comm_body').get_text().strip()
                commentCnt += 1
            data = [id, datetime, author, title, content, commentList[0], commentList[1], commentList[2], commentList[3],
                    commentList[4]]
            save_excel(FILENAME.format(titleList[inputNum],datetime[:7]), data, HEADER)
            log('s',"{} / {} 개 완료 ...".format(urlIndex,len(lines)))
            urlIndex += 1
        except:
            Alert(driver).accept()
            log('s', "{} / {} 개 완료 ...".format(urlIndex, len(lines)))
            urlIndex += 1


if __name__ == '__main__':
    #valid_user()
    """
    @ 사용법
    1. 프로그램이 시작되면 카페 게시판 목록이 뜨고 파싱하려는 
       해당게시판 번호를 입력합니다
       
    2. 시작, 종료 날짜를 (YYYY-MM-DD)형식에 맞춰 입력합니다
       예로 )2018-09-01, 2018-09-03 이라고 입력시 
        1일포함 ~ 3일까지(포함) 해당 게시판의 내용들을 검색합니다.
        
    3. URL 파싱 : 내용파싱은 하지않고, 우선 해당날짜에 걸린 카페게시글의 URL만 수집합니다.
       내용파싱 : URL파싱을 하지 않고, 저장해둔 URL LIST(꼭 선행되어야함)를 가지고 내용만 가져옵니다.
       처음시작 : 위 두과정을 같이 하는것입니다. 
       
    4. 그럼 크롬이 켜지고, 로그인 다 완료하시고, 프로그램으로 돌아와서 엔터를 누르면 시작됩니다. 
    
    @ 추가적으로
    1. URL리스트들은 
       게시판이름_시작날짜~종료날짜.txt 파일로 저장됩니다.
       예) 임신준비 질문방_20180901~20180904.txt
       
    2. 결과물 엑셀파일은
       게시판이름_몇월인지.xlsx 파일로 저장됩니다.
       예) 임신준비 질문방_2018.09.xlsx
       
    3. URL 파싱하고 내용파싱은 어케하냐 !
       URL파일이 예를들면 임신준비질문방_20180901~20180931.txt
       이면 내용파싱 맨처음 시작하실때 시작날짜, 종료날짜를 파일과 동일하게 쓰시면 그대로 사용
        가능합니다. 
        
    4. 중간에 내용파싱중에 IP벤이나, VPN연결이 끊어졌을때 대처법
       결과물 엑셀파일을 확인하여 글번호를 확인후에, 
       URL 리스트에 들어가셔서 글번호를 검색하여 결과물에 맨마지막에있는 글번호까지 이전데이터는 그냥
       지우시고 저장하시면 
       URL 리스트에 남은 URL만 돌아갑니다 
       즉, 이미 다된 URL은 수동으로 지우시고 다시 내용파싱하시면 그 URL부터 돌아갑니다.
    """
    '''ㅡㅡㅡㅡㅡ INPUT ㅡㅡㅡㅡㅡ'''
    for idx in range(len(linkList)):
        print(" {} : {} ".format(idx,titleList[idx]))
    inputNum = int ( input(">>> 번호 입력 : ") )
    startDate = input(">>> 시작날짜 입력 (YYYY-MM-DD 형식) : ")
    endDate = input(">>> 종료날짜 입력 (YYYY-MM-DD 형식) : ")
    menu = input(">>> URL 파싱만 0 , 내용파싱만 1, 처음시작은 2 :")

    # driver init
    driver = webdriver.Chrome('./chromedriver')
    driver.get('https://nid.naver.com/nidlogin.login')
    driver.maximize_window()
    doLogin = input(">>> 로그인 후에 엔터를 눌러주세요 : ")
    #Url parsing
    if menu == '0':
        urlMin = int(input(">>> URL 파싱간 딜레이 최소값 정수 입력: "))
        urlMax = int(input(">>> URL 파싱간 딜레이 최대값 정수 입력: "))
        urlStart = int(input(">>> URL 파싱 시작 페이지 입력 (기본값 1 ):"))
        parsingMin = 3
        parsingMax = 7
        get_url()
    #Content Parsing
    elif menu == '1':
        urlMin = 3
        urlMax = 7
        urlStart = 1
        parsingMin = int(input(">>> 데이터 파싱간 딜레이 최소값 정수 입력: "))
        parsingMax = int(input(">>> 데이터 파싱간 딜레이 최대값 정수 입력: "))
        get_parsing()
    else:
        urlMin = int(input(">>> URL 파싱간 딜레이 최소값 정수 입력: "))
        urlMax = int(input(">>> URL 파싱간 딜레이 최대값 정수 입력: "))
        urlStart = int(input(">>> URL 파싱 시작 페이지 입력 (기본값 1 ):"))
        parsingMin = int(input(">>> 데이터 파싱간 딜레이 최소값 정수 입력: "))
        parsingMax = int(input(">>> 데이터 파싱간 딜레이 최대값 정수 입력: "))
        get_url()
        get_parsing()
    # ~()
    driver.quit()




