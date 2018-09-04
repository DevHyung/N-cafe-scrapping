'''
네이버카페 웹 크롤링 프로그램을 개발하고자 문의드립니다.
1. 맘스홀릭베이비(https://cafe.naver.com/imsanbu)카페에서
    특정 게시판
    (임신준비 질문방,
    테스터/초음파 질문방,
    임신 중 질문방,
    난임/인공/시험관 질문방,
    분만 질문방,
    산후조리 질문방,
    산후다이어트 질문방,
    수유 질문방,
    육아 질문방)을
    선택해서 지정하는 기간 동안에 해당하는 데이터를 긁어오고 싶습니다.
    현재는 긁어오고자 하는 게시판이 정해져 있는데 상황에 따라 다른 게시판을 크롤링해야 할 수도 있습니다.
2. 게시판 별로 글번호/작성자/작성일/제목/글내용/댓글1~5(갯수에 따라 셀이 늘어남(댓글작성일 및 작성자 정보는 필요없고 내용만)의
    정보를xlsx파일로 저장하고 싶습니다. 그런데 걱정이 되는 것은 게시판 별로 저장은 하겠지만,
    1년치 데이터를 하나의 엑셀파일에 저장하면 나중에 너무 무거워져서 컨트롤하기 어려워지지 않을까 하는 것입니다.
    그래서 월별로 나눠서 데이터를 저장하고 싶은데 혹시 그런 기능도 구현이 되는지 궁금합니다.
3. 1년치 데이터를 크롤링하고 싶은데 하루에 글이 꽤 많이 올라오는 편이라
    긁고자 하는 페이지 범위를 설정하는 방법이 최선인지 문의드리고 싶네요.

4. 1년치 데이터를 크롤링하는 동안 아이디가 막히지 않도록 처리를 해주셨으면 합니다.
'''
# 요약하면 게시판 별로 저장을 하되, 월별로 저장하고 싶다.
# 근데 그중에 페이지 설정도 하고싶고
# 작성일 기준으로 엑셀파일 제목을정하고
# 그아래 또 게시판별 엑셀을 따로 저장해야겠군
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
    pageIdx = 1
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

def valid_user():
    # 20180815 20:03기준 4시간
    print(time.time())
    now = 1536034504.2608087
    terminTime = now + 60 * 60 * 12
    print("체험판 만료기간 : ", time.ctime(terminTime))
    if time.time() > terminTime:
        print('만료되었습니다.')
        exit(-1)
    else:
        print(">>> 프로그램이 실행되었습니다.")

if __name__ == '__main__':
    valid_user()
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
        parsingMin = 3
        parsingMax = 7
        get_url()
    #Content Parsing
    elif menu == '1':
        urlMin = 3
        urlMax = 7
        parsingMin = int(input(">>> 데이터 파싱간 딜레이 최소값 정수 입력: "))
        parsingMax = int(input(">>> 데이터 파싱간 딜레이 최대값 정수 입력: "))
        get_parsing()
    else:
        urlMin = int(input(">>> URL 파싱간 딜레이 최소값 정수 입력: "))
        urlMax = int(input(">>> URL 파싱간 딜레이 최대값 정수 입력: "))
        parsingMin = int(input(">>> 데이터 파싱간 딜레이 최소값 정수 입력: "))
        parsingMax = int(input(">>> 데이터 파싱간 딜레이 최대값 정수 입력: "))
        get_url()
        get_parsing()
    # ~()
    driver.quit()




