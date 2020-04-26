# -*- coding=UTF-8 -*-
from snownlp import sentiment
from snownlp import SnowNLP
# sentiment.train('D:\\SnowNLP\\snownlp-0.12.3\\snownlp\\sentiment\\neg.txt', 
#                 'D:\\SnowNLP\\snownlp-0.12.3\\snownlp\\sentiment\\pos.txt')
# sentiment.save('D:\\SnowNLP\\snownlp-0.12.3\\snownlp\\sentiment\\sentiment.marshal')

def Analyse(arr):
    ans = []
    for i in range(len(arr)):
        text = arr[i]
        s = SnowNLP(text)
        # print(s.sentiments)
        if s.sentiments <= 0.0009 or s.sentiments > 1:
            ans.append(0)
        else:
            ans.append(1)
    return ans

