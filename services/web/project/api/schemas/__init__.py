import json
import os

this_dir = os.path.dirname(os.path.realpath(__file__))

# Alert
with open(os.path.join(this_dir, 'alert_create.json')) as j:
    alert_schema_create = json.load(j)
with open(os.path.join(this_dir, 'alert_update.json')) as j:
    alert_schema_update = json.load(j)
