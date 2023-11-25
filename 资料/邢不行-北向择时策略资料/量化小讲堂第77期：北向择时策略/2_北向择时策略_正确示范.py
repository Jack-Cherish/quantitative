'''
邢不行 | 量化小讲堂系列
《妙用北向资金找出大盘买点 卖点，跟着操作5年4倍【量化投资邢不行啊】》
https://www.bilibili.com/video/BV1sM4y1M72j
获取更多量化文章，请联系邢不行个人微信：xbx297
'''
from functions import *

# 读取错误的北向资金数据
# 北向资金大于20.41亿看涨，小于2.95亿看跌
error_df = pd.read_csv('北向资金择时回测_错误.csv', encoding='utf-8-sig', parse_dates=['交易日期'])
# 根据每日涨跌幅计算策略资金曲线
error_df['错误策略资金曲线'] = (error_df['equity_change'] + 1).cumprod()

# 读取正确的北向资金数据
correct_df = pd.read_csv('北向资金择时回测_正确.csv', encoding='utf-8-sig', parse_dates=['交易日期'])
# 根据每日涨跌幅计算策略资金曲线
correct_df['正确策略资金曲线'] = (correct_df['equity_change'] + 1).cumprod()

# 展示一下数据
print(correct_df.head(3))
# 评估正确策略表现
res = evaluate_investment(correct_df, tittle='正确策略资金曲线', time_label='交易日期')
# 显示回测结果
print('\n===============正确结果展示===============')
print(res)
# 评估错误策略表现
res = evaluate_investment(error_df, tittle='错误策略资金曲线', time_label='交易日期')
# 显示回测结果
print('\n===============错误结果展示===============')
print(res)
# 合并正确数据和错误数据，并在同一张图上绘制资金曲线
df = pd.merge(left=correct_df, right=error_df[['交易日期', '错误策略资金曲线']], on=['交易日期'], how='left')

draw_equity_curve(df, data_dict={'北向择时_错误': '错误策略资金曲线', '北向择时_正确': '正确策略资金曲线', '沪深300': 'benchmark'})
