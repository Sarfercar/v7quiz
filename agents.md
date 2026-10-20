# AGENTS.md · Volotea Destination Finder

Instructions for AI Agents (Cursor, Copilot, Gemini CLI, etc.): Strictly follow the guidelines in this file before modifying any code.

## What this project is
A functional Streamlit travel companion prototype inspired by Volotea's visual identity. It recommends up to three personalized travel destinations from Volotea's official catalog based on an interactive inspiration quiz, without asking for departure inputs.

## How it is built
- **Python 3.10+**
- **Frontend Interface:** Streamlit (with embedded CSS custom styling utilizing Volotea's brand palette: Red `#E10E49` and Brown `#452325`).
- **Data Sources:** Self-contained `destinations.csv` with English translations, curated editorial tags, and description match rules. No external paid databases, services, or flight network graphs are utilized.
- **Image Integration:** Dynamic, non-API-key-dependent retrieval using the official Wikimedia Commons Search API with failover caching and graceful layout recovery fallback.
- **Dependencies:** Maintained in `requirements.txt`.

## Rules
1. **Design Integrity:** Maintain the strict Volotea-inspired color system (Red for Call-to-Actions, Brown for titles and body texts). Maintain a clean, white background with professional, mobile-friendly spacing.
2. **No Airfare/Route Guarantees:** The recommendations are inspirational matches. The app must never state or imply specific ticket prices, schedule availability, or fixed routes from an imaginary origin.
3. **Deterministic Logic:** Result sorting must remain fully deterministic on Streamlit reruns. Do not randomize selection arrays.
4. **No API Keys or Secrets:** Keep the execution completely independent of developer accounts, paid subscriptions, or sensitive environment tokens.
5. **Interface Language:** All user-facing components must remain strictly in concise, natural, and engaging English.

## How to verify it works
- Run `streamlit run destination_v7.py` locally or inside Google Colab using a LocalTunnel connection.
- **Test Cases:**
  - Select `beach`, `islands`, `summer`, and `high` budget -> App returns up to three iconic holiday spots (e.g., Mykonos, Ibiza) with corresponding pictures and valid matches.
  - Set contradictory filters where no matches score >= 4 -> The app displays a friendly notice inviting the user to adjust their choices instead of loading weak suggestions.

## What not to do
- Do not delete or rewrite this `AGENTS.md` file without asking.
- Do not integrate user logins, tracking, or persistent databases.
- Do not auto-inject airline clichés like floating clouds, animated maps, or complex booking flow simulations.
