import pandas as pd
import requests
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
import base64

# ==== Streamlit Page Config ====
st.set_page_config(page_title="PopFlix", layout="wide")

# ==== Convert Logo to Base64 ====
def get_base64_img(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# ==== Load & Encode Logo ====
logo_base64 = get_base64_img("logo.png")

# ==== Display Header ====
st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: center; margin-top: 10px;">
        <img src="data:image/png;base64,{logo_base64}" style="height: 140px; margin-right: 10px;" />
        <h1 style="font-size: 64px; margin: 0;">PopFlix</h1>
    </div>
""", unsafe_allow_html=True)

# ==== Tagline ====
st.markdown("""
    <p style='text-align: center; font-size: 24px; margin-top: 10px;'>
        Because scrolling for 45 minutes is a real horror movie.
    </p>
    <p style='text-align: center; font-size: 20px;'>
        Just pick a movie you love — and PopFlix will suggest five similar films, complete with posters and titles.
    </p>
""", unsafe_allow_html=True)

# ==== Fetch Poster from TMDB ====
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url).json()
        poster_path = data.get('poster_path')
        return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Image"
    except:
        return "https://via.placeholder.com/500x750?text=Error"

# ==== Load Dataset ====
@st.cache_data
def load_data():
    df = pd.read_csv("movies.csv")
    df = df[['id', 'title', 'genres', 'keywords', 'cast', 'director', 'overview']]
    df.dropna(inplace=True)
    df['tags'] = df['overview'] + " " + df['genres'] + " " + df['keywords'] + " " + df['cast'] + " " + df['director']
    df['tags'] = df['tags'].str.lower()
    return df

# ==== Similarity Matrix ====
@st.cache_data
def get_similarity_matrix(data):
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vector_matrix = cv.fit_transform(data['tags']).toarray()
    similarity = cosine_similarity(vector_matrix)
    return similarity

# ==== Recommendation Logic ====
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

# ==== Main Interface ====
movies = load_data()
similarity = get_similarity_matrix(movies)
# ==== Inject CSS for Netflix-style Animation ====
st.markdown("""
    <style>
    @keyframes fadeInUp {
      0% { opacity: 0; transform: translateY(30px); }
      100% { opacity: 1; transform: translateY(0); }
    }

    .recommend-grid {
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      gap: 30px;
      margin-top: 30px;
    }

    .movie-card {
      background-color: #1b1b1b;
      border-radius: 16px;
      overflow: hidden;
      text-align: center;
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      width: 180px;
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.6);
      animation: fadeInUp 0.8s ease forwards;
      opacity: 0;
    }

    .movie-card:hover {
      transform: translateY(-10px) scale(1.05);
      box-shadow: 0 12px 30px rgba(229, 9, 20, 0.5);
    }

    .movie-card img {
      width: 100%;
      height: 270px;
      object-fit: cover;
      border-bottom: 2px solid #e50914;
    }

    .movie-card h4 {
      margin: 10px 0 15px;
      color: #e50914;
      font-size: 1.05rem;
    }
    </style>
""", unsafe_allow_html=True)
selected_movie = st.selectbox("🎥 Select a movie you like:", movies['title'].values)

if st.button("✨ Recommend"):
    names, posters = recommend(selected_movie)
    st.subheader("💡 You may also like:")
    html_cards = '<div class="recommend-grid">'
    for i in range(5):
        html_cards += f"""
            <div class="movie-card" style="animation-delay: {0.2 + i * 0.2}s;">
                <img src="{posters[i]}" alt="{names[i]}">
                <h4>{names[i]}</h4>
            </div>
        """
    html_cards += '</div>'
    st.markdown(html_cards, unsafe_allow_html=True)
