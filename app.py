import pickle
import streamlit as st
import requests

movies = pickle.load(open('model/movie_list.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))

def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url).json()
        poster_path = data.get('poster_path')
        return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Image"
    except:
        return "https://via.placeholder.com/500x750?text=Error"

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(enumerate(similarity[index]), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))
    return recommended_movie_names, recommended_movie_posters

st.set_page_config(page_title="🍿 PopFlix - Smart Movie Recommender", layout="wide")

st.markdown("""
    <h1 style='text-align: center; color: #e50914;'>🎬 PopFlix</h1>
    <h4 style='text-align: center;'>Because scrolling for 45 minutes is a real horror movie.</h4>
    <p style='text-align: center;'>Pick a movie you love, and PopFlix will recommend 5 others you might enjoy — complete with posters, using real-time data from TMDB.</p>
    <hr>
""", unsafe_allow_html=True)

selected_movie = st.selectbox("🎥 Choose a movie you like:", movies['title'].values)

if st.button('🔍 Get Recommendations'):
    names, posters = recommend(selected_movie)
    st.markdown("### 🎯 Here are 5 movies you might enjoy:")
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.image(posters[i], use_column_width=True)
            st.caption(names[i])

st.markdown("---")
st.markdown("""
    <div style="text-align: center;">
        <h5>💡 Powered by Machine Learning & TMDB</h5>
        <p>Using content-based filtering and cosine similarity to recommend movies based on plot, genre, cast, and more.</p>
    </div>
""", unsafe_allow_html=True)
