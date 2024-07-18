import pywencai
word='人气排行'
df=pywencai.get(question=word,loop=True)
print(df)
