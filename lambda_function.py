#!/usr/bin/env python
#coding:UTF-8


import time # for sleep
import os   # for path


from selenium import webdriver
from selenium.webdriver.support.events import EventFiringWebDriver
from selenium.webdriver.support.events import AbstractEventListener


from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import boto3

from bs4 import BeautifulSoup
import json

class ScreenshotListener(AbstractEventListener):
    def on_exception(self, exception, driver):
        screenshot_name = "00_exception.png"
        #driver.get_screenshot_as_file(screenshot_name)
        print("Screenshot saved as '%s'" % screenshot_name)

class S3accessor:
    def __init__(self):
        self.BUCKET_NAME = 'click-scraper-temp01'
        self.SCREENSHOT_DIR = "screenshots"
        self.TEXT_DIR = "logs"
        self.JSON_DIR = "json"
        self.s3 = boto3.resource('s3')
        self.bucket = self.s3.Bucket(self.BUCKET_NAME)

    def save_text(self, filename, text):
        ret = self.bucket.put_object(ACL='public-read', Body=text, Key=self.TEXT_DIR + "/" + filename, ContentType='text/html')

    def save_screenshot(self, filename, binary):
        ret = self.bucket.put_object(ACL='public-read', Body=binary, Key=self.SCREENSHOT_DIR + "/" + filename, ContentType='image/png')

    def save_json(self, filename, json_str):
        ret = self.bucket.put_object(ACL='public-read', Body=json_str, Key=self.JSON_DIR + "/" + filename, ContentType='application/json')


def lambda_handler(event, context):
    USERNAME = os.environ['USERNAME']
    PASSWORD  = os.environ['PASSWORD']

    #not used anymore
    BUCKET_NAME = 'click-scraper-temp01'
    TARGET_DIR = "screenshots"
    FILENAME = "shot.png"

    s3 = S3accessor()

    user_agent = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36")

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = user_agent
    dcap["phantomjs.page.settings.javascriptEnabled"] = True

    _driver = webdriver.PhantomJS(service_log_path=os.path.devnull, executable_path="/var/task/phantomjs", service_args=['--ignore-ssl-errors=true'], desired_capabilities=dcap)
    driver = EventFiringWebDriver(_driver, ScreenshotListener())

    print('drive start')
    driver.get('https://sec-sso.click-sec.com/loginweb/sso-redirect')

    uid_box = driver.find_element_by_name('j_username')
    pass_box = driver.find_element_by_name('j_password')
    uid_box.send_keys(USERNAME)
    pass_box.send_keys(PASSWORD)

    #driver.save_screenshot('0before login.png')
    print("saved before login")

    #login
    driver.find_element_by_name('LoginForm').click()
    driver.implicitly_wait(5)

    #driver.save_screenshot('1after login.png')
    print("saved after login")

    driver.find_element_by_id('mypageMenu').click()
    driver.find_element_by_link_text(u"トップページ").click()
    #driver.get('https://kabu.click-sec.com/sec1-8/mypage/top.do') #was 1-5 before

    driver.implicitly_wait(5)
    #driver.save_screenshot('2after mypage.png')
    print( "saved after mypage")

    #driver.find_element_by_id('marketSummaryTab_2').send_keys(Keys.RETURN)
    driver.execute_script('marketSummary.showList(2)')
    driver.execute_script('marketSummary.reload()')

    driver.implicitly_wait(5)
    print( "saved after kaigai")

    png = driver.get_screenshot_as_png()
    print("png length %d" % ( len(png) ) )

    s3.save_screenshot("03 after kaigai.png", png)
    s3.save_text("03 after kaigai.html", driver.page_source)

    #print("s3 returned: " + ret)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    table = soup.find('table', {'class': 'blue_line'})
    rows = table.find_all()
    lists = []
    for row in rows:
        lst = []
        cols = row.find_all(['td','th'])
        cols = [ele.text.strip() for ele in cols]
        lst.append([ele for ele in cols if ele])
        lists.append(lst)

    print(lists)

    #out = open('out.json', 'w')
    #json.dump(lists, out, indent=4)
    #out.close()
    
    json_str = json.dumps(lists)

    s3.save_json('out.json', json_str)
