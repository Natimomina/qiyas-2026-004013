# House Price Prediction Project 

This project is a machine learning tool built to estimate property values in ETB based on features like the number of rooms, property age, and distance to schools. 

## Project Files
*   `houses_improved.csv`: The dataset containing the property data used to teach the AI.
*   `House_Price_Prediction_Project.ipynb`: The main Python notebook where the data is cleaned and the models are trained.
*   `pipeline_bundle.pkl`: A saved file containing the smartest, most accurate model so it doesn't have to be retrained from scratch every time.

## How It Works
1.  **Training:** The code tests several different algorithms (like Linear Regression and Random Forest) to figure out which one is the most accurate at guessing house prices.
2.  **Web Interface:** It automatically builds a simple web page using Gradio. 
3.  **Prediction:** You can type in the details of any house into the web page, and the best AI model will instantly give you an estimated price.