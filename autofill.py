import re, sys, html, requests
from tqdm import tqdm
from lxml import etree
from bs4 import BeautifulSoup
from pathlib import Path
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from tkinter import Tk, ttk, messagebox
from tkinter.filedialog import askopenfilename

def GUI():
    window = Tk()
    window.title('Favorite Picker MAL')
    window.resizable(False, False)
    window.eval('tk::PlaceWindow . center')
    
    USER = ''
    
    USER_ENTRY = ttk.Entry(justify = 'center', exportselection = 0)
    USER_LABEL = ttk.Label(text = 'Insert your MAL username:', justify = 'center')
    
    def isClickedFunction():
        nonlocal USER
        
        USER = USER_ENTRY.get()
        
        window.destroy()
        
    BUTTON = ttk.Button(text = 'Generate', command = isClickedFunction)
    
    USER_LABEL.grid(row=0, column=0, pady=10)
    USER_ENTRY.grid(row=1, column=0, padx=25)
    
    BUTTON.grid(row=2, column=0, pady=15)
    
    window.mainloop()
    
    return USER

def tag_cleanup(html):
    html = str(html)
    cleanr = re.compile('<.*?>')
    #return re.sub(cleanr, '', html)
    string = (re.sub(cleanr, '', html))
    string = string.replace('\n', '')
    string = string.replace('\t', '')
    return string

def main():
    user = 'Pao_com_Ovo'
    #user = GUI()
    url_list = f'https://myanimelist.net/animelist/{user}?status=2'
    url_user = f'https://myanimelist.net/profile/{user}'

    CUR_DIR = Path(__file__).parent
    PROGRAM = 'chromedriver.exe'
    PATH = CUR_DIR / PROGRAM
    
    OPTIONS = webdriver.ChromeOptions()
    OPTIONS.add_argument('--headless')
    
    try:
        browser = webdriver.Chrome(PATH, options=OPTIONS)
        
    except WebDriverException:
        BINARY = 'D:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
        # BINARY = askopenfilename()
        OPTIONS.binary_location = BINARY
        OPTIONS.add_experimental_option('excludeSwitches', ['enable-logging'])
        browser = webdriver.Chrome(PATH, options=OPTIONS)
    
    try:
        browser.get(url_user)
        WebDriverWait(browser, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'completed')))
        source = browser.page_source
        soup = BeautifulSoup(source, 'html.parser')
        dom = etree.HTML(str(soup))
        xpathselector = '//*[@id="statistics"]/div[1]/div[1]/div[3]/ul[1]/li[2]/span'
        qty = int(dom.xpath(xpathselector)[0].text)
        
        browser.get(url_list)
        WebDriverWait(browser, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'image')))
        source = browser.page_source
        browser.close()
        
        soup = BeautifulSoup(source, 'html.parser')
        dom = etree.HTML(str(soup))
        
        all = []
        imgs = []
        
        for anime in soup.find_all('tr', class_ = 'list-table-data'):
            image = anime.find_all('img', src=True, class_ = 'hover-info')[0]['src']
            name = anime.find_all('a', href=True, class_ = 'sort')[1]
            s = tag_cleanup(name)
            if s and s[0] != ' ' and (not '(Music)' in s.split()):
                id = re.sub(r'[^A-Za-z0-9 ]+', '', s)
                id = (id.replace(' ', '-')).lower()
                name = html.unescape(s)
                img = f'./img/{id}.webp'
                string = f"{{id: '{id}', name: '{name}', image: '{img}'}}"
                all.append(string)
                
                r = requests.get(image)
                with open(img, 'wb') as f:
                    f.write(r.content)
        
        list_str = ', '.join(all)
        
        with open('picker.html', 'r') as file:
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
    
    except TimeoutException:
        try:
            browser.quit()
        finally:
            root = Tk()
            root.withdraw()
            messagebox.showerror('Timeout', 'MAL took too long to respond, try again.')
            root.destroy()
    
if __name__ == '__main__':
    main()