import pandas as pd
import requests
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="🎬 PopFlix", layout="wide")

st.title("🍿 PopFlix")
st.markdown("Because scrolling for 45 minutes is a real horror movie.")
st.markdown("Just pick a movie you love, and PopFlix will suggest five similar films — complete with posters and titles.")

def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url).json()
        poster_path = data.get('poster_path')
        return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Image"
    except:
        return "https://via.placeholder.com/500x750?text=Error"

@st.cache_data
def load_data():
    df = pd.read_csv("movies.csv")
    df = df[['id', 'title', 'genres', 'keywords', 'cast', 'director', 'overview']]
    df.dropna(inplace=True)
    df['tags'] = df['overview'] + " " + df['genres'] + " " + df['keywords'] + " " + df['cast'] + " " + df['director']
    df['tags'] = df['tags'].str.lower()
    return df

@st.cache_data
def get_similarity_matrix(data):
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vector_matrix = cv.fit_transform(data['tags']).toarray()
    similarity = cosine_similarity(vector_matrix)
    return similarity

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

movies = load_data()
similarity = get_similarity_matrix(movies)

selected_movie = st.selectbox("🎥 Select a movie you like:", movies['title'].values)

if st.button("✨ Recommend"):
    names, posters = recommend(selected_movie)
    st.subheader("💡 You may also like:")
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.image(posters[i], use_column_width=True)
            st.caption(names[i])

with st.expander("📌 Project Highlights"):
    st.markdown("""
- 🔍 *Content-Based Filtering*: Uses movie overviews and metadata (genres, keywords, etc.) to compute similarities.
- 📐 *Cosine Similarity*: Quantifies how close two movies are in terms of their content.
- 🎥 *TMDB Dataset*: Real-world data including titles, overviews, cast, crew, genres, and more.
- ⚡ *Fast & Accurate* recommendations in real-time.
    """)

with st.expander("🧠 How It Works"):
    st.markdown("""
1. *Preprocessing*: Cleans and merges relevant movie data.  
2. *Feature Engineering*: Creates a combined string of keywords, genres, cast, director, etc.  
3. *Vectorization*: Uses CountVectorizer to convert text to vectors.  
4. *Similarity Scoring*: Computes cosine similarity between movie vectors.  
5. *Recommendation*: Returns top 5 similar movies based on your selection.
    """)

with st.expander("📁 Dataset Used"):
    st.markdown("[TMDB Movie Metadata on Kaggle](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata?resource=download)")

with st.expander("🛠 Built With"):
    st.markdown("Python, Pandas, NumPy, Scikit-learn, TMDB Dataset, Streamlit")
        <p>Using content-based filtering and cosine similarity to recommend movies based on plot, genre, cast, and more.</p>
    </div>
""", unsafe_allow_html=True)
