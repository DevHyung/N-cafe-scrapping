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

def get_board_dict():
    """
    target = [24,25,26,27,29,30,31,33,37]
    :return:
    """
    boardDict = {} # for return
    bs4 = get_bs_by_txt('html.txt')
    uls = bs4.find_all('ul', class_='cafe-menu-list')
    idx = 1
    for ul in uls:
        lis = ul.find_all('li')
        for li in lis:
            if idx in [24,25,26,27,29,30,31,33,37]:
                print("{}:{}".format(idx,li.a.get_text().strip()))
                boardDict[idx] = 'https://cafe.naver.com/imsanbu/' + li.a['href']
            idx +=1
    return boardDict
if __name__ == '__main__':
    boardDict = get_board_dict()
    print(boardDict)
    # 이다음부턴 검색기능 잘되있던데
    # 검색은 사람이 하게 하고 다되면
    # 그이후만 사람이 하는건어떠냐 
    exit(-1)
    driver = webdriver.Chrome('./chromedriver')
    driver.get('https://cafe.naver.com/imsanbu')


    time.sleep(5)
    driver.quit()
