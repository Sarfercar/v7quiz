import html
import unicodedata
from pathlib import Path

import pandas as pd
import requests
import streamlit as st


st.set_page_config(
    page_title="Volotea Destination Finder",
    page_icon="✈️",
    layout="centered",
)

# Volotea palette
COLOR_RED = "#E10E49"
COLOR_BROWN = "#452325"

st.markdown(
    f"""
    <style>
        html, body, [class*="css"] {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
        }}
        h1, h2, h3, h4 {{
            color: {COLOR_BROWN};
            font-weight: 800;
        }}
        .stButton > button {{
            background-color: {COLOR_RED} !important;
            color: white !important;
            border: none !important;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            font-weight: bold;
        }}
        .stButton > button:hover {{
            background-color: #b50b3a !important;
        }}
        .stLinkButton > a {{
            background-color: {COLOR_RED} !important;
            color: white !important;
            border: none !important;
            border-radius: 4px;
            font-weight: bold;
        }}
        .stLinkButton > a:hover {{
            background-color: #b50b3a !important;
            color: white !important;
        }}
        .recommendation-card {{
            border: 1px solid #ddd;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            background: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }}
        .destination-header {{
            font-size: 1.6rem;
            color: {COLOR_BROWN};
            font-weight: bold;
        }}
        .badge {{
            background-color: {COLOR_BROWN};
            color: white;
            padding: 0.2rem 0.6rem;
            font-size: 0.75rem;
            border-radius: 12px;
            margin-left: 0.3rem;
            display: inline-block;
        }}
        .notice {{
            background-color: #fcf8e3;
            border-left: 4px solid #f0ad4e;
            color: #8a6d3b;
            padding: 0.8rem;
            font-size: 0.85rem;
            margin-top: 1.5rem;
            border-radius: 4px;
        }}
        .cta-link {{
            text-decoration: none;
            color: white !important;
            transition: opacity 0.2s;
        }}
        .cta-link:hover {{
            opacity: 0.9;
            text-decoration: underline;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


# Header logo
logo_url = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/"
    "Volotea.svg/960px-Volotea.svg.png"
)

try:
    st.image(logo_url, width=180)
except Exception:
    st.subheader("Volotea")


# Load the destination catalogue from the same folder as this script.
# Passing the file's modification time into the cache key makes Streamlit
# reload the CSV when a newer version is deployed.
CSV_PATH = Path(__file__).resolve().parent / "destinations.csv"


@st.cache_data
def load_data(csv_path, modified_at):
    return pd.read_csv(csv_path, sep=";")


try:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Could not find {CSV_PATH.name} next to this script.")
    df = load_data(str(CSV_PATH), CSV_PATH.stat().st_mtime)
except Exception as error:
    st.error(f"Error loading catalogue data: {error}")
    df = pd.DataFrame()


def remove_accents(text):
    """Remove accents to provide a fallback search query."""
    normalized = unicodedata.normalize("NFD", str(text))
    return "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Mn"
    )


# Find destination images using Wikipedia's API
@st.cache_data(show_spinner=False)
def fetch_wikimedia_image(destination, country):
    destination = str(destination).split("(")[0].strip()
    country = str(country).strip()

    clean_destination = remove_accents(destination)
    clean_country = remove_accents(country)

    queries = [
        f"{destination}, {country}",
        destination,
        f"{clean_destination}, {clean_country}",
        clean_destination,
        f"{clean_destination} town",
    ]

    api_url = "https://en.wikipedia.org/w/api.php"
    headers = {
        "User-Agent": "VoloteaDestinationFinder/1.0 (https://www.volotea.com/)"
    }

    for query in queries:
        params = {
            "action": "query",
            "format": "json",
            "formatversion": 2,
            "generator": "search",
            "gsrsearch": query,
            "gsrnamespace": 0,
            "gsrlimit": 5,
            "prop": "pageimages",
            "piprop": "thumbnail",
            "pithumbsize": 600,
        }

        try:
            response = requests.get(
                api_url,
                params=params,
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()

            pages = response.json().get("query", {}).get("pages", [])

            for page in pages:
                image_url = page.get("thumbnail", {}).get("source")
                if image_url:
                    return image_url, "Wikipedia"

        except (requests.RequestException, ValueError):
            # Try the next search query if this request fails.
            continue

    return None, None


# Main interface
st.title("Inspirational Travel Quiz")
st.write(
    "Not sure where to go next? Tell us what you love and discover "
    "destinations that match your travel style and budget."
)

with st.form("quiz_form"):
    moods = st.multiselect(
        "What kind of trip are you in the mood for?",
        options=[
            "beach",
            "nature and mountains",
            "city break",
            "culture",
            "food",
            "islands",
            "relaxation",
        ],
        default=["culture"],
    )

    length = st.selectbox(
        "How much time do you have?",
        options=["2–3 days", "4–5 days", "a week or more"],
    )

    season = st.selectbox(
        "When would you like to travel?",
        options=["spring", "summer", "autumn", "winter", "any time"],
    )

    budget = st.selectbox(
        "What's your approximate budget?",
        options=["low", "medium", "high"],
    )

    submit = st.form_submit_button("Find my destinations")


if submit:
    if df.empty:
        st.error("The destination catalogue is empty or could not be loaded.")
    elif not moods:
        st.warning("Please select at least one trip category to begin!")
    else:
        results = []

        if length == "2–3 days":
            mapped_length = "2-3 days"
        elif length == "4–5 days":
            mapped_length = "4-5 days"
        else:
            mapped_length = "a week or more"

        for _, row in df.iterrows():
            score = 0
            reasons = []

            # Match interests
            destination_interests = [
                interest.strip()
                for interest in str(row.get("interests", "")).split("|")
                if interest.strip()
            ]
            matched_moods = [
                mood for mood in moods if mood in destination_interests
            ]

            if matched_moods:
                score += len(matched_moods) * 3
                reasons.append(
                    f"matches your interest in {', '.join(matched_moods)}"
                )

            # Match trip length
            destination_lengths = [
                item.strip()
                for item in str(row.get("trip_length", "")).split("|")
            ]
            if mapped_length in destination_lengths:
                score += 2
                reasons.append(f"ideal for a {length} trip")

            # Match season
            destination_seasons = [
                item.strip().lower()
                for item in str(row.get("seasons", "")).split("|")
            ]

            if season.lower() == "any time":
                score += 2
                reasons.append("great for flexible, any-time travel")
            elif season.lower() in destination_seasons:
                score += 2
                reasons.append(f"fits the {season} travel season")

            # Match budget
            destination_budget = str(
                row.get("budget_tier", "")
            ).strip().lower()

            if destination_budget == budget.lower():
                score += 1
                reasons.append(f"aligns with your {budget} budget choice")

            if score >= 4:
                results.append((score, row, reasons))

        results.sort(
            key=lambda result: (
                -result[0],
                str(result[1].get("destination_en", "")),
            )
        )
        top_matches = results[:3]

        if not top_matches:
            st.info(
                "No close matches were found. Try changing your trip "
                "preferences or selecting 'any time' for the season."
            )
        else:
            st.subheader("Your Curated Travel Recommendations")

            for score, row, reasons in top_matches:
                destination = str(row.get("destination_en", ""))
                country = str(row.get("country_en", ""))
                region = row.get("region_en", "")
                iata = str(row.get("iata", ""))
                description = str(row.get("description", ""))

                # Display a region only when it identifies an island destination.
                island_regions = {
                    "Canary Islands", "Balearic Islands", "Corsica",
                    "Greek Islands", "Crete", "Samos", "Sardinia",
                    "Sicily", "Lampedusa", "Pantelleria",
                }
                region_text = ""
                if pd.notna(region) and str(region).strip() in island_regions:
                    region_text = f" ({html.escape(str(region).strip())})"

                # Escape CSV values inserted into custom HTML.
                safe_destination = html.escape(destination)
                safe_country = html.escape(country)
                safe_iata = html.escape(iata)

                st.markdown(
                    f"""
                    <div class="recommendation-card">
                        <div class="destination-header">
                            {safe_destination}, {safe_country}{region_text}
                            <span class="badge">{safe_iata}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                image_url, attribution = fetch_wikimedia_image(
                    destination,
                    country,
                )

                if image_url:
                    try:
                        st.image(
                            image_url,
                            caption=f"Image source: {attribution}",
                            use_container_width=True,
                        )
                    except Exception:
                        st.info(
                            f"No image could be displayed for {destination}."
                        )
                else:
                    st.info(
                        f"No image is currently available for {destination}."
                    )

                st.markdown(f"**Why you'll love it:**\n\n{description}")

                reason_bullets = "\n".join(
                    f"- It {reason}." for reason in reasons
                )
                st.markdown(
                    f"**Why it matches your answers:**\n\n{reason_bullets}"
                )

                tags = [
                    tag.strip()
                    for tag in str(row.get("interests", "")).split("|")
                    if tag.strip()
                ]
                if tags:
                    st.write("Tags: " + " ".join(f"`{tag}`" for tag in tags))

                st.link_button(
                    "Check flights",
                    "https://www.volotea.com/",
                    help="Visit Volotea to check available flights.",
                )

                st.divider()

            st.markdown(
                f"""
                <div style="
                    background-color: {COLOR_RED};
                    color: white;
                    padding: 2rem;
                    text-align: center;
                    border-radius: 8px;
                    margin-top: 2rem;
                ">
                    <h2 style="margin: 0;">
                        <a
                            class="cta-link"
                            href="https://www.volotea.com/"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            Discover these destinations and more with Volotea
                        </a>
                    </h2>
                </div>
                """,
                unsafe_allow_html=True,
            )


# Footer
st.markdown(
    """
    <div class="notice">
        ⚠️ Inspiration prototype. Recommendations do not guarantee flight
        availability or prices.
    </div>
    """,
    unsafe_allow_html=True,
)
