import json
with open('state.json', 'r') as fin:
    state = json.load(fin)
print(state)
