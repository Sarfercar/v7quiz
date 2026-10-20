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
