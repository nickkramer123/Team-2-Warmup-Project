
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def get_auth():
    cred = credentials.Certificate("movie-collection-fd2b8-firebase-adminsdk-fbsvc-0d2c29ef17.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db

