from app.app import app

# This is a serverless entry point for Vercel
app.debug = False

# WSGI handler for Vercel
handler = app