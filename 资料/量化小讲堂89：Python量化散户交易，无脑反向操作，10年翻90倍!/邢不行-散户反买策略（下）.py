'''
本代码由邢不行制作提供，
如需获取视频中数据和代码，
可联系邢不行个人微信：xbx719
'''

import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
pd.set_option('display.max_rows', 5000)  # 最多显示数据的行数

# 读取文件
equity = pd.read_csv(r'回测结果_event_资金流_1_3_3_3.csv', encoding='gbk', parse_dates=['交易日期'])
equity.set_index(['交易日期'], inplace=True)

# print(equity) #可使用print功能观察数据

# 画图
equity[['净值', '基准净值']].plot(figsize=(16, 9), grid=False, fontsize=20)
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.savefig(r'散户反买策略.png')
plt.show()
