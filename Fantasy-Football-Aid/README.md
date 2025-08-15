# Fantasy Football Season Predictions + Draft Aid

This goal of this project is to predict performance for football players for the upcoming 2025 NFL season. I used a RandomForest model to predict fantasy points per game for players at each position and created an LLM integrated streamlit interface to help users draft a team. 

## Notebooks

### 1. Fantasy_Football_Player_Predictions.ipynb
- Collected and cleaned prior season rushing, receiving and passing statistics at each position. 
- Applied a one season lag to each player's statistics to add more robust features. 
- Tested predictions using XGBoost and RandomForest models, ultimately choosing RandomForest due to better MAE metrics.
- Weighted outputs against players' average draft positions to account for injuries, role changes, rookies, etc. 
  
### 2. streamlit_fantasy_ui.py
- Created a simple draft aid user interface that allows someone drafting a team to track who they have picked ad players drafted by other teams in the league. 
- Integrated Gemini LLM with a google studio API that tracks players available and current team needs to recommend a team's next pick.  

## Objective
To give someone new to fantasy football an easy to use interface so that they can make more informed decisions when drafting a team. 

## Techniques Used
- Data collection, cleaning, EDA, feature engineering, and dataset shifting. 
- XGBoost and RandomForest modeling. 

## Tools
- Python (Pandas, Matplotlib, scikit-learn)
- Google Studio API
- Streamlit 
