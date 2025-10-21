import os
import logging
import requests
from flask import Flask, request, jsonify

# ========== Config ========== 
TOKEN = os.environ.get("TELEGRAM_TOKEN")  # מוגדר ב-Render
PUBLIC_URL = os.environ.get("PUBLIC_URL")  # אופציונלי: https://amir-trading