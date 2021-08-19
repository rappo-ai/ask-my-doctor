from actions.db.store import MongoDataStore

_rasa_db_store = MongoDataStore("rasa")

rasa_db = _rasa_db_store.db


def reset_rasa_db():
    for c in rasa_db.list_collection_names():
        rasa_db.drop_collection(c)
