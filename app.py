import pandas as pd
import requests
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image

# ==== Streamlit Page Config ====
st.set_page_config(page_title="🎬 PopFlix", layout="wide")

# ==== Load and Display Logo ====
logo = Image.open("logo.png")  # ✅ Updated image name
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image(logo, width=200)  # Adjust width if needed
st.markdown("</div>", unsafe_allow_html=True)

# ==== Title and Tagline ====
st.title("🍿 PopFlix")
st.markdown("Because scrolling for 45 minutes is a real horror movie.")
st.markdown("Just pick a movie you love, and PopFlix will suggest five similar films — complete with posters and titles.")

# ==== TMDB Poster Fetching ====
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url).json()
        poster_path = data.get('poster_path')
        return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Image"
    except:
        return "https://via.placeholder.com/500x750?text=Error"

# ==== Load Data ====
@st.cache_data
def load_data():
    df = pd.read_csv("movies.csv")
    df = df[['id', 'title', 'genres', 'keywords', 'cast', 'director', 'overview']]
    df.dropna(inplace=True)
    df['tags'] = df['overview'] + " " + df['genres'] + " " + df['keywords'] + " " + df['cast'] + " " + df['director']
    df['tags'] = df['tags'].str.lower()
    return df

# ==== Compute Similarity Matrix ====
@st.cache_data
def get_similarity_matrix(data):
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vector_matrix = cv.fit_transform(data['tags']).toarray()
    similarity = cosine_similarity(vector_matrix)
    return similarity

# ==== Movie Recommendation Logic ====
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(enumerate(similarity[index]), key=lambda x: x[1], reverse=True)[1:6]
    recommended_movies = []
    posters = []
    for i in distances:
        movie_id = movies.iloc[i[0]].id
        recommended_movies.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))
    return recommended_movies, posters

# ==== App Logic ====
movies = load_data()
similarity = get_similarity_matrix(movies)

selected_movie = st.selectbox("🎥 Select a movie you like:", movies['title'].values)

if st.button("✨ Recommend"):
    names, posters = recommend(selected_movie)
    st.subheader("💡 You may also like:")
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.image(posters[i], use_container_width=True)
            st.caption(names[i])
