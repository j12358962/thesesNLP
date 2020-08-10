# -*- coding: utf-8 -*-
import logging
import gensim
import jieba
import numpy as np
import pymysql
import pandas as pd
import re
import os

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


# 設定你的資料庫 ip, port, 帳號, 密碼
db_settings = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "db": "thesesComparison",
    "charset": "utf8"
}

# connect to database
try:
    conn = pymysql.connect(**db_settings)
    cur = conn.cursor()
except Exception as e:
    print(e)

def getProjectData(projectName):

    cur.execute('SELECT projectHost, abstract_ch, startTime, endTime  FROM `project-information` WHERE projectName="%s"' % projectName)
    projectInfo = cur.fetchone()
    return projectInfo

def getThesesData(professorName):
    cur.execute('SELECT thesesName_ch, abstract_ch, publishYear FROM `theses-information` WHERE professorName_ch LIKE "%%'+professorName+'%%"')
    thesesInfo = cur.fetchall()
    return thesesInfo

def segment(doc: str):
    """中文分词
    Arguments:
        doc {str} -- 输入文本
    Returns:
        [type] -- [description]
    """


    # 停用詞
    stop_words = pd.read_csv("stopword.txt", index_col=False, quoting=3,
                             names=['stopword'],
                             sep="\n",
                             encoding='utf-8')
    stop_words = list(stop_words.stopword)
    reg_html = re.compile(r'<[^>]+>', re.S)
    doc = reg_html.sub('', doc)
    doc = re.sub('[０-９]', '', doc)
    doc = re.sub('\s', '', doc)
    word_list = list(jieba.cut(doc))
    out_str = ''
    for word in word_list:
        if word not in stop_words:
            out_str += word
            out_str += ' '
    segments = out_str.split(sep=" ")
    return segments

def test_model(projectAbstract, thesesAbstract):

    st1 = projectAbstract
    st2 = thesesAbstract[1]
    # 分詞
    st1 = segment(st1)
    st2 = segment(st2)
    # 轉成句子向量
    vect1 = sent2vec(model, st1)
    vect2 = sent2vec(model, st2)

    from scipy import spatial
    cos = 1 - spatial.distance.cosine(vect1, vect2)
    return cos

def sent2vec(model, words):
    """文本轉換成向量

    Arguments:
        model {[type]} -- Doc2Vec 模型
        words {[type]} -- 分詞後的文本

    Returns:
        [type] -- 向量數組
    """

    vect_list = []
    for w in words:
        try:
            vect_list.append(model.wv[w])
        except:
            continue
    vect_list = np.array(vect_list)
    vect = vect_list.sum(axis=0)
    return vect / np.sqrt((vect ** 2).sum())



if __name__ == '__main__':

    try:
        os.mkdir("output")
    except:
        print("資料夾已存在")

    print("Load model...")
    model = gensim.models.Doc2Vec.load('models\\theses_doc2vec.model')
    jieba.set_dictionary('dict.txt.big')

    #拿到所有計畫的名稱
    cur.execute('SELECT projectName, projectHost FROM `project-information`')
    projectTuples = cur.fetchall()

    for projectTuple in projectTuples:
        projectName = projectTuple[0]
        similarityList = []
        # projectName = '運用低功耗廣域物聯網於智慧電網之需求面管理架構'
        projectInfo = getProjectData(projectName)
        thesesData = getThesesData(projectInfo[0])
        for element in thesesData:
            similarityList.append((element[0], element[2], test_model(projectInfo[1], element)))
        similarityDF = pd.DataFrame.from_records(similarityList, columns=['論文標題', '論文年份', '相似度'])
        title = projectName + ",執行起迄：" + str(projectInfo[2]) + "~" + projectInfo[3] + "\n"

        #照相似度排序
        similarityDF = similarityDF.sort_values(by=['相似度'], ascending=False)
        similarityDF = similarityDF.round(4)
        similarityDF = similarityDF.reset_index(drop=True)

        if(similarityDF.相似度[0]>0.45):
            outputFileName = 'output\\正面例子-'+projectName+'相關的論文.csv'
            outputFileName = re.sub(":", "-", outputFileName)
        elif(similarityDF.相似度[0]<0.18):
            outputFileName = 'output\\反面例子-'+projectName+'相關的論文.csv'
            outputFileName = re.sub(":", "-", outputFileName)
        else:
            outputFileName = 'output\\'+projectName+'相關的論文.csv'
            outputFileName = re.sub(":", "-", outputFileName)
        with open(outputFileName, 'w', encoding='utf-8') as f:
            f.write(title)

        similarityDF.to_csv(outputFileName, mode='a', index=False)
