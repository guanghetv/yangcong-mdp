from config import *
from bson.objectid import ObjectId
from collections import defaultdict

'''
    Topic difficulty model params
        - topic type (A-1 B-2 C-3 D-4)
        - topic position
        - topic correct

    Schema (mdp -> topicDiff)
        {
            "_id": <topic_id>,
            "type": 1,
            "position": topic Index in theme / (theme Topics +1),
            "incorrect": topic incorrect ratio
        }
'''



# theme_lists
pipeline = [
    {"$match": {"subject": "math", "publisher": "人教版"}},
    {"$group": {"_id": None, "themes": {"$push": "$themes"}}}
]

theme_lists = list(chapters.aggregate(pipeline))[0]['themes']
theme_lists = [item for sublist in theme_lists for item in sublist]

# Construct skill -> ability mapping
skill_abilities = {
    1: 'abstraction',
    2: 'abstraction',
    3: 'abstraction',
    4: 'imagination',
    5: 'imagination',
    6: 'imagination',
    7: 'data',
    8: 'data',
    9: 'data',
    10: 'calculation',
    11: 'calculation',
    12: 'calculation',
    13: 'calculation',
    14: 'logic',
    15: 'logic',
    16: 'logic',
    17: 'logic',
    18: 'logic',
    19: 'logic',
    20: 'logic',
    21: 'logic',
    22: 'model',
    23: 'model'
}

# topic type -> skillset weights
type_skill_weights = 0.6

# filter questionable topics only
topic_candidate = events.distinct("topicId", {"action": "q"})

# get answer correctness by topics
pipeline = [
    {"$match": {"action": "q"}},
    {"$sort": {"eventTime": 1}},
    {"$group": {"_id": {"user": "$user", "topic": "$topicId"}, "c": {"$first": "$correct"}}},
    {"$group": {"_id": "$_id.topic", "results": {"$push": "$c"}}}
]
x = events.aggregate(pipeline, allowDiskUse=True)

for t in x:
    t_id = ObjectId(t['_id'])
    t_body = topics.find_one(t_id)
    if t_body is not None and \
        t_body['subject'] == 'math' and \
        t_body['type'] in 'ABCD' and \
        len(t_body['skills']) > 0:

        result = dict()

        # _id
        result['_id'] = t_id

        # ability set
        skill_ability_conversion = defaultdict(float)
        total_skill_points = 0.0
        for skill in t_body['skills']:
            if t_body['skills'].index(skill) == 0:
                skill_ability_conversion[skill_abilities[skill]] += 1.0
                total_skill_points += 1.0
            else:
                skill_ability_conversion[skill_abilities[skill]] += type_skill_weights
                total_skill_points += type_skill_weights

        result['abilitySet'] = dict()
        for k, v in skill_ability_conversion.items():
            point_value = v / total_skill_points
            result['abilitySet'][k] = round(point_value, 3)

        # type
        result['type'] = '0ABCD'.index(t_body['type'])

        # position
        u_theme = themes.find_one({"_id": {"$in": theme_lists}, "topics": t_id})
        if u_theme:
            result['position'] = (u_theme['topics'].index(t_id) + 1) / (len(u_theme['topics']) + 1)

        # incorrect ratio
        answerings = len(t['results']) + 0.1
        incorrects = t['results'].count(False) + 0.1
        result['incorrect'] = incorrects / answerings

        # insert doc
        topic_diff.insert_one(result)

# close connections
conn.close()
