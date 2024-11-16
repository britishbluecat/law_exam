import openai
import pandas as pd
import pickle
import os
from rank_bm25 import BM25Okapi
from janome.tokenizer import Tokenizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# APIキーの設定
def load_api_key():
    key_file = 'key.txt'
    if os.path.exists(key_file):
        with open(key_file, 'r') as f:
            return f.readline().strip()
    else:
        raise FileNotFoundError("key.txt が見つかりません。APIキーを設定してください。")

# APIキーの読み込み
api_key = load_api_key()
openai.api_key = api_key

# インデックスファイルの設定
INDEX_FILE = 'bm25_index.pkl'
TOKENIZED_CORPUS_FILE = 'tokenized_corpus.pkl'
DOCUMENTS_FILE = 'documents.pkl'

tokenizer = Tokenizer()

def tokenize(text):
    return [token.surface for token in tokenizer.tokenize(text)]

def load_index(clear_cache_flg=0):
    if clear_cache_flg == 1:
        return None, None, None
    if os.path.exists(INDEX_FILE) and os.path.exists(TOKENIZED_CORPUS_FILE) and os.path.exists(DOCUMENTS_FILE):
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
    with open(INDEX_FILE, 'wb') as f:
        pickle.dump(bm25, f)
    with open(TOKENIZED_CORPUS_FILE, 'wb') as f:
        pickle.dump(tokenized_corpus, f)
    with open(DOCUMENTS_FILE, 'wb') as f:
        pickle.dump(documents, f)

# Excelファイルの読み込み
def prepare_data():
    df = pd.read_excel('law_exam_data.xlsx')
    documents = df['問題文'].tolist()
    civil_law = df['民法 (0,1)'].tolist()
    administrative_law = df['行政法 (0,1)'].tolist()
    constitutional_law = df['憲法 (0,1)'].tolist()
    return documents, civil_law, administrative_law, constitutional_law

def create_index(documents):
    tokenized_corpus = [tokenize(doc) for doc in documents]
    bm25 = BM25Okapi(tokenized_corpus)
    save_index(bm25, tokenized_corpus, documents)
    return bm25

# 埋め込みモデルを使用してテキストの埋め込みを取得
def get_embedding(text):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response['data'][0]['embedding']

# 埋め込みベースの類似性スコアを計算
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

# ユーザーの質問に対する回答を生成
def generate_response(user_input, clear_cache_flg=0):
    documents, civil_law, administrative_law, constitutional_law = prepare_data()
    bm25, tokenized_corpus, saved_documents = load_index(clear_cache_flg)

    if bm25 is None:
        bm25 = create_index(documents)

    tokenized_query = tokenize(user_input)
    scores = bm25.get_scores(tokenized_query)

    best_index = scores.argmax()
    relevant_document = documents[best_index]
    relevant_civil_law = civil_law[best_index]
    relevant_administrative_law = administrative_law[best_index]
    relevant_constitutional_law = constitutional_law[best_index]

    prompt_template = f"""
    あなたは、法学試験の過去問を使用して、予想問題を出せる程度、法学がわかります。
    この問題は、法学過去問データに基づいて回答されます。

    問題文: {relevant_document}
    この問題は次の法律に関連しています:
    - 民法: {'関連あり' if relevant_civil_law == 1 else '関連なし'}
    - 行政法: {'関連あり' if relevant_administrative_law == 1 else '関連なし'}
    - 憲法: {'関連あり' if relevant_constitutional_law == 1 else '関連なし'}

    ユーザーの質問: {user_input}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "あなたは役に立つ法学アシスタントです。"},
            {"role": "user", "content": prompt_template}
        ]
    )
    output_text = response.choices[0].message['content']

    # 埋め込みモデルによる類似性スコアの計算
    similarity_score_embedding = evaluate_similarity_embedding(relevant_document, output_text)

    return relevant_document, output_text, similarity_score_embedding
