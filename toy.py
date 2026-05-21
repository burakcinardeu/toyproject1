import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from pathlib import Path

# ==============================
# AI-Supported Fraud Decision Prototype
# Master Thesis Experiment Prototype
# ==============================

st.set_page_config(
    page_title="AI-Supported Fraud Decision Study",
    page_icon="🤖",
    layout="centered"
)

RESULTS_FILE = Path("results_fraud_reliance.csv")

# ------------------------------
# Example scenarios
# Later, these can be replaced with cases derived from a public fraud dataset.
# ------------------------------
SCENARIOS = [
    {
        "scenario_id": "S01",
        "amount": "€1,850",
        "time": "02:14 AM",
        "location": "Germany",
        "device": "New device",
        "failed_logins": "3",
        "ground_truth": "Fraud",
        "ai_recommendation": "Fraud",
        "explanation": "The transaction occurred at an unusual time, from a new device, with multiple failed login attempts.",
        "confidence": "86%"
    },
    {
        "scenario_id": "S02",
        "amount": "€42",
        "time": "14:20 PM",
        "location": "Germany",
        "device": "Known device",
        "failed_logins": "0",
        "ground_truth": "Not Fraud",
        "ai_recommendation": "Not Fraud",
        "explanation": "The transaction amount is low, the device is known, and there are no failed login attempts.",
        "confidence": "91%"
    },
    {
        "scenario_id": "S03",
        "amount": "€920",
        "time": "23:48 PM",
        "location": "Foreign country",
        "device": "New device",
        "failed_logins": "1",
        "ground_truth": "Fraud",
        "ai_recommendation": "Fraud",
        "explanation": "The transaction shows multiple risk indicators, including a new device and unusual location.",
        "confidence": "78%"
    },
    {
        "scenario_id": "S04",
        "amount": "€310",
        "time": "11:05 AM",
        "location": "Germany",
        "device": "Known device",
        "failed_logins": "0",
        "ground_truth": "Not Fraud",
        "ai_recommendation": "Fraud",
        "explanation": "The system detected a moderate transaction amount and flagged it as potentially unusual.",
        "confidence": "62%"
    },
    {
        "scenario_id": "S05",
        "amount": "€2,400",
        "time": "03:25 AM",
        "location": "Foreign country",
        "device": "New device",
        "failed_logins": "4",
        "ground_truth": "Fraud",
        "ai_recommendation": "Fraud",
        "explanation": "The transaction combines several high-risk indicators: high amount, foreign location, new device, and failed logins.",
        "confidence": "93%"
    },
    {
        "scenario_id": "S06",
        "amount": "€75",
        "time": "18:45 PM",
        "location": "Germany",
        "device": "Known device",
        "failed_logins": "0",
        "ground_truth": "Not Fraud",
        "ai_recommendation": "Not Fraud",
        "explanation": "The transaction pattern appears consistent with normal customer behavior.",
        "confidence": "88%"
    }
]

TRANSPARENCY_CONDITIONS = [
    "No transparency",
    "Explanation",
    "Explanation + confidence"
]

# ------------------------------
# Helper functions
# ------------------------------
def initialize_session():
    if "participant_id" not in st.session_state:
        st.session_state.participant_id = str(uuid.uuid4())[:8]
    if "scenario_index" not in st.session_state:
        st.session_state.scenario_index = 0
    if "condition" not in st.session_state:
        # For this prototype, one condition is assigned per participant.
        # Later, this can be randomized more systematically.
        st.session_state.condition = TRANSPARENCY_CONDITIONS[hash(st.session_state.participant_id) % len(TRANSPARENCY_CONDITIONS)]
    if "completed" not in st.session_state:
        st.session_state.completed = False


def classify_reliance(user_decision, ai_recommendation, ground_truth):
    ai_correct = ai_recommendation == ground_truth
    user_followed_ai = user_decision == ai_recommendation

    if ai_correct and user_followed_ai:
        return "Appropriate reliance"
    elif (not ai_correct) and user_followed_ai:
        return "Over-reliance"
    elif ai_correct and (not user_followed_ai):
        return "Under-reliance"
    else:
        return "Appropriate non-reliance"


def save_response(row):
    df = pd.DataFrame([row])
    if RESULTS_FILE.exists():
        df.to_csv(RESULTS_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(RESULTS_FILE, mode="w", header=True, index=False)


# ------------------------------
# App
# ------------------------------
initialize_session()

st.title("AI-Supported Fraud Decision Study")

if st.session_state.completed:
    st.success("Thank you for participating in this study.")
    st.write("Your responses have been recorded anonymously.")
    st.stop()

# Intro screen
if st.session_state.scenario_index == 0:
    with st.expander("Study information", expanded=True):
        st.write(
            "In this study, you will evaluate transaction scenarios. "
            "For each case, an AI recommendation will be shown. "
            "Your task is to decide whether the transaction is fraudulent or not."
        )
        st.write("Your responses will be stored anonymously for academic research purposes.")
        st.write(f"Assigned transparency condition: **{st.session_state.condition}**")

scenario = SCENARIOS[st.session_state.scenario_index]

st.subheader(f"Scenario {st.session_state.scenario_index + 1} of {len(SCENARIOS)}")

st.markdown("### Transaction details")
st.write(f"**Amount:** {scenario['amount']}")
st.write(f"**Time:** {scenario['time']}")
st.write(f"**Location:** {scenario['location']}")
st.write(f"**Device:** {scenario['device']}")
st.write(f"**Failed login attempts:** {scenario['failed_logins']}")

st.markdown("### AI recommendation")
st.info(f"AI recommendation: **{scenario['ai_recommendation']}**")

if st.session_state.condition in ["Explanation", "Explanation + confidence"]:
    st.write(f"**Explanation:** {scenario['explanation']}")

if st.session_state.condition == "Explanation + confidence":
    st.write(f"**Confidence:** {scenario['confidence']}")

st.markdown("### Your decision")
user_decision = st.radio(
    "Do you think this transaction is fraudulent?",
    options=["Fraud", "Not Fraud"],
    index=None
)

trust_score = st.slider(
    "How much do you trust the AI recommendation in this case?",
    min_value=1,
    max_value=7,
    value=4,
    help="1 = do not trust at all, 7 = trust completely"
)

understanding_score = st.slider(
    "How understandable was the AI recommendation?",
    min_value=1,
    max_value=7,
    value=4,
    help="1 = not understandable, 7 = very understandable"
)

if st.button("Submit and continue"):
    if user_decision is None:
        st.warning("Please select Fraud or Not Fraud before continuing.")
    else:
        reliance_type = classify_reliance(
            user_decision=user_decision,
            ai_recommendation=scenario["ai_recommendation"],
            ground_truth=scenario["ground_truth"]
        )

        row = {
            "timestamp": datetime.now().isoformat(),
            "participant_id": st.session_state.participant_id,
            "scenario_id": scenario["scenario_id"],
            "condition": st.session_state.condition,
            "ground_truth": scenario["ground_truth"],
            "ai_recommendation": scenario["ai_recommendation"],
            "user_decision": user_decision,
            "user_followed_ai": user_decision == scenario["ai_recommendation"],
            "ai_correct": scenario["ai_recommendation"] == scenario["ground_truth"],
            "reliance_type": reliance_type,
            "trust_score": trust_score,
            "understanding_score": understanding_score
        }

        save_response(row)

        st.session_state.scenario_index += 1
        if st.session_state.scenario_index >= len(SCENARIOS):
            st.session_state.completed = True
        st.rerun()
