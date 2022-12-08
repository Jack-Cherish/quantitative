# 指数代码常量
SH_INDEX_CODE = "sh000001"
A_STOCK_INDEX_CODE = "sh000002"
B_STOCK_INDEX_CODE = "sh000003"

# 股票标识列常量
COL_DATE = '日期'
COL_CODE = '代码'

# 基础指标列常量
COL_OPEN = '开盘'
COL_CLOSE = '收盘'
COL_HIGHEST = '最高'
COL_LOWESR = '最低'
COL_DEAL_MONEY = '成交额'
COL_DEAL_AMOUNT = '成交量'
COL_AMPLITUDE = '振幅'
COL_CHANGE_RATE = '涨跌幅'
COL_CHANGE_RATE_NORMALIZE_BY_A_STOCK_INDEX = '正则化涨跌幅(A股)'
COL_CHANGE_RATE_NORMALIZE_BY_CUR_DAY_STOCK = '正则化涨跌幅(当天数据)'
COL_CHANGE_NUM = '涨跌额'
COL_EXCHANGE_RATE = '换手率'
BASE_INDEX_COLS = [
    COL_OPEN
    , COL_CLOSE
    , COL_HIGHEST
    , COL_LOWESR
    , COL_DEAL_MONEY
    , COL_DEAL_AMOUNT
    , COL_AMPLITUDE
    , COL_CHANGE_RATE
    , COL_CHANGE_NUM
    , COL_EXCHANGE_RATE
]

# 计算指标列常量
COL_DAY_ORDER = 'day_order'
COL_HIGHEST_RATE = '最高振幅'
COL_LOWEST_RATE = '最低振幅'
COL_A_STOCK_INDEX_RATE = 'A股大盘指数'
CACULATE_INDEX_COLS = [
    COL_DAY_ORDER
    , COL_HIGHEST_RATE
    , COL_LOWEST_RATE
    , COL_A_STOCK_INDEX_RATE
]

# 一些股票代码常量
XINPIAN_ETF_CODE = "sh512760"
GUANGFU_ETF_CODE = "sz159857"

# 数据文件保存路径
HISTORY_DATA_PATH = './data/stock_history_df'

# 获取pre day后缀函数
def suffix(colName, day) -> str:
    return colName + f'pre_{day}_day'
