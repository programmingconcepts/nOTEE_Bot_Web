import pandas as pd
from transformers import pipeline
import numpy as np
import argparse
from keybert import KeyBERT

from sentence_transformers import SentenceTransformer

# build an argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-q", "--query", required=True, help="Please provide a query")
args = vars(ap.parse_args())

sentence_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

nlp_QA = pipeline("question-answering", model = "bert-large-uncased-whole-word-masking-finetuned-squad")

csv_file_path = "D:/Programming Concepts/Codes/Visual Studio/nOTEE_Bot_Web/nOTEE_Bot_Web/Python/NewData.csv"
df = pd.read_csv(csv_file_path)

Key_Thres = 0.5
Topic_Thres = 0.5

def get_query_keys(query):
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(query, keyphrase_ngram_range=(1, 2))
    keys = ""
    for element in keywords:
        keys += ", " + element[0]

    return keys.strip(", ")


def find_most_similar_topic(query, topics, texts):
    query_embedding = np.array(sentence_model.encode([query]))

    topic_similarities = [np.dot(query_embedding, np.array(sentence_model.encode([topic]))[0]) /
                    (np.linalg.norm(query_embedding) * np.linalg.norm(np.array(sentence_model.encode([topic]))[0]))
                    for topic in topics]
    
    query_keys = get_query_keys(query)

    query_keys_embedding = np.array(sentence_model.encode([query]))

    keys = df["Keys"]

    keys_similarities = [np.dot(query_keys_embedding, np.array(sentence_model.encode([key]))[0]) /
                    (np.linalg.norm(query_keys_embedding) * np.linalg.norm(np.array(sentence_model.encode([key]))[0]))
                    for key in keys]
    
    maxTopic = max(topic_similarities)
    maxKey = max(keys_similarities)

    print("Topic: ", maxTopic)
    print("Key: ", maxKey)

    if(maxKey >= Key_Thres or maxTopic >= Topic_Thres):
        if(maxTopic > maxKey):
            most_similar_index = topic_similarities.index(maxTopic)
        else:
            most_similar_index = keys_similarities.index(maxKey)

        return texts[most_similar_index]

    return "[Sorry]"


def extract_related_text(query, text):
    result = nlp_QA(question = query, context = text)
    return result["answer"]

def create_text_summarizer():
    summarizer = pipeline("summarization", model = "t5-small")
    return summarizer

def summarize_text(text, summarizer):
    summary = summarizer(text, max_length = 500, min_length = 50, length_penalty = 2.0, num_beams = 4, early_stopping=True)

    return summary[0]["summary_text"]


t5_summarizer = create_text_summarizer()

user_query = args["query"]

most_similar_text = find_most_similar_topic(user_query, df["Topic"], df["Text"])

if(most_similar_text == "[Sorry]"):
    print("Sorry! I Couldn't find anything. Please try with another query.")
else:
    summary = summarize_text(most_similar_text, t5_summarizer)

    related_text = extract_related_text(user_query, most_similar_text)

    if(related_text):
        print("[QA]")
        print(related_text)

        print("[ST]")
        print(summary)

    else:
        print("No relevant information found.")