import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from io import StringIO

# -- PAGE CONFIG --
st.set_page_config(page_title="Linear Regression Predictor", layout="centered")

# -- TITLE --
st.title("📚 Test Score Predictor using Linear Regression")

st.markdown("Predict a student's test score based on hours studied. Optionally enter their actual score to track accuracy! 📊")

# -- INITIAL DATA --
X = np.array([1, 2, 3, 4, 5])
y = np.array([50, 60, 65, 70, 80])
X_b = np.c_[np.ones((X.shape[0], 1)), X]
y = y.reshape(-1, 1)

# -- NORMAL EQUATION --
theta_best = np.linalg.inv(X_b.T.dot(X_b)).dot(X_b.T).dot(y)

# -- SESSION STATE FOR PREDICTION HISTORY --
if "history" not in st.session_state:
    st.session_state.history = []

# -- USER INPUTS --
student_name = st.text_input("👤 Enter Student Name", placeholder="e.g. Arya Sharma")
hours = st.slider("⏱️ Select Hours Studied", 0.0, 10.0, 5.0, 0.5)
actual_score = st.number_input("🎯 Enter Actual Test Score (optional)", min_value=0.0, max_value=100.0, step=0.5, format="%.2f")

# -- PREDICT BUTTON --
if st.button("📈 Predict Score"):
    if student_name.strip() == "":
        st.warning("Please enter a student name.")
    else:
        X_new = np.array([[1, hours]])
        predicted_score = float(X_new.dot(theta_best)[0][0])
        
        # Cap the predicted score at 100
        predicted_score = max(predicted_score, 100.0)
        
        # Calculate prediction error if actual provided
        error = round(actual_score - predicted_score, 2) if actual_score else None
        
        # Save to history
        st.session_state.history.append({
            "Student": student_name.title(),
            "Hours Studied": hours,
            "Predicted Score": round(predicted_score, 2),
            "Actual Score": actual_score if actual_score else None,
            "Error": error
        })

        st.success(f"🎯 Predicted Score: **{predicted_score:.2f}**")
        if actual_score:
            st.info(f"📉 Prediction Error: `{error}` (Actual - Predicted)")

# -- DISPLAY TABLE --
if st.session_state.history:
    st.subheader("📊 Prediction History")
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True)

    # -- DOWNLOAD AS CSV --
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Prediction History as CSV",
        data=csv,
        file_name='prediction_history.csv',
        mime='text/csv'
    )

    # -- PLOT SECTION --
    st.subheader("📉 Regression Plot")
    fig, ax = plt.subplots()

    # Original data
    ax.scatter(X, y, color='blue', label='Training Data')

    # Regression line
    X_line = np.array([[1, i] for i in range(0, 11)])
    y_line = X_line.dot(theta_best)
    ax.plot(range(0, 11), y_line, color='red', label='Regression Line')

    # Plot user predictions
    for row in st.session_state.history:
        ax.scatter(row["Hours Studied"], row["Predicted Score"], s=100, label=row["Student"])

    ax.set_xlabel("Hours Studied")
    ax.set_ylabel("Test Score")
    ax.legend(loc="lower right")
    ax.grid(True)

    st.pyplot(fig)
