import json
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="AI Model Evaluation Benchmark",
    page_icon="🧪",
    layout="wide"
)


# -----------------------------
# Load results
# -----------------------------

with open("results.json", "r", encoding="utf-8") as file:
    results = json.load(file)

df = pd.DataFrame(results)


# -----------------------------
# Header
# -----------------------------

st.title("🧪 AI Model Evaluation Benchmark")

st.markdown(
    """
    Interactive evaluation dashboard for analyzing model responses
    across reasoning, coding, mathematics, knowledge, instruction
    following, and hallucination resistance.
    """
)


# -----------------------------
# Overall metrics
# -----------------------------

benchmark_df = df[df["category"] != "development"]

total_tests = len(benchmark_df)
passed = (benchmark_df["result"] == "PASS").sum()
failed = (benchmark_df["result"] == "FAIL").sum()

overall_score = benchmark_df["score"].mean()


col1, col2, col3, col4 = st.columns(4)

col1.metric("Benchmark Tests", total_tests)
col2.metric("Passed", passed)
col3.metric("Failed", failed)
col4.metric("Overall Score", f"{overall_score:.2%}")


# -----------------------------
# Category performance
# -----------------------------

st.header("📊 Category Performance")

category_df = (
    benchmark_df
    .groupby("category")["score"]
    .mean()
    .reset_index()
)

category_df["score"] = category_df["score"] * 100

st.bar_chart(
    category_df.set_index("category")["score"]
)


# -----------------------------
# Test results
# -----------------------------

st.header("🔍 Test Results")

display_df = benchmark_df[
    [
        "id",
        "category",
        "difficulty",
        "evaluation_type",
        "result",
        "score"
    ]
].copy()

display_df["score"] = display_df["score"].apply(
    lambda x: f"{x:.0%}"
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# -----------------------------
# Test explorer
# -----------------------------

st.header("🧩 Test Explorer")

selected_test = st.selectbox(
    "Select a test",
    benchmark_df["id"].tolist()
)

selected = benchmark_df[
    benchmark_df["id"] == selected_test
].iloc[0]


st.subheader(selected["id"])

st.write("**Category:**", selected["category"])
st.write("**Difficulty:**", selected["difficulty"])
st.write("**Evaluation Type:**", selected["evaluation_type"])

st.markdown("### Question")
st.write(selected["question"])

st.markdown("### Expected Answer")
st.write(selected["expected_answer"])

st.markdown("### Model Response")

st.code(
    selected["model_response"],
    language="python"
)

st.markdown("### Evaluation Result")

if selected["result"] == "PASS":
    st.success(
        f"PASS — Score: {selected['score']:.0%}"
    )
else:
    st.error(
        f"FAIL — Score: {selected['score']:.0%}"
    )