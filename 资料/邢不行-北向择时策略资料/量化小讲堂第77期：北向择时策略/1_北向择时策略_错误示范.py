'''
邢不行 | 量化小讲堂系列
《妙用北向资金找出大盘买点 卖点，跟着操作5年4倍【量化投资邢不行啊】》
https://www.bilibili.com/video/BV1sM4y1M72j
获取更多量化文章，请联系邢不行个人微信：xbx297
'''
from functions import *

# 读取北向资金数据
# 北向资金大于20.41亿看涨，小于2.95亿看跌
df = pd.read_csv('北向资金择时回测_错误.csv', encoding='utf-8-sig', parse_dates=['交易日期'])
# 根据每日涨跌幅计算策略资金曲线
df['策略资金曲线'] = (df['equity_change'] + 1).cumprod()
# 展示一下数据
print(df.head(5))
# 评估策略表现
res = evaluate_investment(df, tittle='策略资金曲线', time_label='交易日期')
# 显示回测结果
print(res)
# 绘制资金曲线
data_dict = {'北向资金择时策略': '策略资金曲线', '沪深300': 'benchmark'}
draw_equity_curve(df, data_dict=data_dict)
