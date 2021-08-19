from actions.db.store import MongoDataStore

_rappo_db_store = MongoDataStore("rappo")

rappo_db = _rappo_db_store.db


def reset_rappo_db():
    for c in rappo_db.list_collection_names():
        rappo_db.drop_collection(c)
