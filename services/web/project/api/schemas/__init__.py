import json
import os

this_dir = os.path.dirname(os.path.realpath(__file__))

# Alert
with open(os.path.join(this_dir, 'alert_create.json')) as j:
    alert_create = json.load(j)
with open(os.path.join(this_dir, 'alert_update.json')) as j:
    alert_update = json.load(j)

# Value
with open(os.path.join(this_dir, 'value_create.json')) as j:
    value_create = json.load(j)
with open(os.path.join(this_dir, 'value_update.json')) as j:
    value_update = json.load(j)
