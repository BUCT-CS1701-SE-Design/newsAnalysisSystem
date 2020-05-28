# newsAnalysisSystem
## 数据获取与处理
   主要使用Request和BeautifulSoup。
   借助网站搜索引擎爬虫，利用正则表达式排除无关信息。
   详见main.py
## 新闻分析
   使用SnowNLP。自定义训练集并逐步完善。详见sense.py。
## 数据定制
   可以改变爬虫规则获取指定参数的新闻。
   可以爬取指定博物馆的指定时间段的新闻，默认是爬取所有博物馆的一年内的新闻。
   详见main.py
## 数据更新入库
   确保数据库中，同一个博物馆的新闻列表下没有重复的新闻，结合Python和mysql查询及添加语言更新入库。详见main.py。
## 部分数据展示
   + data.csv --- 依据数据库定义
   + titles.csv --- 新闻分析的输入
   + names.csv --- 统一各博物馆的编号
   + names.csv --- 统一各博物馆的编号
