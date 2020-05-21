# -*- coding=UTF-8 -*-
from snownlp import sentiment
from snownlp import SnowNLP
import pandas as pd 
import os

def train():
    current_path = os.path.dirname(__file__)
    neg=current_path+'\\snownlp\\sentiment\\neg.txt'
    pos=current_path+'\\snownlp\\sentiment\\pos.txt'
    parm=current_path+'\\snownlp\\sentiment\\sentiment.marshal'
    sentiment.train(neg, pos)
    sentiment.save(parm)

# train()

def Analyse(arr):
    ans = []
    for i in range(len(arr)):
        text = arr[i]
        # print(text)
        s = SnowNLP(text)
        # print(s.sentiments)
        if s.sentiments <= 0.001 or s.sentiments > 1:
            ans.append(0)
        else:
            ans.append(1)
    return ans



