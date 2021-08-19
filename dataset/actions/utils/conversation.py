from actions.db.rasa import rasa_db


def get_funnel_stats():
    funnel_stats = rasa_db.conversations.aggregate(
        [
            {"$match": {"slots.chat_type": "private"}},
            {
                "$project": {
                    "sender_id": 1,
                    "events": {
                        "$filter": {
                            "input": "$events",
                            "as": "event",
                            "cond": {
                                "$and": [
                                    {"$eq": ["$$event.event", "action"]},
                                    {"$ne": ["$$event.name", "action_listen"]},
                                ]
                            },
                        }
                    },
                }
            },
            {"$unwind": "$events"},
            {
                "$group": {
                    "_id": "$events.name",
                    "users": {"$addToSet": "$sender_id"},
                },
            },
            {"$unwind": "$users"},
            {"$sortByCount": "$_id"},
        ]
    )
    funnel_stats_str = ""
    for f in funnel_stats:
        funnel_stats_str = funnel_stats_str + f"{f.get('_id')}: {f.get('count')}\n"
    return funnel_stats_str
