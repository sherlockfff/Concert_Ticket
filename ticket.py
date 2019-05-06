# -*- coding: utf-8 -*-
# autor:Oliver0047
import os
import pickle
import time
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Concert(object):
    def __init__(self, domain_url, ticket_url):
        self.domain_url = domain_url
        self.ticket_url = ticket_url
        self.driver = webdriver.Chrome()  # 默认火狐浏览器
        self.driver.minimize_window()

    def __get_cookie(self):
        self.driver.get(self.domai_url)
        print("###请点击登录###")
        while self.driver.title.find('大麦网-全球演出赛事官方购票平台') != -1:
            sleep(1)
        print("###请扫码登录###")
        while self.driver.title == '中文登录':
            sleep(1)
        print("###扫码成功###")
        pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))
        print("###Cookie保存成功###")

    def __set_cookie(self):
        try:
            cookies = pickle.load(open("cookies.pkl", "rb"))  # 载入cookie
            for cookie in cookies:
                cookie_dict = {
                    'domain': '.damai.cn',  # 必须有，不然就是假登录
                    'name': cookie.get('name'),
                    'value': cookie.get('value'),
                    "expires": "",
                    'path': '/',
                    'httpOnly': False,
                    'HostOnly': False,
                    'Secure': False}
                self.driver.add_cookie(cookie_dict)
            print('###载入Cookie###')
        except Exception as e:
            print(e)

    def login(self):
        if not os.path.exists('cookies.pkl'):  # 如果不存在cookie.pkl,就获取一下
            self.get_cookie()
        else:
            self.driver.get(self.domain_url)
            self.set_cookie()

        self.driver.refresh()

    def choose_ticket(self):

        self.num = 0
        time_start = time.time()

        while True:
            # 尝试次数统计
            self.num = self.num + 1

            # 刷新页面
            self.driver.get(self.ticket_url)

            # 选择场次 票价
            self.driver.find_elements_by_class_name('select_right_list_item')[2].click()
            self.driver.find_elements_by_css_selector('[class="select_right_list_item sku_item"]')[4].click()

            # 尝试下单
            if self.driver.find_element_by_class_name('buybtn').text is not '提交缺货登记':
                self.driver.find_element_by_class_name('buybtn').click()
                self.driver.switch_to_window(self.driver.window_handles[1])
                break

        time_end = time.time()
        print("###经过%d轮奋斗，共耗时%f秒，抢票成功！请确认订单信息###" % (self.num - 1, round(time_end - time_start, 3)))

    def check_order(self):
        if self.status in [3, 4, 5]:
            print('###开始确认订单###')
            print('###默认购票人信息###')
            rn_button = self.driver.find_elements_by_xpath('/html/body/div[3]/div[3]/div[2]/div[2]/div/a')
            if len(rn_button) == 1:  # 如果要求实名制
                print('###选择实名制信息###')
                rn_button[0].click()
                # 选择实名信息
                try:
                    tb = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[3]/div[12]/div')))
                except Exception as e:
                    print("###实名信息选择框没有显示###")
                    print(e)
                lb = tb.find_elements_by_tag_name('label')[self.real_name]  # 选择第self.real_name个实名者
                lb.find_elements_by_tag_name('td')[0].click()
                tb.find_element_by_class_name('one-btn').click()
            print('###默认选择付款方式###')
            print('###确认商品清单###')
            rn_button = self.driver.find_elements_by_xpath(
                '/html/body/div[3]/div[3]/div[3]/div[2]/div[2]/div/div/h2/a[1]')
            if len(rn_button) == 1:  # 如果要求实名制
                print('###选择购票人信息###')
                rn_button[0].click()
                # 选择实名信息
                try:
                    tb = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[3]/div[13]/div')))
                except Exception as e:
                    print("###实名信息选择框没有显示###")
                    print(e)
                lb = tb.find_elements_by_tag_name('label')[self.real_name]  # 选择第self.real_name个实名者
                lb.find_elements_by_tag_name('td')[0].click()
                tb.find_element_by_class_name('one-btn').click()
            print('###不选择订单优惠###')
            print('###请在付款完成后下载大麦APP进入订单详情页申请开具###')
            self.driver.find_element_by_id('orderConfirmSubmit').click()  # 同意以上协议并提交订单
            try:
                element = WebDriverWait(self.driver, 5).until(EC.title_contains('支付'))
                self.status = 6
                print('###成功提交订单,请手动支付###')
            except:
                print('###提交订单失败,请查看问题###')

    def finish(self):
        self.driver.quit()


if __name__ == '__main__':
    try:
        # 大麦网
        domain_url = "https://www.damai.cn/"

        # 买票页面的url，程序会一直刷新页面直到可以购买
        ticket_url = "https://www.damai.cn/"

        con = Concert(domain_url, ticket_url)
        con.login()
        con.choose_ticket()
        con.check_order()

        con.finish()
    except Exception as e:
        print(e)
        con.finish()
