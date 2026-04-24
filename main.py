import pandas as pd
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset
movies = pd.read_csv("movies.csv")

# Keep only required columns
movies = movies[['id', 'title', 'overview', 'genre']]

# Fill missing values
movies['overview'] = movies['overview'].fillna('')
movies['genre'] = movies['genre'].fillna('')

# Create tags (overview + genre)
movies['tags'] = movies['overview'] + " " + movies['genre']

# TF-IDF Vectorizer
tfidf = TfidfVectorizer(max_features=5000, stop_words='english')
vector = tfidf.fit_transform(movies['tags'].values.astype('U')).toarray()

# Cosine similarity
similarity = cosine_similarity(vector)

# Save model
pickle.dump(movies, open('movies_list.pkl', 'wb'))
pickle.dump(similarity, open('similarity.pkl', 'wb'))

# Recommendation function
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommend_movie = []
    for i in distance[1:11]:
        recommend_movie.append(movies.iloc[i[0]].title)
    return recommend_movie

# Accuracy Evaluation (Precision@5 with genres)
def evaluate_recommender(movies, sample_size=200, k=5):
    correct, total = 0, 0
    sampled_movies = movies.sample(min(sample_size, len(movies)), random_state=42)
    for _, row in sampled_movies.iterrows():
        try:
            recs = recommend(row['title'])
            true_genres = set(row['genre'].split())
            for rec in recs:
                rec_genres = set(movies[movies['title'] == rec]['genre'].values[0].split())
                if len(true_genres & rec_genres) > 0:  # if at least one genre matches
                    correct += 1
                total += 1
        except:
            continue
    return correct / total if total > 0 else 0

# Run evaluation
accuracy = evaluate_recommender(movies, sample_size=200, k=5)
print(f"TF-IDF Model Accuracy (Precision@5): {accuracy:.2f}")
