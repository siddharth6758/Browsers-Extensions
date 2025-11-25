import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("firebaseConfig.json")
app = firebase_admin.initialize_app(cred)
print(app)