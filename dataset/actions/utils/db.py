from actions.db.store import MongoDataStore

_db_store = MongoDataStore()


def get_db():
    return _db_store.db


def get_specialities():
    return [
        "General Surgeon",
        "Paediatrician",
        "Gynaecologist",
        "Psychiatrist",
        "Dermatologist",
    ]


def get_doctors():
    return [
        "Dr. Murali",
        "Dr. Lata",
        "Dr. Srini",
    ]
