# Deployment Guide

This document explains how to deploy the Streamlit app from this repository to two common platforms: **Streamlit Cloud** and **Heroku**.

## Prerequisites

- A GitHub account with the repository accessible online
- An OpenAI API key for running the app
- (For Heroku) A Heroku account and the Heroku CLI installed locally

## Deploying to Streamlit Cloud

1. Push your code to GitHub if it is not already hosted there.
2. Log in to [Streamlit Cloud](https://share.streamlit.io/) with your GitHub account.
3. Click **New app** and select this repository and the `streamlit_app.py` file.
4. Add `OPENAI_API_KEY` to the app secrets in the Streamlit Cloud UI.
5. Click **Deploy**. Streamlit Cloud will install the requirements and run the app automatically.

Any changes pushed to the repository will trigger a rebuild on Streamlit Cloud.

## Deploying to Heroku

1. Install the Heroku CLI and log in with `heroku login`.
2. Create a new Heroku app:
   ```bash
   heroku create YOUR_APP_NAME
   ```
3. Set the OpenAI API key on Heroku:
   ```bash
   heroku config:set OPENAI_API_KEY=your-key
   ```
4. Add a `Procfile` in the repository root containing:
   ```
   web: streamlit run streamlit_app.py --server.port=$PORT
   ```
5. Commit the `Procfile` and push to Heroku:
   ```bash
   git push heroku main
   ```
6. Visit the URL provided by Heroku to see your running app.

Heroku will install the dependencies from `requirements.txt` during the deploy step.

