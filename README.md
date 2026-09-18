# BTC/ETH Position Size Calculator

A Streamlit web UI based on the supplied Python position-sizing calculation.

## Run locally

Install Python 3.10+ and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The browser will open the calculator.

## Deploy free on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload:
   - `app.py`
   - `requirements.txt`
3. Go to Streamlit Community Cloud.
4. Sign in with GitHub.
5. Create a new app.
6. Select your repository and `app.py`.
7. Deploy.

The resulting URL can be opened from your phone or laptop.

## Calculation

The calculator retains the supplied formula:

Q = (capital × risk percentage) /
    (|entry − stop loss| + fee rate × (entry + stop loss))

Lots = floor(Q / contract value)

It additionally shows the rounded position size and the corresponding estimated loss and fees.
