import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import json
import os
import matplotlib.pyplot as plt

def run_analysis(log_file):
    """
    Performs EDA and Linear Regression on the usage log file.
    Saves a plot demonstrating the model performance.
    """
    if not os.path.exists(log_file) or os.stat(log_file).st_size == 0:
        return {"status": "error", "details": f"Log file '{log_file}' is empty or does not exist."}

    # --- Step 4: Exploratory Data Analysis (EDA) ---
    
    # 1. Data Collection & Loading
    data = []
    with open(log_file, 'r') as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                continue # Skip invalid lines

    df = pd.DataFrame(data)
    
    # Filter for successful question queries for latency analysis
    df_questions = df[(df['type'] == 'question') & (df['success'] == True)].copy()

    if df_questions.shape[0] < 5:
        return {"status": "error", "details": f"Not enough successful question entries ({df_questions.shape[0]}) for analysis."}
    
    # 2. Descriptive Statistics
    desc_stats = {
        "mean_latency_seconds": df_questions['duration'].mean(),
        "median_latency_seconds": df_questions['duration'].median(),
        "mean_query_length": df_questions['query_length'].mean(),
        "max_query_length": df_questions['query_length'].max()
    }
    
    # 3. Visualization (EDA) - Histogram of Latency
    plt.figure(figsize=(8, 5))
    df_questions['duration'].plot(kind='hist', bins=10, edgecolor='black', color='#004a99')
    plt.title('Distribution of AI Response Latency (seconds)')
    plt.xlabel('Duration (s)')
    plt.ylabel('Frequency')
    plt.savefig('eda_latency_distribution.png')
    plt.close()

    # --- Step 5 & 6: Modeling (Linear Regression) & Evaluation ---
    
    # Objective: Predict Response Time (Latency) based on Query Length
    X = df_questions[['query_length']]  # Independent Variable (Feature)
    y = df_questions['duration']        # Dependent Variable (Target)

    # 1. Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # 2. Train Model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # 3. Predict and Evaluate
    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    # 4. Visualization (Model Performance)
    plt.figure(figsize=(10, 6))
    plt.scatter(X_test, y_test, color='#004a99', label='Actual Latency')
    plt.plot(X_test, y_pred, color='red', linewidth=2, label=f'Regression Line ($R^2$: {r2:.2f})')
    plt.title('Linear Regression: Query Length vs. AI Latency')
    plt.xlabel('Query Length (Characters)')
    plt.ylabel('Response Duration (Seconds)')
    plt.legend()
    plt.savefig('regression_performance.png')
    plt.close()
    
    # 5. Summary of Results
    model_results = {
        "model": "Linear Regression",
        "feature": "Query Length",
        "target": "Response Duration (Latency)",
        "r_squared": r2,
        "mean_squared_error": mse,
        "coefficient (slope)": model.coef_[0],
        "intercept": model.intercept_
    }

    # Returns results for the Flask route response
    return {
        "Descriptive Statistics": desc_stats,
        "Model Results": model_results,
        "Visualization_EDA": "eda_latency_distribution.png",
        "Visualization_Model": "regression_performance.png"
    }

if __name__ == '__main__':
    # Example usage: Ensure you have a usage_log.jsonl file before running directly
    print("Running analysis module standalone...")
    results = run_analysis('usage_log.jsonl')
    print(json.dumps(results, indent=4))