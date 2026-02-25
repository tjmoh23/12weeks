from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from selenium.common.exceptions import NoSuchElementException
import time
import re

import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st

# 한글 폰트 설정
plt.rc('font', family = 'AppleGothic')

# 데이터 로드
@st.cache_data

# 사람인 크롤링
def saramin():
    # Selenium으로 웹 드라이버 실행
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    url ='https://www.saramin.co.kr/zf_user/'
    driver.get(url)
    driver.implicitly_wait(0.5) # 응답 바로 읽지 않고 기다려주기

    # 검색어 버튼 클릭 1
    search_click = driver.find_elements(By.CLASS_NAME, 'btn_search')
    search_click[0].click()
    time.sleep(2)

    # 검색어 입력
    search_input = driver.find_element(By.ID, 'ipt_keyword_recruit')
    search_input.send_keys('데이터 분석') 
    time.sleep(2)

    # 검색어 버튼 클릭 2
    search_click[1].click()
    time.sleep(2)

    recruit = []
    url = []
    company = []
    detail = []

    # 전체정보
    search_info = driver.find_elements(By.CSS_SELECTOR, "[class*='item_recruit']")

    for i in range(len(search_info)):
        title_link = search_info[i].find_element(By.CLASS_NAME, 'job_tit') # 제목과 링크
        Col_recruit = title_link.text # 제목
        Col_url = title_link.find_element(By.TAG_NAME, 'a').get_attribute('href') # 링크
        Col_company = search_info[i].find_element(By.CLASS_NAME, 'corp_name').text # 회사명
        Col_detail = search_info[i].find_element(By.CLASS_NAME, 'job_condition').text.split('\n') # 세부조건

        recruit.append(Col_recruit)
        url.append(Col_url)
        company.append(Col_company)
        detail.append(Col_detail)

    df_saramin = pd.DataFrame({'Site':'Saramin', 'Col_company':company, 'Col_recruit':recruit, 'Col_detail':detail, 'Col_url':url})
    
    driver.quit()   

    # 사람인 데이터 저장
    # df_saramin.to_csv('data_tmp/data_saramin.csv', index=False, encoding='utf-8-sig')
    return df_saramin


# 잡코리아 크롤링
def jobkorea():
    # Selenium으로 웹 드라이버 실행
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    url ='https://www.jobkorea.co.kr/'
    driver.get(url)
    driver.implicitly_wait(2) # 응답 바로 읽지 않고 기다려주기

    # 팝업 닫기 시도
    try:
        popup = driver.find_element(By.CLASS_NAME, 'Modal_overlay__1qbupvq0')
        close_btn = popup.find_element(By.XPATH, './/button/i')
        close_btn.click()
        time.sleep(1)
        print("팝업 닫음")

    except NoSuchElementException:
        print("팝업 없음, 바로 진행")
        
    # search_input = driver.find_element(By.CLASS_NAME, 'Modal_overlay__1qbupvq0')
    # search_input1 = search_input.find_element(By.XPATH, '//*[@id="jk-_r_0_"]/button/i')
    # search_input1.click()
    # time.sleep(2)

    # 검색어 입력
    search_input = driver.find_element(By.ID, 'radix-_R_kl6anmlbH2_')
    search_input.send_keys('데이터 분석') 
    time.sleep(2)

    # 검색 버튼 클릭
    search_click = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div/div/div[1]/div[1]/div/div[2]/div/div/div/div[1]/div[2]/button[2]')
    search_click.click()
    time.sleep(2)

    # 전체 내용
    search = driver.find_element(By.CSS_SELECTOR, "#jk-_R_olfaknqdb_-content-recruit > div > div:nth-child(2) > div.Flex_display_flex__i0l0hl2.Flex_gap_space16__i0l0hlj.Flex_direction_column__i0l0hl4")
    search_info = search.find_elements(By.CLASS_NAME, 'Box_bgColor_white__1wwr54u0.Box_borderColor_default__1wwr54u5.Box_borderSize_1__1wwr54ud.styles_p_space0__dk46ts61.styles_radius_radius16__dk46ts9d.Shadow_root_list__bm2zcc6.dlua7o0')

    recruit = []
    url = []
    company = []
    detail_list = []

    for i in range(len(search_info)):
        title_link = search_info[i].find_element(By.CLASS_NAME, 'styles_mb_space2__dk46ts4t') # 제목과 링크
        title = title_link.text # 제목
        link = title_link.find_element(By.TAG_NAME, 'a').get_attribute('href') # 링크
        cop_nm = search_info[i].find_element(By.CLASS_NAME, 'Typography_variant_size16__344nw26.Typography_weight_regular__344nw2e.Typography_color_gray700__344nw2o.Typography_truncate__344nw2y').text # 회사명
        detail = search_info[i].find_element(By.CLASS_NAME, 'Flex_display_flex__i0l0hl2.Flex_gap_space10__i0l0hlm.Flex_direction_column__i0l0hl4').text.split('\n')
        detail_final = [x for x in detail if re.search(r"[가-힣a-zA-Z0-9]", x)] # 특수문자만 있을 경우 제외
        

        recruit.append(title) # 제목
        url.append(link)
        company.append(cop_nm)
        detail_list.append(detail_final)

    df_jobkorea = pd.DataFrame({'Site':'Job_Korea', 'Col_company':company, 'Col_recruit':recruit, 'Col_detail':detail_list, 'Col_url':url})

    driver.quit()

    # 잡코리아 데이터 저장
    # df_jobkorea.to_csv('data_tmp/df_jobkorea.csv', index=False, encoding='utf-8-sig')
    return df_jobkorea


# Streamlit 나가려면 ctrl + C

if __name__ == "__main__":
    st.header('Title')

    with st.form('recruit', clear_on_submit = True):
        submitted1 = st.form_submit_button('Recruit Searching')
        if submitted1:
            df_saramin = saramin() # 함수 실행 해줘야 함
            df_jobkorea = jobkorea()

            # 두 사이트 병합
            df_total = pd.concat([df_saramin, df_jobkorea]).reset_index(drop=True)

            # 비율
            df_fin = df_total.groupby('Site')[['Col_url']].count().reset_index(drop=False)
            df_fin['sum'] = df_fin['Col_url'].sum()
            df_fin['Ratio'] = round(df_fin['Col_url']/df_fin['sum']*100, 2)
            df_fin = df_fin.drop(['sum'], axis=1)
            df_fin.columns = ['Site', 'Count', 'Ratio']
            
            # 그래프
            pie = px.pie(df_fin,  names='Site', values='Ratio', title='Recruiment Ratio')

            st.dataframe(df_total, use_container_width=False)
            st.dataframe(df_fin, use_container_width=False)
            st.plotly_chart(pie, use_container_width=False)
            


# 실행 시 터미널에서 가상환경 키고 해야 함
# streamlit run 'Code_streamlit.py'