"""
Command line runner for the Music Recommender Simulation.

Loads songs from CSV, scores them against multiple user profiles,
and prints ranked recommendations with explanations.
Supports multiple scoring modes and a diversity penalty.
"""

from src.recommender import load_songs, recommend_songs, SCORING_MODES, get_max_score


PROFILES = {
    "High-Energy Pop Fan": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "valence": 0.85,
        "danceability": 0.8,
        "likes_acoustic": False,
        "preferred_decade": "2020s",
        "mood_tags": ["euphoric", "uplifting"],
        "instrumentalness": 0.15,
        "lyricalness": 0.80,
    },
    "Chill Lofi Listener": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "valence": 0.6,
        "danceability": 0.55,
        "likes_acoustic": True,
        "preferred_decade": "2020s",
        "mood_tags": ["dreamy", "peaceful"],
        "instrumentalness": 0.80,
        "lyricalness": 0.10,
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.9,
        "valence": 0.4,
        "danceability": 0.6,
        "likes_acoustic": False,
        "preferred_decade": "2010s",
        "mood_tags": ["aggressive", "powerful"],
        "instrumentalness": 0.30,
        "lyricalness": 0.65,
    },
    "Conflicting: High Energy + Melancholy": {
        "genre": "folk",
        "mood": "melancholy",
        "energy": 0.95,
        "valence": 0.2,
        "danceability": 0.3,
        "likes_acoustic": True,
        "mood_tags": ["nostalgic", "bittersweet"],
        "instrumentalness": 0.35,
        "lyricalness": 0.75,
    },
    "Edge Case: Acoustic Classical Romantic": {
        "genre": "classical",
        "mood": "romantic",
        "energy": 0.2,
        "valence": 0.7,
        "danceability": 0.3,
        "likes_acoustic": True,
        "preferred_decade": "1990s",
        "mood_tags": ["peaceful", "warm"],
        "instrumentalness": 0.90,
        "lyricalness": 0.05,
    },
}


# ---------------------------------------------------------------------------
# Challenge 4: ASCII table formatting
# ---------------------------------------------------------------------------

def table_row(rank, title, artist, score, max_s, reasons, width=90):
    """Formats a single recommendation as table rows."""
    title_col = f"{title} — {artist}"
    if len(title_col) > 38:
        title_col = title_col[:35] + "..."
    score_col = f"{score:.2f}/{max_s:.1f}"
    return (f"  {rank:<4} {title_col:<38} {score_col:<10}",
            f"       {reasons}")


def print_table(name: str, prefs: dict, songs: list,
                mode: str = "balanced", diversity: bool = False) -> None:
    max_s = get_max_score(mode)
    recommendations = recommend_songs(prefs, songs, k=5, mode=mode, diversity=diversity)

    label = f"  {name}"
    if mode != "balanced":
        label += f"  [mode: {mode}]"
    if diversity:
        label += "  [diversity ON]"

    print(f"\n{'=' * 90}")
    print(label)
    print(f"  genre={prefs['genre']}, mood={prefs['mood']}, energy={prefs['energy']}, "
          f"tags={prefs.get('mood_tags', [])}")
    print("-" * 90)
    print(f"  {'#':<4} {'Song':<38} {'Score':<10}")
    print("-" * 90)

    for rank, (song, score, explanation) in enumerate(recommendations, 1):
        row, reasons = table_row(rank, song["title"], song["artist"], score, max_s, explanation)
        print(row)
        print(reasons)

    print("=" * 90)


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs with {len(songs[0])} features each\n")

    # --- Section 1: Standard balanced mode ---
    print("#" * 90)
    print("  BALANCED MODE (default weights)")
    print("#" * 90)
    for name, prefs in PROFILES.items():
        print_table(name, prefs, songs, mode="balanced")

    # --- Section 2: Compare scoring modes on one profile ---
    print("\n" + "#" * 90)
    print("  SCORING MODE COMPARISON — High-Energy Pop Fan")
    print("#" * 90)
    pop_prefs = PROFILES["High-Energy Pop Fan"]
    for mode in SCORING_MODES:
        print_table(f"Pop Fan", pop_prefs, songs, mode=mode)

    # --- Section 3: Diversity penalty demo ---
    print("\n" + "#" * 90)
    print("  DIVERSITY PENALTY DEMO — Chill Lofi Listener")
    print("#" * 90)
    lofi_prefs = PROFILES["Chill Lofi Listener"]
    print_table("Without diversity", lofi_prefs, songs, mode="balanced", diversity=False)
    print_table("With diversity", lofi_prefs, songs, mode="balanced", diversity=True)


if __name__ == "__main__":
    main()
