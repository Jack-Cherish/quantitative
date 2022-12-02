from selenium import webdriver
from selenium.webdriver import ActionChains
from io import BytesIO
import json
import base64
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from PIL import Image
from selenium import webdriver

# 账号
USERNAME = '***'
# 密码
PASSWORD = '***'
BORDER = 6


class Login(object):
    def __init__(self):
        self.url = 'https://xueqiu.com/'

        opt = webdriver.ChromeOptions()
        opt.add_experimental_option('w3c', False)
        self.browser = webdriver.Chrome("chromedriver.exe", chrome_options=opt)
        self.browser.maximize_window()#第一处修复，设置浏览器全屏
        self.username = USERNAME
        self.password = PASSWORD
        self.wait = WebDriverWait(self.browser, 20)

    def __del__(self):
        print("close")

    def open(self):
        self.browser.get(self.url)
        ele = self.browser.find_element_by_xpath('//*[@id="app"]/nav/div[1]/div[2]/div/div')#第二处修复，改xpath
        ele.click()
        username = self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="username"]')))
        pwd = self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="password"]')))
        username.send_keys(self.username)
        time.sleep(2)
        pwd.send_keys(self.password)

    # 获取验证码按钮
    def get_yzm_button(self):
        button = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div/div/div/div[2]/div[2]/div[2]')))#第三处修复，改xpath
        return button

    # 获取验证码图片对象
    def get_img_element(self):
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, '//cavas[@name="geetest_canvas_bg geetest_absolute"]')))
        return element

    def get_position(self):
        # 获取验证码位置
        element = self.get_img_element()
        sleep(2)
        location = element.location
        size = element.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return left, top, right, bottom

    def get_geetest_image(self):
        """
        获取验证码图片
        :return: 图片对象
        """
        '''
        <canvas class="geetest_canvas_bg geetest_absolute" height="160" width="260"></canvas>
        '''
        # 带阴影的图片
        # im = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[2]/div[6]/div/div[1]/div[1]/div/a/div[1]/div/canvas[1]')))
        im = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.geetest_canvas_bg')))
        time.sleep(2)
        im.screenshot('captcha.png')
        # 执行 JS 代码并拿到图片 base64 数据
        JS = 'return document.getElementsByClassName("geetest_canvas_fullbg")[0].toDataURL("image/png");'  # 不带阴影的完整图片
        im_info = self.browser.execute_script(JS)  # 执行js文件得到带图片信息的图片数据
        # 拿到base64编码的图片信息
        im_base64 = im_info.split(',')[1]
        # 转为bytes类型
        captcha1 = base64.b64decode(im_base64)
        # 将图片保存在本地
        with open('captcha1.png', 'wb') as f:
            f.write(captcha1)

        JS = 'return document.getElementsByClassName("geetest_canvas_bg")[0].toDataURL("image/png");'
        # 执行 JS 代码并拿到图片 base64 数据ng  # 带阴影的图片
        im_info = self.browser.execute_script(JS)  # 执行js文件得到带图片信息的图片数据
        # 拿到base64编码的图片信息
        im_base64 = im_info.split(',')[1]
        # 转为bytes类型
        captcha2 = base64.b64decode(im_base64)
        # 将图片保存在本地
        with open('captcha2.png', 'wb') as f:
            f.write(captcha2)

        captcha1 = Image.open('captcha1.png')
        captcha2 = Image.open('captcha2.png')
        return captcha1, captcha2

    # 获取网页截图
    def get_screen_shot(self):
        screen_shot = self.browser.get_screenshot_as_png()
        screen_shot = Image.open(BytesIO(screen_shot))
        return screen_shot

    def get_yzm_img(self, name='captcha.png'):
        #  获取验证码图片
        left, top, right, bottom = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screen_shot = self.get_screen_shot()
        captcha = screen_shot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def get_slider(self):
        # 获取滑块
        # :return: 滑块对象
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_track')))
        return slider

    def get_gap(self, image1, image2):
        """
        获取缺口偏移量
        :param image1: 不带缺口图片
        :param image2: 带缺口图片
        :return:
        """
        left = 62
        for i in range(left, image1.size[0]):
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    left = i
                    return left
        # return left

    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 60
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 初速度
        v = 0
        # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
        t = 0.3
        # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
        tracks = []
        # 当前的位移
        current = 5
        # 到达mid值开始减速
        mid = distance * 3 / 5
        while current < distance:
            if current < mid:
                # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
                a = 2
            else:
                a = -3
            # 初速度
            v0 = v
            # 0.2秒时间内的位移
            s = v0 * t + 0.4 * a * (t ** 2)
            # 当前的位置
            current += s
            # 添加到轨迹列表
            tracks.append(round(s))
            # 速度已经达到v,该速度作为下次的初速度
            v = v0 + a * t
        return tracks

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.browser).click_and_hold(slider).perform()
        for x in track:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()

    def shake_mouse(self):
        """
        模拟人手释放鼠标抖动
        :return: None
        """
        ActionChains(self.browser).move_by_offset(xoffset=-2, yoffset=0).perform()
        ActionChains(self.browser).move_by_offset(xoffset=2, yoffset=0).perform()

    def operate_slider(self, track):
        '''
        拖动滑块
        '''
        # 获取拖动按钮
        back_tracks = [-1,-1, -1, -1]
        slider_bt = self.browser.find_element_by_xpath('//div[@class="geetest_slider_button"]')

        # 点击拖动验证码的按钮不放
        ActionChains(self.browser).click_and_hold(slider_bt).perform()

        # 按正向轨迹移动
        for i in track:
            ActionChains(self.browser).move_by_offset(xoffset=i, yoffset=0).perform()

        time.sleep(1)
        ActionChains(self.browser).release().perform()

    def get_cookies(self):
        try:
            cookie_list = self.browser.get_cookies()
            cookie_dict = {i['name']: i['value'] for i in cookie_list}
            with open('xueqiu_cookies', 'w', encoding='utf8')as f:
                cookie_dict = json.dumps(cookie_dict)
                f.write(cookie_dict)

            return cookie_dict
        except:
            print("cookie 获取失败")
            return None

    # 读取cookie
    def return_cookie(self):
        cookies = ''
        with open('xueqiu_cookies', 'r')as f:
            cookie = f.read()[1:-1]
            cookie = cookie.split(', ')
            for i in cookie:
                cook = i.split(': ')
                cookies += cook[0][1:-1] + '=' + cook[1][1:-1] + ';'
            return cookies

    def run(self):
        # 破解入口
        self.open(), sleep(3)
        self.get_yzm_button().click(), sleep(2)# 点击验证按钮
        # 点按呼出缺口
        slider = self.get_slider()
        # slider.click()
        # 获取带缺口的验证码图片
        image1, image2 = self.get_geetest_image()
        gap = self.get_gap(image1, image2)
        print('缺口位置', gap)
        track = self.get_track(gap)
        print('滑动轨迹', track)
        self.operate_slider(track)
        # 判定是否成功
        time.sleep(8)
        try:
            elem = self.wait.until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, 'nav__btn--longtext'), '发帖'))
            if elem:
                cookie = self.get_cookies()
            else:
                print("get cookies errors")
        except Exception as e:
            print(e, 'fail! ')
            time.sleep(3)
            self.run()
        finally:
            self.browser.quit()


if __name__ == '__main__':
    crack = Login()
    crack.run()
