''' The admin program reads data from a JSON file saved locally and
will initialize and upload the data to the Google Firebase Cloud Datastore.
It will run one time. A second run deletes and recreates the datastore '''

# preface: firebase connection and authentication. Import function from that file.

import json
import sys
from conn_auth import get_auth

''' load_dataset() reads JSON file and returns python object'''
def load_dataset(str_path):
    with open(str_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    return dataset


''' delete_collection() uses the firestore object to delete all documents'''
def delete_collection(coll_ref, batch_size):
    if batch_size == 0:
        return

    docs = coll_ref.list_documents(page_size=batch_size)
    deleted = 0

    for doc in docs:
        doc.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)


''' upload_movies() takes db object and dataset loaded from JSON.
Uploads/writes each movie as a document in the collection'''
def upload_movies(coll_ref, movies):

    uploaded = 0

    for m in movies:
        if not isinstance(m, dict):
            continue # only dictionaries

        coll_ref.add(m)  # document being added
        uploaded = uploaded + 1

    print(f"Uploaded {uploaded} docs")


def main():
    # Check for program to take a single command-line argument
    # $ python admin.py restaurant-data.json
    if len(sys.argv) != 2:
        print(f"Error: check command line arguments.")
        sys.exit(1)

    # obtain dataset filepath from command-line
    dataset_path = sys.argv[1] # movies.json

    # get Firestore client object when initializing
    db = get_auth()

    # load_dataset() call
    movies = load_dataset(dataset_path)
    print(f"Loaded {len(movies)} movies from {dataset_path}")

    coll_ref = db.collection("movies")
    # delete_collection() call
    delete_collection(coll_ref, batch_size=99)


    upload_movies(coll_ref, movies)
    print("Done.")


if __name__ == "__main__":
    main()