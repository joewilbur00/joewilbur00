# Earnings Call Sentiment and Volatility Analysis

This notebook analyzes the relationship between earnings call sentiment and stock volatility. It combines FinBERT sentiment scores and topic features to build a predictive classifier.

## Key Components
- Created a dataset including text from earnings calls and stock data surrounding earnings call dates using yfinance
- Extracted FinBERT sentiment scores from earnings calls
- Combined with topic model features from LDA
- Built a Random Forest model to classify volatility risk

## Purpose
To evaluate whether CEO tone and discussion topics during earnings calls can predict short-term stock price volatility.

## Tools Used
- Python (Pandas, FinBERT, Scikit-learn)
- Classification modeling and performance evaluation
