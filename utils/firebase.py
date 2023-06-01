from firebase_admin import credentials, initialize_app, firestore, _apps


def init_firebase():
    if not _apps:
        print("Init firebase...")
        cred = credentials.Certificate("serviceAccountKey.json")
        initialize_app(cred)

    return firestore.client()
