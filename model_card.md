# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

This recommender suggests 5 songs from a small 20-song catalog based on a user's preferred genre, mood, energy level, and other taste attributes. It is designed for classroom exploration only — not for real users or production deployment. It demonstrates how content-based filtering works by comparing song attributes against a user profile and ranking by weighted similarity.

**Non-intended use:** This system should not be used to make real music recommendations for actual listeners. The catalog is too small (20 songs), the scoring weights are hand-tuned rather than learned from data, and there is no feedback loop to correct mistakes. It should not be used to draw conclusions about real listener behavior, and it should not be embedded in any product or service.

---

## 3. How the Model Works

The system looks at each song in the catalog and asks: "How close is this song to what the user wants?" It checks six things:

1. **Genre** — Does the song's genre exactly match the user's favorite? This is the heaviest factor (worth 3.0 points) because genre is usually the strongest signal of taste.
2. **Mood** — Does the song's mood (happy, chill, intense, etc.) match? Worth 2.0 points.
3. **Energy** — How close is the song's energy level to what the user prefers? A song at exactly the right energy gets full points (1.5); the further away, the fewer points.
4. **Valence** — How close is the song's emotional positiveness to the user's target? Worth up to 1.0 point.
5. **Danceability** — How close is the song's danceability to the user's preference? Worth up to 0.5 points.
6. **Acousticness** — Does the song's acoustic character match the user's preference? A binary check worth 0.5 points.

The maximum possible score is 8.5 points. After scoring every song, the system sorts them from highest to lowest and returns the top 5.

---

## 4. Data

The catalog contains **20 songs** in `data/songs.csv`, spanning 15 genres (pop, lofi, rock, jazz, ambient, synthwave, indie pop, hip-hop, folk, electronic, classical, metal, latin, r&b, country) and 10 moods (happy, chill, intense, relaxed, moody, focused, melancholy, energetic, angry, romantic).

The dataset was expanded from an original 10-song starter to provide more genre diversity. However, some genres have only 1 song (rock, jazz, classical, metal, etc.) while pop and lofi have 3 each. This imbalance means some user profiles have very few relevant options. The data reflects a curated selection, not real listening data — it does not capture the breadth of any real music platform.

---

## 5. Strengths

- **Pop and lofi profiles get excellent results.** For the "High-Energy Pop Fan," Sunrise City scored 8.45/8.50 — a near-perfect match. The "Chill Lofi Listener" got Library Rain at 8.49/8.50. When the catalog has multiple songs in the user's genre, the system differentiates well.
- **Scoring is transparent.** Every recommendation includes a reason breakdown, so users can see exactly why a song was chosen. This makes the system easy to audit and explain.
- **The system correctly distinguishes between profiles.** The Rock fan gets Storm Runner (#1), the Lofi listener gets Library Rain (#1), and the Pop fan gets Sunrise City (#1) — each profile produces different, sensible results.

---

## 6. Limitations and Bias

- **Genre dominance creates a filter bubble.** At 3.0 points, genre match is so heavy that a song outside the user's preferred genre almost never cracks the top 3, even if it matches mood, energy, and everything else perfectly. For the "Acoustic Classical Romantic" profile, the #1 result (Moonlit Sonata) doesn't even match the user's mood ("romantic" vs "relaxed") — but it wins because genre alone is worth more than mood + acoustic combined.
- **Conflicting preferences expose system rigidity.** The "High Energy + Melancholy" profile wants folk (low-energy genre) but energy=0.95. The system still ranks the low-energy folk song #1 because genre+mood (5.0 pts) overwhelms the energy mismatch penalty. A real user with this profile would probably want intense folk-rock, which doesn't exist in our catalog.
- **Single-song genres get no variety.** A classical fan will always get Moonlit Sonata as #1 with no alternatives. The system cannot diversify within underrepresented genres.
- **No cross-genre discovery.** The system cannot learn that "people who like lofi also tend to like ambient" — it treats each genre as an isolated category. A lofi fan might enjoy Spacewalk Thoughts (ambient/chill), but it can never rank higher than the lofi songs.
- **Binary acoustic preference is too coarse.** A user who "somewhat" likes acoustic music is treated identically to one who exclusively listens to it.

---

## 7. Evaluation

**Profiles tested:**

| Profile | Top Result | Score | Intuition Check |
|---------|-----------|-------|-----------------|
| High-Energy Pop Fan | Sunrise City (pop/happy) | 8.45 | Feels right — upbeat pop hit |
| Chill Lofi Listener | Library Rain (lofi/chill) | 8.49 | Perfect — exactly the vibe |
| Deep Intense Rock | Storm Runner (rock/intense) | 8.37 | Correct — high-energy rock |
| High Energy + Melancholy (adversarial) | Autumn Letters (folk/melancholy) | 7.32 | Surprising — low-energy song tops a high-energy request |
| Acoustic Classical Romantic (edge case) | Moonlit Sonata (classical/relaxed) | 6.39 | Reasonable genre pick, but mood mismatch |

**Weight experiment (genre halved to 1.5, energy doubled to 3.0):**

The most notable change was for the "Conflicting: High Energy + Melancholy" profile. With default weights, Autumn Letters (energy=0.30) ranked #1 at 7.32 despite the user wanting energy=0.95. With doubled energy weight, Autumn Letters dropped to 6.34 and Burning Asphalt (energy=0.97) jumped from #3 to #3 at 4.29 — still not #1 because genre+mood still outweighed energy, but the gap narrowed significantly.

For the Pop profile, Rooftop Lights (indie pop/happy) jumped from #4 to #2 in the experiment, overtaking Cloud Nine and Gym Hero. This is because with reduced genre weight, the mood match (+2.0) plus high energy proximity became more competitive than genre match alone. The system started recommending more by "feel" than by label.

**Key takeaway:** The default weights produce genre-locked recommendations. Reducing genre weight opens up cross-genre discovery but risks recommending songs that don't match the user's core identity.

---

## 8. Future Work

- **Add multi-genre preferences** — let users specify 2-3 genres instead of one, reducing the filter bubble.
- **Diversity penalty** — after picking the top result, slightly penalize songs that are too similar to it, so the top 5 aren't all from the same genre.
- **Tempo scoring** — `tempo_bpm` is in the data but unused. Adding it could help distinguish "intense rock" (150+ BPM) from "intense hip-hop" (96 BPM).
- **Collaborative filtering** — with multiple user profiles, the system could learn that "users who like lofi also tend to like ambient," enabling cross-genre recommendations.
- **Configurable weights via CLI** — let users adjust genre/mood/energy importance at runtime to explore how weight changes affect results.

---

## 9. Personal Reflection

All tests passing which felt good to see after all the refactoring:

```
$ pytest tests/ -v
============================= test session starts ==============================
platform darwin -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: /Users/kali/ai110-module3show-musicrecommendersimulation-starter
collecting ... collected 2 items

tests/test_recommender.py::test_recommend_returns_songs_sorted_by_score PASSED [ 50%]
tests/test_recommender.py::test_explain_recommendation_returns_non_empty_string PASSED [100%]

============================== 2 passed in 0.00s ===============================
```

Honestly the biggest thing I took away from this project is how much one number can change everything. The genre weight was 3.0 and that felt totally fine when I first set it up, but then when I actually tested it I realized the system basicaly never recommends anything outside your genre. Like even if a song matches your mood and energy perfectly, it still loses to a genre match that dosent fit anything else. Thats kind of crazy when you think about it — one weight is the diffrence between a system that helps you discover stuff and one that just keeps showing you the same type of music.

Using AI tools was super helpful for the boring parts like generating the csv data and getting the output formatted nicely. But I had to actually think through the scoring logic myself. The AI wanted to do simple if/else for numeric features at first and I had to push it toward the proximity based scoring which made way more sense. Also when I ran the weight experiement I had to double check the math myself because the AI wrote the code fine but I needed to make sure halving genre was actually testing what I wanted.

The thing that suprised me the most was how real the recommendations felt even tho its literally just 6 rules and 20 songs. When Sunrise City came back as the top pick for the pop/happy profile at 8.45 points it genuinly felt like a solid recommendation. Not because the algorithm is smart or anything but because matching on genre + mood + energy captures enough of what "taste" means to be convincing. It made me think that real recommender systems like Spotify probably aren't doing anything magical, they just have way more data to work with.

If I kept working on this I'd want to add genre similarity so that folk and indie are treated as closer together than folk and metal. The adversarial profile really showed this gap — if someone wants high energy melancholy folk, a human would think of intense folk-rock, but the system just picks the calmest folk song it can find becuase it has no concept of blending genres. I'd also add some kind of diversity thing so the top 5 results arent all from the exact same genre.
