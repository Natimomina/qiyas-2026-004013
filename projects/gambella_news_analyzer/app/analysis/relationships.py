from collections import defaultdict
from ..models import Article

def article_relationships(article):
    groups = defaultdict(list)
    for e in article.entities:
        groups[e.entity_type].append(e.entity_text)
    rels=[]
    people=set(groups.get('PERSON',[])); orgs=set(groups.get('ORG',[])); locs=set(groups.get('LOCATION',[]))
    for p in people:
        for o in orgs: rels.append({'source':p,'target':o,'relation':'mentioned_with'})
        for l in locs: rels.append({'source':p,'target':l,'relation':'mentioned_with'})
    for o in orgs:
        for l in locs: rels.append({'source':o,'target':l,'relation':'mentioned_with'})
    return rels
