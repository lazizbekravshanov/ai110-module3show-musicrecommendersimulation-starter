import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Song:
    """Represents a song and its attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 50
    release_decade: str = "2020s"
    mood_tags: List[str] = field(default_factory=list)
    instrumentalness: float = 0.5
    lyricalness: float = 0.5


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


# ---------------------------------------------------------------------------
# Scoring modes (Challenge 2)
# ---------------------------------------------------------------------------

SCORING_MODES = {
    "balanced": {
        "w_genre": 3.0, "w_mood": 2.0, "w_energy": 1.5,
        "w_valence": 1.0, "w_dance": 0.5, "w_acoustic": 0.5,
        "w_popularity": 0.5, "w_decade": 0.5, "w_mood_tags": 1.0,
        "w_instrumentalness": 0.3, "w_lyricalness": 0.3,
    },
    "genre-first": {
        "w_genre": 5.0, "w_mood": 1.5, "w_energy": 1.0,
        "w_valence": 0.5, "w_dance": 0.3, "w_acoustic": 0.3,
        "w_popularity": 0.3, "w_decade": 0.3, "w_mood_tags": 0.5,
        "w_instrumentalness": 0.2, "w_lyricalness": 0.2,
    },
    "mood-first": {
        "w_genre": 1.5, "w_mood": 4.0, "w_energy": 1.5,
        "w_valence": 1.5, "w_dance": 0.5, "w_acoustic": 0.3,
        "w_popularity": 0.3, "w_decade": 0.3, "w_mood_tags": 2.0,
        "w_instrumentalness": 0.3, "w_lyricalness": 0.3,
    },
    "energy-focused": {
        "w_genre": 1.0, "w_mood": 1.0, "w_energy": 4.0,
        "w_valence": 1.0, "w_dance": 1.5, "w_acoustic": 0.3,
        "w_popularity": 0.3, "w_decade": 0.2, "w_mood_tags": 0.5,
        "w_instrumentalness": 0.2, "w_lyricalness": 0.2,
    },
}


def get_max_score(mode: str = "balanced") -> float:
    """Returns the theoretical max score for a given mode."""
    weights = SCORING_MODES[mode]
    return round(sum(weights.values()), 2)


# ---------------------------------------------------------------------------
# OOP scoring (used by Recommender class / tests)
# ---------------------------------------------------------------------------

def score_song_obj(user: UserProfile, song: Song) -> Tuple[float, List[str]]:
    """Scores a Song dataclass against a UserProfile, returning (score, reasons)."""
    score = 0.0
    reasons: List[str] = []

    if song.genre.lower() == user.favorite_genre.lower():
        score += 3.0
        reasons.append("genre match (+3.0)")

    if song.mood.lower() == user.favorite_mood.lower():
        score += 2.0
        reasons.append("mood match (+2.0)")

    energy_pts = round(1.5 * (1.0 - abs(song.energy - user.target_energy)), 2)
    score += energy_pts
    reasons.append(f"energy proximity (+{energy_pts})")

    valence_pts = round(1.0 * (1.0 - abs(song.valence - 0.5)), 2)
    score += valence_pts
    reasons.append(f"valence proximity (+{valence_pts})")

    dance_pts = round(0.5 * (1.0 - abs(song.danceability - 0.5)), 2)
    score += dance_pts
    reasons.append(f"danceability proximity (+{dance_pts})")

    if (song.acousticness >= 0.6) == user.likes_acoustic:
        score += 0.5
        reasons.append("acoustic match (+0.5)")

    return round(score, 2), reasons


class Recommender:
    """OOP implementation of the recommendation logic."""
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k songs ranked by score for the given user profile."""
        scored = [(song, score_song_obj(user, song)[0]) for song in self.songs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable explanation of why a song was recommended."""
        score, reasons = score_song_obj(user, song)
        return f"Score: {score:.2f} — " + ", ".join(reasons)


# ---------------------------------------------------------------------------
# Functional CSV loader
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from a CSV file and returns a list of dictionaries with proper types."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            song = {
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"].strip().lower(),
                "mood": row["mood"].strip().lower(),
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
                "popularity": int(row.get("popularity", 50)),
                "release_decade": row.get("release_decade", "2020s").strip(),
                "mood_tags": [t.strip().lower() for t in row.get("mood_tags", "").split("|") if t.strip()],
                "instrumentalness": float(row.get("instrumentalness", 0.5)),
                "lyricalness": float(row.get("lyricalness", 0.5)),
            }
            songs.append(song)
    return songs


# ---------------------------------------------------------------------------
# Functional scoring (Challenge 1 + Challenge 2)
# ---------------------------------------------------------------------------

def score_song(user_prefs: Dict, song: Dict, mode: str = "balanced",
               **weight_overrides) -> Tuple[float, List[str]]:
    """Scores a song dict against user preferences using the given mode."""
    weights = {**SCORING_MODES.get(mode, SCORING_MODES["balanced"]), **weight_overrides}
    score = 0.0
    reasons: List[str] = []

    # Genre match
    if song["genre"] == user_prefs.get("genre", "").lower():
        score += weights["w_genre"]
        reasons.append(f"genre match (+{weights['w_genre']})")

    # Mood match
    if song["mood"] == user_prefs.get("mood", "").lower():
        score += weights["w_mood"]
        reasons.append(f"mood match (+{weights['w_mood']})")

    # Energy proximity
    target_energy = user_prefs.get("energy", 0.5)
    energy_pts = round(weights["w_energy"] * (1.0 - abs(song["energy"] - target_energy)), 2)
    score += energy_pts
    reasons.append(f"energy (+{energy_pts})")

    # Valence proximity
    target_valence = user_prefs.get("valence", 0.5)
    valence_pts = round(weights["w_valence"] * (1.0 - abs(song["valence"] - target_valence)), 2)
    score += valence_pts
    reasons.append(f"valence (+{valence_pts})")

    # Danceability proximity
    target_dance = user_prefs.get("danceability", 0.5)
    dance_pts = round(weights["w_dance"] * (1.0 - abs(song["danceability"] - target_dance)), 2)
    score += dance_pts
    reasons.append(f"dance (+{dance_pts})")

    # Acoustic match
    is_acoustic = song["acousticness"] >= 0.6
    if is_acoustic == user_prefs.get("likes_acoustic", False):
        score += weights["w_acoustic"]
        reasons.append(f"acoustic (+{weights['w_acoustic']})")

    # --- NEW FEATURES (Challenge 1) ---

    # Popularity bonus: scale 0-100 linearly into weight
    pop = song.get("popularity", 50)
    pop_pts = round(weights["w_popularity"] * (pop / 100.0), 2)
    score += pop_pts
    reasons.append(f"popularity (+{pop_pts})")

    # Decade match: +full weight if song decade matches user pref, else 0
    pref_decade = user_prefs.get("preferred_decade", "")
    if pref_decade and song.get("release_decade", "") == pref_decade:
        score += weights["w_decade"]
        reasons.append(f"decade match (+{weights['w_decade']})")

    # Mood tags: award partial credit for each matching tag
    user_tags = set(user_prefs.get("mood_tags", []))
    song_tags = set(song.get("mood_tags", []))
    if user_tags and song_tags:
        overlap = len(user_tags & song_tags)
        total = len(user_tags)
        tag_pts = round(weights["w_mood_tags"] * (overlap / total), 2)
        if tag_pts > 0:
            score += tag_pts
            matched = ", ".join(user_tags & song_tags)
            reasons.append(f"mood tags [{matched}] (+{tag_pts})")

    # Instrumentalness proximity
    target_inst = user_prefs.get("instrumentalness", 0.5)
    inst_pts = round(weights["w_instrumentalness"] * (1.0 - abs(song.get("instrumentalness", 0.5) - target_inst)), 2)
    score += inst_pts
    reasons.append(f"instrumental (+{inst_pts})")

    # Lyricalness proximity
    target_lyr = user_prefs.get("lyricalness", 0.5)
    lyr_pts = round(weights["w_lyricalness"] * (1.0 - abs(song.get("lyricalness", 0.5) - target_lyr)), 2)
    score += lyr_pts
    reasons.append(f"lyrical (+{lyr_pts})")

    return round(score, 2), reasons


# ---------------------------------------------------------------------------
# Recommendation with diversity penalty (Challenge 3)
# ---------------------------------------------------------------------------

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5,
                    mode: str = "balanced", diversity: bool = False,
                    artist_penalty: float = 2.0, genre_penalty: float = 1.0,
                    **weight_overrides) -> List[Tuple[Dict, float, str]]:
    """Scores all songs and returns the top k as (song, score, explanation) tuples.

    When diversity=True, songs are picked greedily: after selecting each song,
    remaining candidates from the same artist or genre get a score penalty.
    """
    scored = []
    for song in songs:
        total, reasons = score_song(user_prefs, song, mode=mode, **weight_overrides)
        scored.append({"song": song, "base_score": total, "reasons": reasons, "penalty": 0.0})

    if not diversity:
        scored.sort(key=lambda x: x["base_score"], reverse=True)
        return [(s["song"], s["base_score"], ", ".join(s["reasons"])) for s in scored[:k]]

    # Greedy diversity selection
    results: List[Tuple[Dict, float, str]] = []
    seen_artists: Dict[str, int] = {}
    seen_genres: Dict[str, int] = {}

    for _ in range(min(k, len(scored))):
        # Compute effective scores with penalties
        for item in scored:
            artist = item["song"]["artist"]
            genre = item["song"]["genre"]
            item["penalty"] = (seen_artists.get(artist, 0) * artist_penalty
                               + seen_genres.get(genre, 0) * genre_penalty)

        scored.sort(key=lambda x: x["base_score"] - x["penalty"], reverse=True)

        pick = scored.pop(0)
        effective = round(pick["base_score"] - pick["penalty"], 2)
        explanation = ", ".join(pick["reasons"])
        if pick["penalty"] > 0:
            explanation += f" [diversity penalty -{pick['penalty']}]"

        results.append((pick["song"], effective, explanation))

        # Track what we've already picked
        seen_artists[pick["song"]["artist"]] = seen_artists.get(pick["song"]["artist"], 0) + 1
        seen_genres[pick["song"]["genre"]] = seen_genres.get(pick["song"]["genre"], 0) + 1

    return results
