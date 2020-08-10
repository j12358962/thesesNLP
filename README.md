# 論文相似度比較程式

## 第一次使用：
1. 安裝 docker compose 後，在有 ```docker-compose.yml``` 的目錄執行
 ```docker-compose down && docker-compose up -d && docker-compose up```
2. 安裝需要的套件，執行 ```pip install -r requirements.txt```

## (選) 下載 train 好的 model 及 維基百科已分詞過的資料
[shorturl.at/ixJN5](https://)

## 如果想自己重新 train 一個 model：
1. 將資料放入 data/corpus_words (相對文件根目錄)
2. ```python train.py```

## 比較科技部計畫：
1. 執行 ```python test_model.py```
2. csv資料會以科技部計畫名稱為檔名存在 output 資料夾中