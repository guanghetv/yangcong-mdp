from config import *

# return selected list of ObjectIds of topic ids 
def choose_topics(publisher, semester):
    c = chapters.find({"publisher": publisher, "semester": semester})
    t = list()
    for doc in c:
        t += doc['themes']

    topic = list()
    for each in t:
        x = themes.find_one({"_id": each})
        if x is not None:
            topic += x['topics']

    y = topic_diff.distinct("_id", {"_id": {"$in": topic}})
    return y
