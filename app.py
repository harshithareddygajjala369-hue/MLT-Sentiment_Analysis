import streamlit as st
import json
import os
import random
from textblob import TextBlob

# --- CONFIGURATION ---
DB_FILE = "product_database.json"

# --- DATA SEEDING (Differentiated per Product) ---
def seed_data():
    # Group products to give them unique overall sentiment profiles
    product_profiles = {
        "Positive": [
            "Apple iPhone 15 Pro", "Sony WH-1000XM5", "MacBook Air M3", 
            "Nintendo Switch OLED", "Apple AirPods Pro 2", "PlayStation 5", 
            "Logitech MX Master 3S", "Anker 737 Power Bank", "LG C3 OLED TV", "Kindle Paperwhite"
        ],
        "Neutral": [
            "Samsung Galaxy S24 Ultra", "Dell XPS 13", "Bose QC Ultra", 
            "Google Pixel 8 Pro", "Instant Pot Duo", "Fitbit Charge 6", 
            "Surface Pro 9", "Canon EOS R6 Mark II", "Sonos Beam Gen 2", "SteelSeries Arctis Nova"
        ],
        "Negative": [
            "Dyson V15 Detect", "GoPro Hero 12", "Razer BlackWidow V4", 
            "Philips Hue Kit", "Corsair Vengeance RAM", "WD Black SN850X SSD", 
            "Elgato Stream Deck", "Ember Mug 2", "Tesla Wall Connector", "Fitbit Luxe"
        ]
    }

    # Review Content Pools
    pos_pool = ["Absolutely incredible, best purchase ever!", "Works exactly as advertised.", "High quality build.", "Five stars, highly recommend."]
    neu_pool = ["It's okay, nothing special.", "Average product for the price.", "Decent quality.", "Does the job, but pricey."]
    neg_pool = ["Worst experience ever.", "Total waste of money.", "Very disappointed with the quality.", "Broke after a week."]

    db = {}
    for profile, products in product_profiles.items():
        for p in products:
            reviews = []
            count = random.randint(12, 15)
            for _ in range(count):
                # Bias the pool based on the assigned profile
                if profile == "Positive":
                    pool = random.choices([pos_pool, neu_pool], weights=[80, 20])[0]
                elif profile == "Neutral":
                    pool = random.choices([pos_pool, neu_pool, neg_pool], weights=[20, 60, 20])[0]
                else: # Negative
                    pool = random.choices([neg_pool, neu_pool], weights=[80, 20])[0]
                
                reviews.append({"review": random.choice(pool)})
            db[p] = reviews
    return db

def load_data():
    if not os.path.exists(DB_FILE):
        data = seed_data()
        with open(DB_FILE, "w") as f:
            json.dump(data, f)
        return data
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def get_prediction_score(text):
    return TextBlob(text).sentiment.polarity

# --- NAVIGATION ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

st.set_page_config(page_title="AI Product Hub", layout="wide")
data = load_data()

# --- HOME PAGE ---
if st.session_state.page == 'home':
    st.title("🤖 AI Product Insight Hub")
    st.subheader("Analyze product reputations with automated sentiment tracking.")
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("### 🔍 Browse & Overall Analysis")
        if st.button("Explore Catalog", use_container_width=True):
            st.session_state.page = 'browse'
            st.rerun()
    with col2:
        st.success("### ✍️ Add a Review")
        if st.button("Write a Review", use_container_width=True):
            st.session_state.page = 'add'
            st.rerun()

# --- BROWSE PAGE ---
elif st.session_state.page == 'browse':
    if st.button("⬅️ Back to Home"):
        st.session_state.page = 'home'
        st.rerun()
    
    st.header("Search & Overall Analysis")
    selected_prod = st.selectbox("Select a Product:", sorted(data.keys()))
    reviews = data[selected_prod]

    # --- AGGREGATED SENTIMENT LOGIC ---
    st.subheader(f"📊 Overall Consensus for {selected_prod}")
    if st.button("Analyze Overall Sentiment", use_container_width=True):
        if reviews:
            total_score = sum(get_prediction_score(r['review']) for r in reviews)
            avg_score = total_score / len(reviews)
            
            if avg_score > 0.15:
                st.success(f"### Overall Verdict: POSITIVE 😊")
                st.write("Customers are highly satisfied with this product.")
            elif avg_score < -0.15:
                st.error(f"### Overall Verdict: NEGATIVE 😠")
                st.write("Customers generally have complaints or bad experiences.")
            else:
                st.warning(f"### Overall Verdict: NEUTRAL 😐")
                st.write("The sentiment is mixed or indifferent.")
        else:
            st.info("No reviews available.")

    st.divider()
    st.write(f"**Customer Reviews ({len(reviews)}):**")
    for r in reversed(reviews):
        with st.container(border=True):
            st.write(f"\"{r['review']}\"")

# --- ADD PAGE ---
elif st.session_state.page == 'add':
    if st.button("⬅️ Back to Home"):
        st.session_state.page = 'home'
        st.rerun()
    
    st.header("Contribute Feedback")
    with st.form("add_form"):
        p_name = st.text_input("Product Name").strip()
        r_content = st.text_area("Your Review")
        if st.form_submit_button("Save & Submit"):
            if p_name and r_content:
                if p_name not in data: data[p_name] = []
                data[p_name].append({"review": r_content})
                save_data(data)
                st.success("Review Saved!")
                st.balloons()
            else:
                st.error("Please fill in all fields.")
