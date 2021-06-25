from actions.db.store import MongoDataStore

_db_store = MongoDataStore()


def get_db():
    return _db_store.db
