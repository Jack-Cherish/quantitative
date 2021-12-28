import hs_udata as udata
from pyecharts import options as opts
from pyecharts.charts import Pie
from tqdm import tqdm

if __name__ == "__main__":
    # 替换你的 token，查看 token 地址：https://udata.hs.net/console/overAllView
    udata.set_token(token = 'xxxxx')
    # 获取所有股票
    data = udata.stock_list(listed_state = "1")
    codes = data['hs_code'].tolist()
    
    industry_name_dict = {}
    # 遍历股票
    for code in tqdm(codes):
        # 获取股票行业信息
        data = udata.industry_category(en_prod_code = code)
        industry_name_csrc = data['industry_name_csrc'][0].split("-")[0]
        # print(industry_name_csrc)
        # 统计行业数量
        if industry_name_csrc not in industry_name_dict.keys():
            industry_name_dict[industry_name_csrc] = 1
        else:
            industry_name_dict[industry_name_csrc] += 1

    # 可视化
    c = (
        Pie()
        .add(
            "",
            [
                list(z)
                for z in zip(
                    industry_name_dict.keys(),
                    industry_name_dict.values(),
                )
            ],
            center=["40%", "50%"],
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="A 股股票行业分布"),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="80%", orient="vertical"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        .render("pie.html")
    )
