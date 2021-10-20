#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import base64
import datetime
import os
import re
import sys
import requests

from os import remove
from hashlib import md5
from PIL import Image as image
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By as by
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support.expected_conditions import presence_of_element_located as located


def verification(file, codetype):
    params = {
        'user': cjy_username,
        'pass2': md5(cjy_password.encode('utf8')).hexdigest(),
        'softid': cjy_password,
        'codetype': codetype
    }
    headers = {'Connection': 'Keep-Alive',
               'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)'}
    files = {'userfile': ('code.jpg', open(file, 'rb').read())}
    data = requests.post('http://upload.chaojiying.net/Upload/Processing.php',
                         data=params, files=files, headers=headers, proxies={"http": None, "https": None}).json()
    return data['pic_str']


def login(username, psw):
    """
    登录操作
    :param username: 学号、手机号、空值
    :param psw: 学号对应的密码
    :return: None
    """
    driver.get("https://e.kmmu.edu.cn/")
    if len(username) == 9:
        print("登陆方式：学号登陆")
        XPATH = '//*[@id="root"]/span/div[4]/div/div/div[1]/div/div/form/div[5]/button[1]'  # 登录按钮
        element = wait(driver, 10, 0.5).until(located((by.XPATH, XPATH)))
        driver.find_element_by_id('userName').send_keys(username)
        driver.find_element_by_id('password').send_keys(psw)
        XPATH = '//*[@id="root"]/span/div[4]/div/div/div[1]/div/div/form/div[4]/div/div/span/div/div[2]/div/img'
        screen = driver.find_element_by_xpath(XPATH)
        driver.save_screenshot(r'./code.png')
        left = screen.location['x']
        top = screen.location['y']
        right = left + screen.size['width']
        bottom = top + screen.size['height']
        picture = image.open(r'./code.png')
        picture = picture.crop((left, top, right, bottom))
        picture.save(r'./code.png')
        code = verification("./code.png", "6001")
        driver.find_element_by_id('captcha').send_keys(code)
        remove("./code.png")
        element.click()
        wait(driver, 10, 0.5).until(located((by.NAME, '我要评价')))
    elif len(username) == 11:
        print("登陆方式：手机号登录")
        XPATH = '//*[@id="root"]/span/div[4]/div/div/div[3]/span'  # 短信登陆按钮
        wait(driver, 10, 0.5).until(located((by.XPATH, XPATH))).click()
        XPATH = '//*[@id="root"]/span/div[4]/div/div/div[1]/div/div/form/div[4]/div/div/span/button'  # 登录按钮
        element = wait(driver, 10, 0.5).until(located((by.XPATH, XPATH)))
        driver.find_element_by_id('mobile').send_keys(username)
        driver.find_element_by_class_name('index-send-2UVkM').click()
        XPATH = '/html/body/div[5]/div/div[2]/div/div[2]/div/div/div[2]/button'  # 警告窗口按钮
        wait(driver, 10, 0.5).until(located((by.XPATH, XPATH))).click()
        driver.find_element_by_id('smsCode').send_keys(input("输入验证码："))
        element.click()
        wait(driver, 10, 0.5).until(located((by.NAME, '我要评价')))
    elif len(username) == 0:
        print("登陆方式：二维码登录")
        size = driver.get_window_size()
        driver.maximize_window()
        XPATH = '//*[@id="root"]/span/div[4]/div[2]/div/ul/li[2]'  # 二维码登录按钮
        wait(driver, 10, 0.5).until(located((by.XPATH, XPATH))).click()
        # qr(username, r'E:\image.jpg')
        wait(driver, 120, 0.5).until(located((by.NAME, '我要评价')))
        driver.set_window_size(size['width'], size['height'])
        # os.system('taskkill /IM Microsoft.Photos.exe /F')
    else:
        driver.quit()
        print("登陆方式错误，请检查输入的账号是否为学号、手机号码，且是否正确")
        sys.exit()
    driver.get('https://kypk.kmmu.edu.cn/home1')
    XPATH = '//*[@id="app"]/div/div[1]/div[3]/div[2]/div/div[1]/div/i'  # 学生评课按钮
    wait(driver, 10, 0.5).until(located((by.XPATH, XPATH))).click()


def classes(entrance):
    """
    学生评课
    :param entrance: 入口值
    :return: None
    """
    XPATH = f'//*[@id="app"]/div/div[1]/div/div[1]/div/div/div/div[{str(entrance)}]/span'
    wait(driver, 10, 0.5).until(located((by.XPATH, XPATH))).click()
    for _ in range(1, 16):
        for m in range(1, 16):
            try:
                # 评价状态框 xpath
                # //*[@id="app"]/div/div[1]/div/div[2]/div[1]/div/div/div/div[1]/div[3]/span[2]
                # //*[@id="app"]/div/div[1]/div/div[2]/div[1]/div/div/div/div[2]/div[3]/span[2]
                XPATH = f'//*[@id="app"]/div/div[1]/div/div[2]/div[1]/div/div/div/div[{m}]/div[3]/span[2]'
                element = wait(driver, 5, 0.5).until(located((by.XPATH, XPATH)))
                driver.execute_script("arguments[0].scrollIntoView();", element)  # 拖动到可见的元素去
            except TimeoutException:
                return
            if "已完成" in element.text:
                continue
            else:
                sumbit(element, 40)
                print(f"完成第{m}门课程的评价")
            break


def teachers(entrance):
    """
    学生评课
    :param entrance: 入口值
    :return: None
    """
    XPATH = f'//*[@id="app"]/div/div[1]/div/div[1]/div/div/div/div[{str(entrance)}]/span'
    wait(driver, 10, 0.5).until(located((by.XPATH, XPATH))).click()
    for _ in range(1, 26):
        for m in range(1, 26):
            try:
                # 评价状态框 xpath
                # //*[@id="app"]/div/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div[2]/span
                # //*[@id="app"]/div/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[2]/span
                XPATH = f'//*[@id="app"]/div/div[1]/div/div[2]/div[2]/div/div/div/div[{m}]/div[2]/span'
                element = wait(driver, 5, 0.5).until(located((by.XPATH, XPATH)))
                driver.execute_script("arguments[0].scrollIntoView();", element)  # 拖动到可见的元素去
            except TimeoutException:
                return
            if "已完成" in element.text:
                continue
            else:
                sumbit(element, 20)
                print(f"完成第{m}位老师的评价")
            break


def myself(entrance):
    """
    学生自评
    :param entrance: 入口值
    :return: None
    """
    XPATH = f'//*[@id="app"]/div/div[1]/div/div[1]/div/div/div/div[{str(entrance)}]/span'
    wait(driver, 10, 0.5).until(located((by.XPATH, XPATH))).click()
    # 评价状态框 xpath
    # //*[@id="app"]/div/div[1]/div/div[2]/div[3]/div/div/div/div[1]/div[2]/span[2]
    XPATH = '//*[@id="app"]/div/div[1]/div/div[2]/div[3]/div/div/div/div[1]/div[2]/span[2]'
    element = wait(driver, 10, 0.5).until(located((by.XPATH, XPATH)))
    driver.execute_script("arguments[0].scrollIntoView();", element)  # 拖动到可见的元素去
    if "已完成" in element.text:
        return
    else:
        sumbit(element, 25)
        print("完成自我评价")


def roommates(entrance):
    """
    室友互评
    :param entrance: 入口值
    :return: None
    """
    XPATH = f'//*[@id="app"]/div/div[1]/div/div[1]/div/div/div/div[{str(entrance)}]/span'
    wait(driver, 10, 0.5).until(located((by.XPATH, XPATH))).click()
    for _ in range(1, 16):
        for m in range(1, 16):
            try:
                # 评价状态框 xpath
                # //*[@id="app"]/div/div[1]/div/div[2]/div[4]/div/div/div/div[1]/div[3]/span[2]
                # //*[@id="app"]/div/div[1]/div/div[2]/div[4]/div/div/div/div[2]/div[3]/span[2]
                XPATH = f'//*[@id="app"]/div/div[1]/div/div[2]/div[4]/div/div/div/div[{m}]/div[3]/span[2]'
                element = wait(driver, 5, 0.5).until(located((by.XPATH, XPATH)))
                driver.execute_script("arguments[0].scrollIntoView();", element)  # 拖动到可见的元素去
            except TimeoutException:
                return
            if "已完成" in element.text:
                continue
            else:
                sumbit(element, 25)
                print(f"完成第{m}位舍友的评价")
            break


def sumbit(element, num):
    """
    提交操作
    :param element: 点击操作
    :param num: 题目数量
    :return: None
    """
    element.click()
    for n in range(1, int(num) + 1):
        XPATH = f'//*[@id="app"]/div/div[1]/div[2]/div/div[{n}]/div[2]/div[1]/div/i'
        element = wait(driver, 10, 0.5).until(located((by.XPATH, XPATH)))
        driver.execute_script("arguments[0].scrollIntoView();", element)  # 拖动到可见的元素去
        element.click()
    XPATH = '//*[@id="app"]/div/div[1]/div[1]/div/div/div[3]/div[1]/button[2]'  # 提交按钮
    wait(driver, 10, 0.5).until(located((by.XPATH, XPATH))).click()
    XPATH = '/html/body/div[3]/div[3]/button[2]'  # 确定按钮
    wait(driver, 10, 0.5).until(located((by.XPATH, XPATH))).click()


def restart():
    """
    重启操作
    :return: None
    """
    print("重试中……")
    driver.get('https://kypk.kmmu.edu.cn/home1')
    XPATH = '//*[@id="app"]/div/div[1]/div[3]/div[2]/div/div[1]/div/i'  # 学生评课按钮
    wait(driver, 10, 0.5).until(located((by.XPATH, XPATH))).click()


def qr(username, fpath):
    """
    显示图片操作
    :param username: 学号、空值
    :param fpath: 图片文件路径
    :return: None
    """
    if len(username) == 9:
        regex = r'(?<=imgalt="logo"src="data:image/png;base64,)\S+(' \
                r'?="></div></div></div></span></div></div></div><divclass="ant-row"><buttontype="button"class="ant' \
                r'-btnindex-submit-36Dahundefinedflant-btn-primaryant-btn-lg">) '
    elif len(username) == 0:
        regex = r'(?<=imgalt="logo"src="data:image/png;base64,)\S+(' \
                r'?="><divclass="index-qrMask-27FBLindex-qrMaskHide-3p9Fn"><)'  # 二维码登录 
    else:
        return
    html = driver.page_source.replace("\n", "").replace("\r", "").replace("\b", "").replace(" ", "")
    string = re.findall(regex, html)[0]
    with open(fpath, "wb") as f:
        f.write(base64.b64decode(string))
    os.startfile(fpath)


def main(username, psw):
    """
    主程序
    :param username: 学号、手机号、空值
    :param psw: 学号对应的密码
    :return: None
    """
    start = datetime.datetime.now()
    login(username, psw)
    loop = True
    while loop:
        try:
            print("当前任务：学生评课")
            classes(1)
            loop = False
        except TimeoutException:
            restart()
            loop = True
    loop = True
    while loop:
        try:
            print("当前任务：学生评教")
            teachers(2)
            loop = False
        except TimeoutException:
            restart()
            loop = True
    loop = True
    while loop:
        try:
            print("当前任务：学生自评")
            myself(3)
            loop = False
        except TimeoutException:
            restart()
            loop = True
    loop = True
    while loop:
        try:
            print("当前任务：室友互评")
            roommates(4)
            loop = False
        except TimeoutException:
            restart()
            loop = True
    end = datetime.datetime.now()
    print('运行耗时：', end - start)
    driver.quit()


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.headless = False  # True开启无窗口模式
    UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                'Chrome/91.0.4472.124 Safari/537.36 '
    options.add_argument(f'--user-agent="{UserAgent}"')  # 设置请求头的User-Agent
    options.add_argument('--no-sandbox')  # 解决DevToolsActivePort文件不存在报错问题
    options.add_argument('--lang=zh_CN.UTF-8')  # 中文编码
    options.add_argument('--disable-javascript')  # 禁用javascript
    options.add_argument('--disable-java')  # 禁用java
    options.add_argument('–-disable-software-rasterizer')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')  # 禁用GPU硬件加速
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--ignore-certificate-errors')  # 禁用扩展插件并实现窗口最大化
    # options.add_argument('--blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
    driver = webdriver.Chrome(options=options)
    cjy_username = ""
    cjy_password = ""
    cjy_softid = ""
    main("", "")
