import streamlit as st
from src.recommender import load_songs, recommend_songs, SCORING_MODES, get_max_score

st.set_page_config(page_title="VibeFinder 1.0", page_icon="🎵", layout="wide")

# Load data once
@st.cache_data
def get_songs():
    return load_songs("data/songs.csv")

songs = get_songs()
all_genres = sorted(set(s["genre"] for s in songs))
all_moods = sorted(set(s["mood"] for s in songs))
all_tags = sorted(set(tag for s in songs for tag in s.get("mood_tags", [])))
all_decades = sorted(set(s["release_decade"] for s in songs))

# --- Header ---
st.title("🎵 VibeFinder 1.0")
st.caption("A content-based music recommender simulation")

# --- Sidebar: User Profile ---
st.sidebar.header("Your Taste Profile")

genre = st.sidebar.selectbox("Favorite Genre", all_genres, index=all_genres.index("pop"))
mood = st.sidebar.selectbox("Favorite Mood", all_moods, index=all_moods.index("happy"))
energy = st.sidebar.slider("Target Energy", 0.0, 1.0, 0.8, 0.05)
valence = st.sidebar.slider("Target Valence", 0.0, 1.0, 0.75, 0.05)
danceability = st.sidebar.slider("Target Danceability", 0.0, 1.0, 0.7, 0.05)
likes_acoustic = st.sidebar.checkbox("Prefer Acoustic", value=False)
preferred_decade = st.sidebar.selectbox("Preferred Decade", [""] + all_decades, index=0)
mood_tags = st.sidebar.multiselect("Mood Tags", all_tags, default=["euphoric", "uplifting"])
instrumentalness = st.sidebar.slider("Target Instrumentalness", 0.0, 1.0, 0.3, 0.05)
lyricalness = st.sidebar.slider("Target Lyricalness", 0.0, 1.0, 0.7, 0.05)

st.sidebar.divider()
st.sidebar.header("Settings")
mode = st.sidebar.selectbox("Scoring Mode", list(SCORING_MODES.keys()), index=0)
diversity = st.sidebar.checkbox("Enable Diversity Penalty", value=False)
k = st.sidebar.slider("Number of Results", 1, 20, 5)

user_prefs = {
    "genre": genre,
    "mood": mood,
    "energy": energy,
    "valence": valence,
    "danceability": danceability,
    "likes_acoustic": likes_acoustic,
    "preferred_decade": preferred_decade,
    "mood_tags": mood_tags,
    "instrumentalness": instrumentalness,
    "lyricalness": lyricalness,
}

# --- Results ---
results = recommend_songs(user_prefs, songs, k=k, mode=mode, diversity=diversity)
max_score = get_max_score(mode)

st.subheader(f"Top {k} Recommendations — {mode} mode")
if diversity:
    st.info("Diversity penalty is ON — repeated artists/genres get penalized.")

for rank, (song, score, explanation) in enumerate(results, 1):
    pct = score / max_score
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f"**#{rank} — {song['title']}** by {song['artist']}")
        st.progress(min(pct, 1.0))
        tags_display = " ".join(f"`{t}`" for t in song.get("mood_tags", []))
        st.caption(
            f"{song['genre']} · {song['mood']} · energy {song['energy']} · "
            f"{song['release_decade']} · pop {song['popularity']} · {tags_display}"
        )

    with col2:
        st.metric("Score", f"{score:.2f}", f"/ {max_score:.1f}")

    with st.expander("Why this song?"):
        for reason in explanation.split(", "):
            st.markdown(f"- {reason}")

    st.divider()

# --- Full catalog ---
with st.expander("📋 Full Song Catalog"):
    import pandas as pd
    df = pd.DataFrame(songs)
    df["mood_tags"] = df["mood_tags"].apply(lambda t: ", ".join(t))
    st.dataframe(df, use_container_width=True, hide_index=True)
