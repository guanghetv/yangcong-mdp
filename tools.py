from config import *
from collections import defaultdict

class Student(object):
    def reset_abilities(self):
        self.abilities = {
            "model": 0.0,
            "imagination": 0.0,
            "calculation": 0.0,
            "logic": 0.0,
            "abstraction": 0.0,
            "data": 0.0
        }

    def evaluate_abilities(self):
        self.reset_abilities()
        learn_scope = list(self.learned_coeff.keys())
        x = topic_diff.find({"_id": {"$in": learn_scope}})
        t_abilities = defaultdict(float)
        for doc in x:
            e = self.learned_coeff[doc['_id']]
            d = doc['ndiff']
            a = doc['abilitySet']
            for k in a:
                self.abilities[k] += e * d * a[k]
                t_abilities[k] += d * a[k]

        for k in self.abilities:
            if t_abilities[k] != 0.0:
                self.abilities[k] /= t_abilities[k]

    # @learned : a dict with topic ids (ObjectId) as key, and init Learned
    # coeff ([0.0, 1.0]) as value, if None, all the learned will be set to
    # 0.5
    def __init__(self, learned=None):
        if learned != None:
            self.learned_coeff = learned 
        else:
            learn_scope = topic_diff.distinct("_id")
            self.learned_coeff = dict()
            for each in learn_scope:
                self.learned_coeff[each] = 0.5

        # update abilities
        self.evaluate_abilities()


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
