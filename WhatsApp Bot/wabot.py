from bs4 import BeautifulSoup as bs
from connection import Connection
from datetime import datetime
import json
import os
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


class WABot:
    def __init__(self):
        self.con = Connection()
        self.log_file = 'logs.csv'

        options = Options()
        options.add_argument('--disable-notifications')
        options.add_argument('--start-maximized')
        options.add_argument("--user-data-dir=chrome-data")
        #options.add_argument('--headless')

        self.driver = webdriver.Chrome('./chromedriver', options=options)


    def login(self):
        url = 'https://web.whatsapp.com'

        #open whatsapp
        self.driver.get(url)

        #delay for scanning QR code
        WebDriverWait(self.driver, 60).until(lambda x: x.find_element_by_css_selector('div._1MZWu'))


    def get_message(self):
        return 'Hello ,\nWelcome to *APEX ROAD CARRIER*\n\n*For LR STATUS* \n\nType the details in the following pattern and search your LR No details\n\nFormat\n*LR No* <space> *Bale No*\n\n---------------\n*[SAMPLE] *\n*1234567 12354*\n---------------\n\nand type *Account* for your account status'


    def check_message(self, message, contact):
        regex = re.compile('^\d+ \d+$')

        if regex.match(message):
            lr, bale = map(int, message.split(' '))
            return self.con.get_data(lr, bale, contact)
        elif message == 'Account':
            return self.con.get_account_status(contact)
        else:
            return self.get_message()


    def send_message(self, message, contact):
        #link = "https://web.whatsapp.com/send?phone={}&text={}".format(contact.replace(' ', '').replace('+', ''), message.replace('\n', '%0A'))

        WebDriverWait(self.driver,30).until(lambda x: x.find_elements_by_css_selector('div[contenteditable="true"]')[1]).click()
        for line in message.split('\n'):
            ActionChains(self.driver).send_keys(line).perform()
            ActionChains(self.driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()
        ActionChains(self.driver).send_keys(Keys.RETURN).perform()


    def get_data(self):
        for x in range(len(self.driver.find_elements_by_css_selector('div._1MZWu'))):
            self.driver.find_elements_by_css_selector('div._1MZWu')[x].click()
            try:
                contact = self.driver.find_elements_by_css_selector('div._1MZWu')[x].find_element_by_css_selector('span._1hI5g._1XH7x._1VzZY').get_attribute('title')
            except:
                print('Contact is not valid')
                continue

            try:
                WebDriverWait(self.driver, 30).until(lambda x: x.find_element_by_css_selector('div._1RAno.message-in.focusable-list-item'))
                page = bs(self.driver.page_source, 'lxml')
            except:
                print('Incoming message not found')
                continue

            try:
                last_in = page.find_all('div', {'class': '_1RAno message-in focusable-list-item'})[-1].find('span', {'class': '_1VzZY selectable-text invisible-space copyable-text'})
                last_ov = page.find_all('span', {'class': '_1VzZY selectable-text invisible-space copyable-text'})[-1]
            except:
                print('Last message is invalid')

            if last_in == last_ov:
                message = last_in.text
                output = self.check_message(message, contact)
                self.send_message(output, contact)
                self.save_log(message, output, contact)


    def save_log(self, in_msg, out_msg, contact):
        data = pd.DataFrame(columns=['Timestamp', 'Message In', 'Message Out', 'Contact'])
        data.loc[0] = [datetime.now(), in_msg, out_msg, contact]
        
        if os.path.exists(self.log_file):
            pd.concat([pd.read_csv(self.log_file, low_memory=False), data]).to_csv(self.log_file, index=None)
        else:
            data.to_csv(self.log_file, index=None)


def main():
    wabot = WABot()

    #whatsapp login
    wabot.login()

    #whatsapp data
    while True:
        wabot.get_data()
        
    return

if __name__ == '__main__':
    main()