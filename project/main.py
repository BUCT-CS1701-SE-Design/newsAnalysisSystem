# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup,Comment
import re
import pandas as pd
import numpy as np
import os
from sense import Analyse
from sqlalchemy import create_engine
import pymysql

import datetime

def to_date(s):
    # print(s)
    y,m,d=s.split("-")
    date=datetime.date(int(y),int(m),int(d))
    return date

def read_file():
    res=[]
    current_path = os.path.dirname(__file__)
    names=pd.read_csv(current_path+'names.csv') # 此处如果本地运行需要写成 current_path+'\\names.csv'格式
    for x in names['name']:
        res.append(x)
    return res

def write_file(titles):
    a=np.array(titles).reshape((len(titles),1))
    df=pd.DataFrame(a)
    df.columns=['title']
    current_path = os.path.dirname(__file__)
    df.to_csv(current_path+'\\titles.csv',encoding='utf_8_sig')

def get_news(news,idx):
    try:
        hd={'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.6)', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}
        r=requests.get(news,headers=hd,timeout=1000)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        soup=BeautifulSoup(r.text,'html.parser')
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))
        [comment.extract() for comment in comments]

        time0=re.compile(r'\d\d\d\d年\d\d月\d\d日 \d\d:\d\d')
        time=str(soup.find(text=time0))
        time=time.replace('年','-')
        time=time.replace('月','-')
        time=time.replace('日','')
        time=time[-16::]
        # time=time[:11:]

        title0=soup.find('h1')
        title=None
        if title0==None:
            title1=soup.find(name='div',class_='title')
            if title1:
                title=title1.text
        else:
            title=title0.string
        if title==None:
            return {'id':None,'title':None,'content':None,'time':None}
        title=title.replace('\n','')

        pic=re.compile(r'(\u3000)*((资料图)|(编辑)|((\n)?原标题))')
        res=""
        cont1=re.compile(r'(content)|(cnt_bd)')
        cont2=re.compile(r'cont')
        content=soup.find(name='div',class_=cont1)
        if content==None:
            content=soup.find(name='div',class_=cont2)
        for text0 in content.find_all(name=['p']):
            if text0.get('style')=="text-align: center;":
                continue
            if text0.text==None:
                continue
            if pic.match(text0.text):
                continue
            res+=str(text0.text)
            res+='\n'
        res.replace('\u3000',' ')
        if res=='':
            return {'id':None,'title':None,'content':None,'time':None}
        dic={'id':str(idx),'title':title,'content':res,'time':time}
        return dic    
    except:
        return {'id':None,'title':None,'content':None,'time':None}

# get_news('http://news.cctv.com/2019/09/09/ARTISfcJJbpt2x9WBMeTUFTS190909.shtml',1)

def get_url(name,time_id):
    urls=[]
    imgs=[]
    num=1
    while True:
        try:
            hd={'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.6)', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}
            kv={
                'qtext': name,
                'sort':'date',
                'type':'web',
                'datepid':str(time_id),
                'channel':'新闻',
                'page': str(num)
            }
            r=requests.get('https://search.cctv.com/search.php',headers=hd,params=kv)
            # print(r.text)
            r.raise_for_status()
            r.encoding=r.apparent_encoding
            soup=BeautifulSoup(r.text,'html.parser')
            comments = soup.findAll(text=lambda text: isinstance(text, Comment))
            [comment.extract() for comment in comments]

            result=re.compile(r'(.)*全部网页结果共')
            aaa=soup.find(text=result)
            aa=str(aaa)
            xxx=result.match(aa).span()
            tot=int(aa[xxx[1]:len(aa)-1:])
            tot=(tot+9)//10

            pre=re.compile(r'link_p.php[?]targetpage=http://news(.)*html&')
            for xa in soup.find_all(name='div',class_='tright'):
                link=xa.find('a')
                x=link.get('href')
                
                if pre.match(x):
                    xx=pre.match(x).span()
                    urls.append(x[22:xx[1]-1:])
                else: 
                    continue
                imgg=xa.find('img')
                imgx=imgg.get('src')
                if imgx:
                    imgs.append(imgx)
                else:
                    imgs.append('https://p1.img.cctvpic.com/photoAlbum/templet/common/DEPA1546583592748817/logo31.png')    
            num+=1
            if num>tot:
                break
        except:
            # print('fuck')
            return urls,imgs
    return urls,imgs

def check(x):
    if x==0:
        return 'negative'
    else:
        return 'positive'

#time_id: 1为全部 2为一周内 3为一个月内 4为半年内 5为一年内 默认为全部
#museum_name:指定博物馆 默认为全部
#start_time,end_time:指定时间段
def get_resualt(museum_name='',start_time='1949-10-01',end_time='2049-10-01',time_id=1):
    titles=[]
    tt=[]
    names=[]
    names=read_file()
    data={
        'newsID':[],
        'museumID':[],
        'newsTitle':[],
        'newsTime':[],
        'newsmaintext':[],
        'positive/negative':[],
        'imageurl':[],
    }
    # 获得现有记录数
    db=pymysql.connect("rm-bp1k0s6kbpm66bpfc4o.mysql.rds.aliyuncs.com", "test2", "test2", "museumapplication")
    cursor=db.cursor()
    query=" select max(newsID) from {}".format('museumnews')
    cursor.execute(query)
    db.commit()
    cnt=cursor.fetchall()
    xxxx=cnt[0][0]
    if xxxx==None:xxxx=0
    print('x=',xxxx)
    for i,name in enumerate(names):
        if not museum_name=='':
            if not name==museum_name:
                continue
        idx=i+1
        print(name, idx)
        urls,imgs=get_url(name,time_id)
        # print(urls)
        for x,imgx in zip(urls,imgs):
            xxxx+=1
            xx=get_news(x,idx)
            if xx['id']==None or xx['title']==None or xx['content']==None or xx['time']==None:
                tt.append(x)
                continue
            
            timex=str(xx['time'])
            datex=timex[:11:]
            time_re=re.compile(r'\d\d\d\d-\d\d-\d\d')
            if not time_re.match(timex):
                continue
            if to_date(start_time)>to_date(datex) or to_date(end_time)<to_date(datex):
                continue
            print('start_time=', start_time, 'end_time=', end_time, 'timex=', timex)

            #判断是否已经在库中
            print("title=", xx['title'])
            sql="select * from museumnews where newsTitle='%s' and museumID='%s'" % (xx['title'],xx['id'])
            exist = cursor.execute(sql)
            print('exist=', exist, ' title=', xx['title'], ' time=', xx['time'],)
            if exist:
                xxxx-=1
            else:
                # print("yes", xx['title'], xx['time'])
                data['newsID'].append(str(xxxx))
                data['museumID'].append(xx['id'])
                data['newsTitle'].append(xx['title'])
                data['newsmaintext'].append(xx['content'])
                data['newsTime'].append(str(xx['time']))
                data['imageurl'].append(imgx)
                titles.append(xx['title'])

        #     if xxxx>=3:
        #         break
        # if xxxx>=3:
        #     break
    data['positive/negative']=list(map(check,Analyse(titles)))
    df=pd.DataFrame(data)

    # print(df)
    engine = create_engine('mysql+pymysql://test2:test2@rm-bp1k0s6kbpm66bpfc4o.mysql.rds.aliyuncs.com/museumapplication')
    df.to_sql(name='museumnews',con=engine,chunksize=500,if_exists='append',index=None)
    # print(tt)
    # current_path = os.path.dirname(__file__)
    # df.to_csv(current_path+'\\data.csv',encoding='utf_8_sig')
    # write_file(titles)

get_resualt(museum_name=m,start_time=s,end_time=e)