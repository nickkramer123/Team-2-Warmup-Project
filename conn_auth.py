
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def get_auth():
    cred = credentials.Certificate("movie-collection-firebase-admin.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db

