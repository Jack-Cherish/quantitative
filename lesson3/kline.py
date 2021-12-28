#-*- coding:utf-8 -*-
import hs_udata as udata
from datetime import datetime, timedelta
import time
from pyecharts import options as opts
from pyecharts.charts import Kline

if __name__ == "__main__":
    # 替换你的 token，查看 token 地址：https://udata.hs.net/console/overAllView
    udata.set_token(token = 'xxxxx')

    current_dt = time.strftime("%Y-%m-%d", time.localtime())
    current_dt = datetime.strptime(current_dt, '%Y-%m-%d')

    # 获取 30 天的数据
    day_num = 30
    all_data = []
    all_date = []
    for i in range(1, day_num + 1)[::-1]:
        search_date = current_dt - timedelta(days = i)
        search_date = search_date.strftime("%Y%m%d")
        
        # 恒生电子近 30 日的股价
        data = udata.stock_quote_daily(en_prod_code = "600570.SH", trading_date = search_date)
        # 开盘价
        open_price = data['open_price'][0]
        # 收盘价
        close_price = data['close_price'][0]
        # 最低价
        low_price = data['low_price'][0]
        # 最高价
        high_price = data['high_price'][0]
        # 去掉非交易日数据
        if len(open_price) == 0:
            continue
        all_date.append(search_date)
        all_data.append([float(open_price), float(close_price), float(low_price), float(high_price)])
    
    # 使用 pyecharts 绘制 K 线
    c = (
        Kline()
        .add_xaxis(all_date)
        .add_yaxis(
            "K线",
            all_data,
            itemstyle_opts = opts.ItemStyleOpts(
                color = "#ec0000",
                color0 = "#00da3c",
                border_color = "#8A0000",
                border_color0 = "#008F28",
            ),
        )
        .set_global_opts(
            xaxis_opts = opts.AxisOpts(is_scale = True),
            yaxis_opts = opts.AxisOpts(
                is_scale = True,
                splitarea_opts = opts.SplitAreaOpts(
                    is_show = True, areastyle_opts = opts.AreaStyleOpts(opacity = 1)
                ),
            ),
            datazoom_opts = [opts.DataZoomOpts(type_ = "inside")],
            title_opts = opts.TitleOpts(title = "恒生电子近 30 日 K 线"),
        )
        .render("kline.html")
    )
