import json

# Opening JSON file
f = open('daemon.json')

# returns JSON object as 
# a dictionary
data = json.load(f)

print(data['fixed-cidr-v6'])

data['fixed-cidr-v6']="aljkljaljlkjajl"

json_string = json.dumps(data)

# Directly from dictionary
with open('json_data.json', 'w') as outfile:
    outfile.write(json_string)