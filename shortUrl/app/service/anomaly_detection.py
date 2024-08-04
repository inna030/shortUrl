import os

import boto3
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
from app.models.database import dynamodb
from app.service.shorten_url import get_url_length, get_num_special_chars, table

table = dynamodb.Table('urls')
def fetch_data_from_dynamodb(table_name):


    response = table.scan()
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    return pd.DataFrame(data)

def preprocess_data(df):
    df['url_length'] = df['original_url'].apply(get_url_length)
    df['num_special_chars'] = df['original_url'].apply(get_num_special_chars)
    df['domain_age'] = df['domain_age'].astype(int)
    df['content_features'] = df['content_features'].astype(float)
    X = df[['url_length', 'num_special_chars', 'domain_age', 'content_features']]
    y = df['is_malicious']
    return X, y

def train_anomaly_detection_model():
    df = fetch_data_from_dynamodb('urls')
    X = preprocess_data(df)

    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X)

    joblib.dump(model, 'anomaly_detection_model.joblib')
    print("Anomaly detection model trained and saved successfully.")

def detect_anomaly(features):
    model = joblib.load('anomaly_detection_model.joblib')
    prediction = model.predict([features])
    return prediction[0] == -1

