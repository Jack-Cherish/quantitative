from datetime import datetime
from enum import Enum
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import pandas as pd
import StockConstant
import threading
import time
from DataPuller import DataPuller


class AbstractStockMonitor():
    SEND = 1
    UN_SEND = 0

    dataPuller = DataPuller()

    class Signal(Enum):
        SELL = 1
        BUY = 0

    def __init__(self):
        self.monitor_thread = None
        self.is_running = False
        self.test_mode = False

        '''
        线程监控的上一轮检测的时间，用来判断日期是否跨天，跨天则重置发送信号
        '''
        self.last_datetime = datetime.today()

        '''
        发送信号状态，1表示已经发送，0表示未发送，初始状态表示买入和买出信号都没发送过
        '''
        self.send_signal_status = {self.Signal['SELL']: self.UN_SEND, self.Signal['BUY']: self.UN_SEND}
        pass

    def reset_signal_status(self):
        self.send_signal_status = {self.Signal['SELL']: self.UN_SEND, self.Signal['BUY']: self.UN_SEND}

    def get_monitor_stock_real_time(self):
        raise NotImplementedError("Please implement way to get monitor stock")

    def start(self, test_mode=False):
        print("Start monitor thread......")

        self.test_mode = test_mode
        # 测试代码，用线程跑无法报错，所以直接运行
        self.is_running = True
        self.check_sell_or_buy()
        return

    def stop(self):
        if self.monitor_thread is not None:
            self.is_running = False
        return

    def check_sell_or_buy(self):
        maxUpperRate = 1
        minDownRate = -1

        print("check sell or buy is running...")
        print(self.is_running)
        while self.is_running:
            if not self.is_on_open_time() and not self.test_mode:
                time.sleep(1)
                continue

            monitor_stock = self.get_monitor_stock_real_time()
            monitor_stock_rate = monitor_stock[StockConstant.COL_CHANGE_RATE].values[0]
            sh_index_rate = self.get_sh_index_rate()
            print('监控股票价格变动', monitor_stock_rate)
            print('大盘指数', sh_index_rate)

            if self.test_mode:
                maxUpperRate = float('-inf')
                minDownRate = float('inf')

            if monitor_stock_rate - sh_index_rate >= maxUpperRate:
                self.push_signal(self.Signal['SELL'])
            if monitor_stock_rate - sh_index_rate <= minDownRate:
                self.push_signal(self.Signal['BUY'])

    def push_signal(self, send_signal):
        if self.send_signal_status[send_signal] == self.SEND:
            return
        self.send_message(send_signal)
        self.send_signal_status[send_signal] = self.SEND
        return

    def send_message(self, signal):
        # qq邮箱smtp服务器
        host_server = 'smtp.qq.com'
        # sender_qq为发件人的qq号码
        sender_qq = '957832064'
        # pwd为qq邮箱的授权码
        pwd = 'sstjhvxllpdwbcbg'
        # 发件人的邮箱
        sender_qq_mail = '957832064@qq.com'
        # 收件人邮箱
        receiver = '957832064@qq.com'
        # 邮件的正文内容
        if signal == self.Signal.SELL: info = "股价涨幅过大"
        if signal == self.Signal.BUY: info = "股价跌幅过大"

        stock_data = self.get_monitor_stock_real_time()
        stock_info = {col: stock_data[col].values[0] for col in stock_data.columns}
        mail_content = f'''
            {info}, {signal.name}信号, 监控股票信息  {stock_info}
            
            1.迅速完成交易，挂当前价格，不要看盘。避免受到影响导致自己精神状态不佳
            2.不做其他操作，只根据策略进行操作。其他操作是另外的策略，而且会使得自己散失主动权
            3.不用让自己的心境因此而发生变化，生活中有更有意义的事情
            
            Attention：你真棒！又一次遵循了策略！
            '''
        # 邮件标题
        mail_title = f'正态分布股价监控策略({signal.name})'

        # 设置邮件内容
        # MIMEMultipart类可以放任何内容
        msg = MIMEMultipart()
        # 把内容加进去
        msg.attach(MIMEText(mail_content, 'plain', 'utf-8'))
        # ssl登录
        smtp = SMTP_SSL(host_server)
        # set_debuglevel()是用来调试的。参数值为1表示开启调试模式，参数值为0关闭调试模式
        smtp.set_debuglevel(1)
        smtp.ehlo(host_server)
        smtp.login(sender_qq, pwd)

        msg["Subject"] = Header(mail_title, 'utf-8')
        msg["From"] = sender_qq_mail
        msg["To"] = receiver

        smtp.sendmail(sender_qq_mail, receiver, msg.as_string())
        smtp.quit()
        return

    def get_sh_index_rate(self):
        data = self.dataPuller.pullIndexData()
        sh_index_data = data[data[StockConstant.COL_CODE] == StockConstant.SH_INDEX_CODE]
        sh_index_change_rate = sh_index_data[StockConstant.COL_CHANGE_RATE].values[0]
        print(sh_index_change_rate)
        return sh_index_change_rate

    def is_on_open_time(self):
        cur_datetime = datetime.today()
        if cur_datetime.day != self.last_datetime.day:
            self.reset_signal_status()

        forenoon_start = cur_datetime.replace(hour=9, minute=30, second=0)
        forenoon_end = cur_datetime.replace(hour=11, minute=30, second=0)
        afternoon_start = cur_datetime.replace(hour=13, minute=0, second=0)
        afternoon_end = cur_datetime.replace(hour=15, minute=0, second=0)
        if (forenoon_start <= cur_datetime <= forenoon_end) or (afternoon_start <= cur_datetime <= afternoon_end):
            return True
        return False


class EtfMonitor(AbstractStockMonitor):
    def __init__(self):
        super().__init__()
        self.monitorStockCode = StockConstant.GUANGFU_ETF_CODE
        pass

    def get_monitor_stock_real_time(self):
        print('get real time data...')
        fundData = self.dataPuller.pullFundData()
        monitorStockData = fundData[fundData[StockConstant.COL_CODE] == self.monitorStockCode]
        return monitorStockData
