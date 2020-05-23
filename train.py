import gensim
from os import listdir

def train():
    """训练 Doc2Vec 模型
    """

    # 先把所有文檔的路徑存進一個 array中，docLabels：
    data_dir = "./data/corpus_words"
    docLabels = [f for f in listdir(data_dir) if f.endswith('.txt')]

    data = []
    for doc in docLabels:
        ws = open(data_dir + "/" + doc, 'r', encoding='UTF-8').read()
        data.append(ws)

    print(len(data))
    # 訓練 Doc2Vec，並保存模型：
    sentences = LabeledLineSentence(data, docLabels)
    # an empty model
    model = gensim.models.Doc2Vec(vector_size=256, window=10, min_count=5,
                                  workers=12, alpha=0.00001, min_alpha=0.00001, epochs=30)
    model.build_vocab(sentences)
    print("開始訓練...")
    model.train(sentences, total_examples=model.corpus_count, epochs=30)

    model.save('models\\theses_doc2vec.model')
    print("model saved")

class LabeledLineSentence(object):
    def __init__(self, doc_list, labels_list):
        self.labels_list = labels_list
        self.doc_list = doc_list

    def __iter__(self):
        for idx, doc in enumerate(self.doc_list):
            yield gensim.models.doc2vec.TaggedDocument(words=doc.split(), tags=[self.labels_list[idx]])


if __name__ == '__main__':
    #如果要 train 自己的 model 就將這行註解取消，train好後再註解起來
    train()