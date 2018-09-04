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




