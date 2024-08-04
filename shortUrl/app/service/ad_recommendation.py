import boto3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
import joblib
import logging

from app.models.database import dynamodb

table = dynamodb.Table('user_interactions')

def calculate_rating(interaction_type):
    interaction_points = {
        'view': 1,
        'click': 3,
        'purchase': 5
    }
    return interaction_points.get(interaction_type, 0)

def record_interaction(user_id, ad_id, interaction_type):
    rating = calculate_rating(interaction_type)

    try:
        response = table.update_item(
            Key={'user_id': user_id, 'ad_id': ad_id},
            UpdateExpression='SET rating = rating + :val',
            ExpressionAttributeValues={':val': rating},
            ReturnValues='UPDATED_NEW'
        )
        logging.info(f"Interaction recorded: {response}")
    except Exception as e:
        logging.error(f"An error occurred while recording interaction: {e}")

def fetch_interaction_data():
    response = table.scan()
    data = response['Items']
    return pd.DataFrame(data)

def preprocess_data(df):
    if not all(col in df.columns for col in ['user_id', 'ad_id', 'rating']):
        raise ValueError("Data must contain 'user_id', 'ad_id', and 'rating' columns")
    return df[['user_id', 'ad_id', 'rating']]

def train_ad_recommendation_model():
    df = fetch_interaction_data()
    df = preprocess_data(df)

    user_encoder = LabelEncoder()
    ad_encoder = LabelEncoder()

    df['user_id'] = user_encoder.fit_transform(df['user_id'])
    df['ad_id'] = ad_encoder.fit_transform(df['ad_id'])

    X = df[['user_id', 'ad_id']]
    y = df['rating']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    joblib.dump(model, 'ad_recommendation_model.joblib')
    joblib.dump(user_encoder, 'user_encoder.joblib')
    joblib.dump(ad_encoder, 'ad_encoder.joblib')
    print("Ad recommendation model trained and saved successfully.")

def recommend_ads(user_id, ad_ids):
    model = joblib.load('ad_recommendation_model.joblib')
    user_encoder = joblib.load('user_encoder.joblib')
    ad_encoder = joblib.load('ad_encoder.joblib')

    user_id_encoded = user_encoder.transform([user_id])[0]
    ad_ids_encoded = ad_encoder.transform(ad_ids)

    recommendations = []
    for ad_id in ad_ids_encoded:
        prediction = model.predict([[user_id_encoded, ad_id]])[0]
        recommendations.append({"ad_id": ad_encoder.inverse_transform([ad_id])[0], "predicted_rating": prediction})

    return recommendations
