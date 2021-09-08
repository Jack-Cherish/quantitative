'''
优化说明:
    1.使用修正标准分
        rsrs_score的算法有：
            仅斜率slope，效果一般；
            仅标准分zscore，效果不错；
            修正标准分 = zscore * r2，效果最佳;
            右偏标准分 = 修正标准分 * slope，效果不错。
    2.将原策略的每次持有两只etf改成只买最优的一个，收益显著提高
    3.将每周调仓换成每日调仓，收益显著提高
    4.因为交易etf，所以手续费设为万分之三，印花税设为零，未设置滑点
    5.修改股票池中候选etf，删除银行，红利等收益较弱品种，增加纳指etf以增加不同国家市场间轮动的可能性
    6.根据研报，默认参数介已设定为最优
    7.加入防未来函数
    8.增加择时与选股模块的打印日志，方便观察每笔操作依据
'''

#导入函数库
from jqdata import *
import numpy as np

#初始化函数 
def initialize(context):
    # 设定沪深300作为基准
    set_benchmark('000300.XSHG')
    # 用真实价格交易
    set_option('use_real_price', True)
    # 打开防未来函数
    set_option("avoid_future_data", True)
    # 将滑点设置为0
    set_slippage(FixedSlippage(0.001))
    # 设置交易成本万分之三
    set_order_cost(OrderCost(open_tax=0, close_tax=0, open_commission=0.0003, close_commission=0.0003, close_today_commission=0, min_commission=5),
                   type='fund')
    # 股票类每笔交易时的手续费是：买入时佣金万分之二，卖出时佣金万分之二，无印花税, 每笔交易佣金最低扣5块钱
    # set_order_cost(OrderCost(close_tax=0.000, open_commission=0.0002, close_commission=0.0002, min_commission=5), type='fund')
    # 过滤order中低于error级别的日志
    log.set_level('order', 'error')
    # 初始化各类全局变量
    #股票池
    g.stock_pool = [
        '159915.XSHE', # 易方达创业板ETF
        '510300.XSHG', # 华泰柏瑞沪深300ETF
        '510500.XSHG', # 南方中证500ETF
    ]
    #动量轮动参数
    g.stock_num = 1 #买入评分最高的前stock_num只股票
    g.momentum_day = 29 #最新动量参考最近momentum_day的
    #rsrs择时参数
    g.ref_stock = '000300.XSHG' #用ref_stock做择时计算的基础数据
    g.N = 18 # 计算最新斜率slope，拟合度r2参考最近N天
    g.M = 600 # 计算最新标准分zscore，rsrs_score参考最近M天
    g.score_threshold = 0.7 # rsrs标准分指标阈值
    #ma择时参数
    g.mean_day = 20 #计算结束ma收盘价，参考最近mean_day
    g.mean_diff_day = 3 #计算初始ma收盘价，参考(mean_day + mean_diff_day)天前，窗口为mean_diff_day的一段时间
    g.slope_series = initial_slope_series()[:-1] # 除去回测第一天的slope，避免运行时重复加入
    # 设置交易时间，每天运行
    run_daily(my_trade, time='11:30', reference_security='000300.XSHG')
    run_daily(check_lose, time='open', reference_security='000300.XSHG')
    run_daily(print_trade_info, time='15:30', reference_security='000300.XSHG')


#1-1 选股模块-动量因子轮动 
#基于股票年化收益和判定系数打分,并按照分数从大到小排名
def get_rank(stock_pool):
    score_list = []
    for stock in g.stock_pool:
        data = attribute_history(stock, g.momentum_day, '1d', ['close'])
        y = data['log'] = np.log(data.close)
        x = data['num'] = np.arange(data.log.size)
        slope, intercept = np.polyfit(x, y, 1)
        annualized_returns = math.pow(math.exp(slope), 250) - 1
        r_squared = 1 - (sum((y - (slope * x + intercept))**2) / ((len(y) - 1) * np.var(y, ddof=1)))
        score = annualized_returns * r_squared
        score_list.append(score)
    stock_dict=dict(zip(g.stock_pool, score_list))
    sort_list=sorted(stock_dict.items(), key=lambda item:item[1], reverse=True) #True为降序
    code_list=[]
    for i in range((len(g.stock_pool))):
        code_list.append(sort_list[i][0])
    rank_stock = code_list[0:g.stock_num]
    print(code_list[0:5])
    return rank_stock



#2-1 择时模块-计算线性回归统计值
#对输入的自变量每日最低价x(series)和因变量每日最高价y(series)建立OLS回归模型,返回元组(截距,斜率,拟合度)
def get_ols(x, y):
    slope, intercept = np.polyfit(x, y, 1)
    r2 = 1 - (sum((y - (slope * x + intercept))**2) / ((len(y) - 1) * np.var(y, ddof=1)))
    return (intercept, slope, r2)

#2-2 择时模块-设定初始斜率序列
#通过前M日最高最低价的线性回归计算初始的斜率,返回斜率的列表
def initial_slope_series():
    data = attribute_history(g.ref_stock, g.N + g.M, '1d', ['high', 'low'])
    return [get_ols(data.low[i:i+g.N], data.high[i:i+g.N])[1] for i in range(g.M)]

#2-3 择时模块-计算标准分
#通过斜率列表计算并返回截至回测结束日的最新标准分
def get_zscore(slope_series):
    mean = np.mean(slope_series)
    std = np.std(slope_series)
    return (slope_series[-1] - mean) / std

#2-4 择时模块-计算综合信号
#1.获得rsrs与MA信号,rsrs信号算法参考优化说明，MA信号为一段时间两个端点的MA数值比较大小
#2.信号同时为True时返回买入信号，同为False时返回卖出信号，其余情况返回持仓不变信号
def get_timing_signal(stock):
    #计算MA信号
    close_data = attribute_history(g.ref_stock, g.mean_day + g.mean_diff_day, '1d', ['close'])
    today_MA = close_data.close[g.mean_diff_day:].mean() 
    before_MA = close_data.close[:-g.mean_diff_day].mean()
    #计算rsrs信号
    high_low_data = attribute_history(g.ref_stock, g.N, '1d', ['high', 'low'])
    intercept, slope, r2 = get_ols(high_low_data.low, high_low_data.high)
    g.slope_series.append(slope)
    rsrs_score = get_zscore(g.slope_series[-g.M:]) * r2
    #综合判断所有信号
    if rsrs_score > g.score_threshold and today_MA > before_MA:
        print('BUY')
        return "BUY"
    elif rsrs_score < -g.score_threshold and today_MA < before_MA:
        print('SELL')
        return "SELL"
    else:
        print('KEEP')
        return "KEEP"


#3-1 过滤模块-过滤停牌股票
#输入选股列表，返回剔除停牌股票后的列表
def filter_paused_stock(stock_list):
	current_data = get_current_data()
	return [stock for stock in stock_list if not current_data[stock].paused]

#3-2 过滤模块-过滤ST及其他具有退市标签的股票
#输入选股列表，返回剔除ST及其他具有退市标签股票后的列表
def filter_st_stock(stock_list):
	current_data = get_current_data()
	return [stock for stock in stock_list
			if not current_data[stock].is_st
			and 'ST' not in current_data[stock].name
			and '*' not in current_data[stock].name
			and '退' not in current_data[stock].name]

#3-3 过滤模块-过滤涨停的股票
#输入选股列表，返回剔除未持有且已涨停股票后的列表
def filter_limitup_stock(context, stock_list):
	last_prices = history(1, unit='1m', field='close', security_list=stock_list)
	current_data = get_current_data()
	# 已存在于持仓的股票即使涨停也不过滤，避免此股票再次可买，但因被过滤而导致选择别的股票
	return [stock for stock in stock_list if stock in context.portfolio.positions.keys()
			or last_prices[stock][-1] < current_data[stock].high_limit]

#3-4 过滤模块-过滤跌停的股票
#输入股票列表，返回剔除已跌停股票后的列表
def filter_limitdown_stock(context, stock_list):
	last_prices = history(1, unit='1m', field='close', security_list=stock_list)
	current_data = get_current_data()
	return [stock for stock in stock_list if stock in context.portfolio.positions.keys()
			or last_prices[stock][-1] > current_data[stock].low_limit]



#4-1 交易模块-自定义下单
#报单成功返回报单(不代表一定会成交),否则返回None,应用于
def order_target_value_(security, value):
	if value == 0:
		log.debug("Selling out %s" % (security))
	else:
		log.debug("Order %s to value %f" % (security, value))
	# 如果股票停牌，创建报单会失败，order_target_value 返回None
	# 如果股票涨跌停，创建报单会成功，order_target_value 返回Order，但是报单会取消
	# 部成部撤的报单，聚宽状态是已撤，此时成交量>0，可通过成交量判断是否有成交
	return order_target_value(security, value)

#4-2 交易模块-开仓
#买入指定价值的证券,报单成功并成交(包括全部成交或部分成交,此时成交量大于0)返回True,报单失败或者报单成功但被取消(此时成交量等于0),返回False
def open_position(security, value):
	order = order_target_value_(security, value)
	if order != None and order.filled > 0:
		return True
	return False

#4-3 交易模块-平仓
#卖出指定持仓,报单成功并全部成交返回True，报单失败或者报单成功但被取消(此时成交量等于0),或者报单非全部成交,返回False
def close_position(position):
	security = position.security
	order = order_target_value_(security, 0)  # 可能会因停牌失败
	if order != None:
		if order.status == OrderStatus.held and order.filled == order.amount:
			return True
	return False

#4-4 交易模块-调仓
#当择时信号为买入时开始调仓，输入过滤模块处理后的股票列表，执行交易模块中的开平仓操作
def adjust_position(context, buy_stocks):
	for stock in context.portfolio.positions:
		if stock not in buy_stocks:
			log.info("[%s]已不在应买入列表中" % (stock))
			position = context.portfolio.positions[stock]
			close_position(position)
		else:
			log.info("[%s]已经持有无需重复买入" % (stock))
	# 根据股票数量分仓
	# 此处只根据可用金额平均分配购买，不能保证每个仓位平均分配
	position_count = len(context.portfolio.positions)
	if g.stock_num > position_count:
		value = context.portfolio.cash / (g.stock_num - position_count)
		for stock in buy_stocks:
			if context.portfolio.positions[stock].total_amount == 0:
				if open_position(stock, value):
					if len(context.portfolio.positions) == g.stock_num:
						break

#4-5 交易模块-择时交易
#结合择时模块综合信号进行交易
def my_trade(context):
    #获取选股列表并过滤掉:st,st*,退市,涨停,跌停,停牌
    check_out_list = get_rank(g.stock_pool)
    check_out_list = filter_st_stock(check_out_list)
    check_out_list = filter_limitup_stock(context, check_out_list)
    check_out_list = filter_limitdown_stock(context, check_out_list)
    check_out_list = filter_paused_stock(check_out_list)
    print('今日自选股:{}'.format(check_out_list))
    #获取综合择时信号
    timing_signal = get_timing_signal(g.ref_stock)
    print('今日择时信号:{}'.format(timing_signal))
    #开始交易
    if timing_signal == 'SELL':
        for stock in context.portfolio.positions:
            position = context.portfolio.positions[stock]
            close_position(position)
    elif timing_signal == 'BUY' or timing_signal == 'KEEP':
        adjust_position(context, check_out_list)
    else:
        pass

#4-6 交易模块-止损
#检查持仓并进行必要的止损操作
def check_lose(context):
    for position in list(context.portfolio.positions.values()):
        securities=position.security
        cost=position.avg_cost
        price=position.price
        ret=100*(price/cost-1)
        value=position.value
        amount=position.total_amount
        #这里设定80%止损几乎等同不止损，因为止损在指数etf策略中影响不大
        if ret <=-20:
            order_target_value(position.security, 0)
            print("！！！！！！触发止损信号: 标的={},标的价值={},浮动盈亏={}% ！！！！！！"
                .format(securities,format(value,'.2f'),format(ret,'.2f')))

#5-1 复盘模块-打印
#打印每日持仓信息
def print_trade_info(context):
    #打印当天成交记录
    trades = get_trades()
    for _trade in trades.values():
        print('成交记录：'+str(_trade))
    #打印账户信息
    for position in list(context.portfolio.positions.values()):
        securities=position.security
        cost=position.avg_cost
        price=position.price
        ret=100*(price/cost-1)
        value=position.value
        amount=position.total_amount    
        print('代码:{}'.format(securities))
        print('成本价:{}'.format(format(cost,'.2f')))
        print('现价:{}'.format(price))
        print('收益率:{}%'.format(format(ret,'.2f')))
        print('持仓(股):{}'.format(amount))
        print('市值:{}'.format(format(value,'.2f')))
    print('一天结束')
    print('———————————————————————————————————————分割线————————————————————————————————————————')
