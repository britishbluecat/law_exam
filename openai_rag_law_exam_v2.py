import openai
import pandas as pd
import pickle
import os
from rank_bm25 import BM25Okapi
from janome.tokenizer import Tokenizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# APIキーの設定
api_key = ''
openai.api_key = api_key

# ユーザーインプット
user_input = "行政調査のそれぞれの調査方法を教えてください。"

clear_cache_flg = 0  # 1の場合、キャッシュを無視して新たにインデックスを生成します

INDEX_FILE = 'bm25_index.pkl'
TOKENIZED_CORPUS_FILE = 'tokenized_corpus.pkl'
DOCUMENTS_FILE = 'documents.pkl'

tokenizer = Tokenizer()

def tokenize(text):
    return [token.surface for token in tokenizer.tokenize(text)]

def load_index():
    if clear_cache_flg == 1:
        print("キャッシュクリアフラグが設定されています。新規インデックスを作成します。")
        return None, None, None
    if os.path.exists(INDEX_FILE) and os.path.exists(TOKENIZED_CORPUS_FILE) and os.path.exists(DOCUMENTS_FILE):
        print("インデックスを読み込み中...")
        with open(INDEX_FILE, 'rb') as f:
            bm25 = pickle.load(f)
        with open(TOKENIZED_CORPUS_FILE, 'rb') as f:
            tokenized_corpus = pickle.load(f)
        with open(DOCUMENTS_FILE, 'rb') as f:
            documents = pickle.load(f)
        return bm25, tokenized_corpus, documents
    else:
        return None, None, None

def save_index(bm25, tokenized_corpus, documents):
    print("インデックスを保存中...")
    with open(INDEX_FILE, 'wb') as f:
        pickle.dump(bm25, f)
    with open(TOKENIZED_CORPUS_FILE, 'wb') as f:
        pickle.dump(tokenized_corpus, f)
    with open(DOCUMENTS_FILE, 'wb') as f:
        pickle.dump(documents, f)

excel_file = 'law_exam_data.xlsx'
df = pd.read_excel(excel_file)

documents = df['問題文'].tolist()
civil_law = df['民法 (0,1)'].tolist()
administrative_law = df['行政法 (0,1)'].tolist()
constitutional_law = df['憲法 (0,1)'].tolist()

bm25, tokenized_corpus, saved_documents = load_index()

if bm25 is None or tokenized_corpus is None or saved_documents is None:
    print("新規インデックスを作成中...")
    tokenized_corpus = [tokenize(doc) for doc in documents]
    bm25 = BM25Okapi(tokenized_corpus)
    save_index(bm25, tokenized_corpus, documents)

tokenized_query = tokenize(user_input)
scores = bm25.get_scores(tokenized_query)

best_index = scores.argmax()
relevant_document = documents[best_index]
relevant_civil_law = civil_law[best_index]
relevant_administrative_law = administrative_law[best_index]
relevant_constitutional_law = constitutional_law[best_index]

# プロンプトの作成
prompt_template = """
あなたは、法学試験の過去問を使用して、予想問題を出せる程度、法学がわかります。
この問題は、法学過去問データに基づいて回答されます。

問題文: {relevant_document}
この問題は次の法律に関連しています:
- 民法: {relevant_civil_law}
- 行政法: {relevant_administrative_law}
- 憲法: {relevant_constitutional_law}

ユーザーの質問: {user_input}
"""

prompt = prompt_template.format(
    relevant_document=relevant_document,
    relevant_civil_law="関連あり" if relevant_civil_law == 1 else "関連なし",
    relevant_administrative_law="関連あり" if relevant_administrative_law == 1 else "関連なし",
    relevant_constitutional_law="関連あり" if relevant_constitutional_law == 1 else "関連なし",
    user_input=user_input
)

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "あなたは役に立つ法学アシスタントです。"},
        {"role": "user", "content": prompt}
    ]
)

output_text = response.choices[0].message['content']
print("関連する過去問:", relevant_document)
print("AIの回答:", output_text)

# 埋め込みモデルを使用した類似性評価
def get_embedding(text):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response['data'][0]['embedding']

def evaluate_similarity_embedding(reference, response):
    reference_embedding = get_embedding(reference)
    response_embedding = get_embedding(response)
    similarity = cosine_similarity(
        [reference_embedding],
        [response_embedding]
    )[0][0]

    if similarity > 0.9:
        return 10
    elif similarity > 0.7:
        return 8
    elif similarity > 0.4:
        return 4
    else:
        return 0

# 類似性スコアの計算
similarity_score_embedding = evaluate_similarity_embedding(relevant_document, output_text)
print("埋め込みモデルによる類似性スコア:", similarity_score_embedding)
