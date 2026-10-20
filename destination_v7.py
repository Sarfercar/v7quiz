import streamlit as st
import pandas as pd
import requests
import urllib.parse
import unicodedata

st.set_page_config(
    page_title="Volotea Destination Finder",
    page_icon="✈️",
    layout="centered"
)

# Volotea Palette
COLOR_RED = "#E10E49"
COLOR_BROWN = "#452325"

# Apply CSS for Custom Font/Coloring to closely follow Volotea identity guidelines
st.markdown(f"""
    <style>
        html, body, [class*="css"] {{ font-family: 'Helvetica Neue', Arial, sans-serif; }}
        h1, h2, h3, h4 {{ color: {COLOR_BROWN}; font-weight: 800; }}
        .stButton>button {{ background-color: {COLOR_RED} !important; color: white !important; border: none !important; border-radius: 4px; padding: 0.5rem 1rem; font-weight: bold; }}
        .stButton>button:hover {{ background-color: #b50b3a !important; }}
        .recommendation-card {{ border: 1px solid #ddd; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
        .destination-header {{ font-size: 1.6rem; color: {COLOR_BROWN}; font-weight: bold; margin-bottom: 0.2rem; }}
        .badge {{ background-color: {COLOR_BROWN}; color: white; padding: 0.2rem 0.6rem; font-size: 0.75rem; border-radius: 12px; margin-right: 0.3rem; display: inline-block; }}
        .notice {{ background-color: #fcf8e3; border-left: 4px solid #f0ad4e; color: #8a6d3b; padding: 0.8rem; font-size: 0.85rem; margin-top: 1.5rem; border-radius: 4px; }}
        .cta-link {{ text-decoration: none; color: white !important; transition: opacity 0.2s; }}
        .cta-link:hover {{ opacity: 0.9; text-decoration: underline; }}
    </style>
""", unsafe_allow_html=True)

# Logo Header helper
logo_url = "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/98/Volotea.svg/960px-Volotea.svg.png"
try:
    st.image(logo_url, width=180)
except:
    st.subheader("Volotea")

# Load CSV safely with fallback handler
@st.cache_data
def load_data():
    try:
        return pd.read_csv("destinations.csv", sep=";")
    except Exception as e:
        st.error(f"Error loading catalogue data: {e}")
        return pd.DataFrame()

df = load_data()

# Upgraded Unicode-safe Image fetcher with multi-stage original-vs-clean fallback
@st.cache_data(show_spinner=False)
def fetch_wikimedia_image(destination, country):
    # Keep original format
    orig_dest = destination.split("(")[0].strip()
    orig_country = country.strip()

    # Standardize string format and remove special non-ASCII accents (e.g. "A Coruña" -> "A Coruna")
    def clean_unicode(text):
        return "".join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

    clean_dest = clean_unicode(orig_dest)
    clean_country = clean_unicode(orig_country)

    # Multi-stage fallback search query list
    queries = [
        f"{orig_dest}, {orig_country}",
        f"{orig_dest}",
        f"{clean_dest}, {clean_country}",
        f"{clean_dest}",
        f"{clean_dest} town"
    ]

    for query in queries:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "pageimages",
            "generator": "search",
            "gsrsearch": query,
            "gsrlimit": 1,
            "piprop": "thumbnail",
            "pithumbsize": 600,
            "utf8": 1
        }
        try:
            res = requests.get(url, params=params, timeout=5.0).json()
            pages = res.get("query", {}).get("pages", {})
            for pid, page in pages.items():
                thumb = page.get("thumbnail", {})
                if thumb.get("source"):
                    return thumb["source"], "Wikimedia Commons"
        except:
            pass
    return None, None

# Main Interface
st.title("Inspirational Travel Quiz")
st.write("Not sure where to go next? Tell us what you love and discover destinations that match your travel style and budget.")

with st.form("quiz_form"):
    moods = st.multiselect(
        "What kind of trip are you in the mood for?",
        options=["beach", "nature and mountains", "city break", "culture", "food", "islands", "relaxation"],
        default=["culture"]
    )

    length = st.selectbox(
        "How much time do you have?",
        options=["2–3 days", "4–5 days", "a week or more"]
    )

    season = st.selectbox(
        "When would you like to travel?",
        options=["spring", "summer", "autumn", "winter", "any time"]
    )

    budget = st.selectbox(
        "What's your approximate budget?",
        options=["low", "medium", "high"]
    )

    submit = st.form_submit_button("Find my destinations")

if submit:
    if not moods:
        st.warning("Please select at least one trip category to begin!")
    else:
        # Matching scoring engine
        results = []
        mapped_len = "2-3 days" if "2–3" in length else ("4-5 days" if "4-5" in length else "a week or more")

        for _, row in df.iterrows():
            score = 0
            matches_reasons = []

            # Compare Mood/Interests
            dest_interests = str(row['interests']).split('|')
            matched_moods = list(set(moods).intersection(dest_interests))
            if matched_moods:
                score += len(matched_moods) * 3
                matches_reasons.append(f"matches your interest in {', '.join(matched_moods)}")

            # Match Length
            dest_lengths = str(row['trip_length']).split('|')
            if mapped_len in dest_lengths:
                score += 2
                matches_reasons.append(f"ideal for a {length} trip")

            # Match Season
            dest_seasons = str(row['seasons']).split('|')
            if season.lower() == "any time" or season.lower() in dest_seasons:
                score += 2
                matches_reasons.append(f"perfectly fits {season} travel season" if season.lower() != "any time" else "great for flexible any-time travel")

            # Match budget tier
            if row['budget_tier'] == budget.lower():
                score += 1
                matches_reasons.append(f"aligns with your choice of {budget} budget category")

            if score >= 4:
                results.append((score, row, matches_reasons))

        # Sort deterministically
        results.sort(key=lambda x: (-x[0], x[1]['destination_en']))
        top_matches = results[:3]

        if not top_matches:
            st.info("No perfect match was found matching all specific parameters. Try adjusting your mood or selecting 'any time' for the season to find more matches!")
        else:
            st.subheader("Your Curated Travel Recommendations")
            for score, row, reasons in top_matches:
                dest_name = row['destination_en']
                country = row['country_en']
                region = row['region_en']
                iata = row['iata']
                desc = row['description']

                region_str = f" ({region})" if pd.notna(region) and region else ""

                st.markdown(f"""
                <div class='recommendation-card'>
                    <div class='destination-header'>{dest_name}, {country}{region_str} <span class='badge'>{iata}</span></div>
                </div>
                """, unsafe_allow_html=True)

                # Handle Photos gracefully
                img_url, attribution = fetch_wikimedia_image(dest_name, country)
                if img_url:
                    st.image(img_url, caption=f"Image Credit: {attribution if attribution else 'Public Domain'}", use_container_width=True)
                else:
                    st.info(f"📤 Scenic preview of {dest_name} (Image loader currently offline)")

                st.markdown(f"**Why you'll love it:**\n{desc}")

                reasons_bullet_points = "\n".join([f"* It {reason}." for reason in reasons])
                st.markdown(f"**Why it matches your answers:**\n{reasons_bullet_points}")

                # Tag display
                st.write("Tags: " + " ".join([f"`{t}`" for t in str(row['interests']).split('|')]))

                # Check flights logic
                st.button("Check flights", key=f"chk_{iata}", help=f"Flight connection details: Volotea services {iata}. Please select your custom departure airport from the homepage to check timetables.")
                st.divider()

            # Clean Brand CTA block with integrated click-through title link
            st.markdown(f"""
            <div style='background-color:{COLOR_RED}; color:white; padding:2rem; text-align:center; border-radius:8px; margin-top:2rem;'>
                <h2 style='margin:0;'>
                    <a class='cta-link' href='https://volotea.com/' target='_blank'>Find your next getaway with Volotea</a>
                </h2>
            </div>
            """, unsafe_allow_html=True)

# Footer Notice
st.markdown("""
<div class='notice'>
    ⚠️ Inspiration prototype. Recommendations do not guarantee flight availability or prices.
</div>
""", unsafe_allow_html=True)
