import time, re, sys
from tqdm import tqdm
from lxml import etree
from bs4 import BeautifulSoup
from pathlib import Path
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

def tag_cleanup(html):
    html = str(html)
    cleanr = re.compile('<.*?>')
    string = (re.sub(cleanr, '', html))[1:-1]
    string = string.replace('\n', '')
    string = string.replace('\t', '')
    return string

def main():
    url = 'https://myanimelist.net/animelist/Pao_com_Ovo?status=2'

    CUR_DIR = Path(__file__).parent
    PROGRAM = 'chromedriver.exe'
    PATH = CUR_DIR / PROGRAM
    
    OPTIONS = webdriver.ChromeOptions()
    OPTIONS.add_argument('--headless')
    
    try:
        browser = webdriver.Chrome(PATH, options=OPTIONS)
        browser.get(url)
        
    except WebDriverException:
        OPTIONS.binary_location = 'D:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
        OPTIONS.add_experimental_option('excludeSwitches', ['enable-logging'])
        browser = webdriver.Chrome(PATH, options=OPTIONS)
        browser.get(url)
    
    browser.get(url)
    time.sleep(5)
    source = browser.page_source
    browser.close()
    
    soup = BeautifulSoup(source, 'html.parser')
    dom = etree.HTML(str(soup))
    
    all = []
    
    for i in tqdm(range(2, 113)):
        xpathselector = f'//*[@id="list-container"]/div[4]/div/table/tbody[{i}]/tr[1]/td[4]/a[1]'
        #imgxpathselector = f'//*[@id="list-container"]/div[4]/div/table/tbody[{i}]/tr[1]/td[3]/a/img'
        imgxpathselector = f'//*[@id="list-container"]/div[4]/div/table/tbody[{i}]/tr[1]/td[3]/a'
        
        current = dom.xpath(xpathselector)[0].text
        current_img = dom.xpath(imgxpathselector)[0].text
        print(type(current_img), current_img)
        
        if not '(Music)' in current.split():
            string = f"{{id: '{current}'}}"
            all.append(string)
    
    list_str = ', '.join(all)
    
    with open('./picker.html', 'r') as file:
        soup = BeautifulSoup(file, features='lxml')

    html_str = (str(soup)).split('\n')

    found = False
    write_index = 0
    
    for i in range(len(html_str)):
        if html_str[i] == 'var items = [':
            write_index = i + 1
            found = True
            break
        
    if found:
        s = '    ' + list_str
        html_str[write_index] = s
        
    html_final = ('\n'.join(html_str)).encode('utf8')
    
    with open('picker.html', 'wb') as outf:
        outf.truncate(0)
        outf.write(html_final)
    
if __name__ == '__main__':
    main()