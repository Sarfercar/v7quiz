# Specification · Volotea Destination Finder

## 1. Problem and User
* **Who has the problem:** A traveler looking for getaway inspiration from Volotea's destination catalog, wanting a quick and easy way to discover matching locations based on their current mood, available time, travel season, and budget tier, without having to enter specific flight route schedules or departure airports first.
* **How they solve it today:** Browsing massive travel portals, dealing with complex flight search forms that demand exact departure cities, and manually cross-referencing trip ideas with their budget and preferred activities.
* **What annoys them today:** Rigid search tools that focus on logistics (origins, specific dates, prices) instead of inspiration, causing information overload and analytical fatigue before a destination is even selected.
* **What part is solved by this application:** The app filters Volotea's offline catalog of 141 destinations to suggest up to three highly curated recommendations that align with the user's qualitative preferences. Real-time airline scheduling, seat availability, and dynamic pricing calculations are explicitly out of scope.

## 2. What the Product Does
1. **Inspiration Quiz:** A simple, responsive, four-question form capturing the user's travel mood (beach, culture, nature, etc.), duration, target season, and budget tier.
2. **Deterministic Recommendation Matcher:** An internal scoring algorithm matching user inputs against an offline database, avoiding real-time API latency or external search dependencies.
3. **Volotea-Branded Recommendation Cards:** Cards displaying the recommended destination (formatted as `City, Country`), the unique matching reasons, relevant tags, representative Wikimedia Commons imagery, and a call-to-action to check flight options.

## 3. Inputs and Outputs
* **User Inputs:** Selection of multiple moods/interests, trip duration, preferred season, and qualitative budget category.
* **App Outputs:** 1 to 3 deterministic recommendation cards detailing the suggested destination, IATA code, regional hierarchy, visual reference, "Why you'll love it" narrative, and "Why it matches your answers" explanations.
* **Example:**
  * *Input:* Mood: `beach, islands`, Duration: `a week or more`, Season: `summer`, Budget: `high`.
  * *Output:* `Ibiza, Spain` (Balearic Islands) [IBZ] and `Mykonos, Greece` (Greek Islands) [JMK] accompanied by corresponding Wikimedia images, custom matching logic justifications, and a "Check flights" prompt.

## 4. The Algorithm & Image Integration (Non-LLM Variant)
* **Matching Engine:** Features an offline rules-based catalog mapping (`destinations.csv`) with translated values, categorized trip profiles, and tags. Scores match quality out of 8 points:
  * Mood Matches: Up to 3 points (3 points per intersecting interest).
  * Duration Matches: 2 points.
  * Season Matches: 2 points.
  * Budget Matches: 1 point.
* **Image Integration:** Dynamic, non-authenticated requests to the Wikimedia Commons API using the format `Destination, Country`. Employs smart, memory-efficient caching (`st.cache_data`) and soft image loading fallbacks to protect the UI layout in offline environments.

## 5. User Flow
1. The user launches the app and views a cleanly styled header showcasing the Volotea brand identity, followed by a streamlined quiz.
2. The user selects their ideal vacation criteria and submits the form.
3. The interface renders the top-scoring matched destinations with dynamic images, structured matching justifications, and primary external connection links to Volotea's booking platform.

## 6. Constraints
* **Zero Cost:** No paid API keys, premium databases, or active user authentication steps are permitted.
* **Offline Capabilities:** No real-time data lookups required except for optional destination photo fetches.
* **Design Guidelines:** Implements the official Volotea brand colors (Primary Red `#E10E49`, Secondary Brown `#452325`, clean white backgrounds, and bold condensed headings).

## 7. Acceptance Criteria

| Input Scenario | Expected Outcome |
| :--- | :--- |
| **Standard Input:** Consistent parameters (e.g., standard beach holiday preferences) | Displays 1 to 3 highly matching destinations with rich text copy and corresponding images. |
| **Extreme / Contradictory Input:** (e.g., a highly specific nature winter vacation with zero overlapping items) | Returns a friendly, informative screen noting that no destinations fully match, inviting the user to relax criteria to find more options. |
| **Network Interruption:** Wikimedia Commons API times out or blocks requests | Destination recommendation card renders successfully using an elegant, clean placeholder fallback with the destination name. |

## 8. Out of Scope
* Live flight connection mapping, seat maps, calendar pricing lookups, or flight status trackers.
* Dynamic user profile creation, session saves, or booking transaction systems.

## 9. Deployment
* **Platform:** Hosted directly on Streamlit Community Cloud.
* **Repository Structure:** Single owner repository containing `destination_v7.py`, `destinations.csv`, `requirements.txt`, `README.md`, `AGENTS.md`, and `SPECIFICATION.md`.