import json
import os

this_dir = os.path.dirname(os.path.realpath(__file__))

# Campaign
with open(os.path.join(this_dir, 'campaign_create.json')) as j:
    campaign_create = json.load(j)
with open(os.path.join(this_dir, 'campaign_update.json')) as j:
    campaign_update = json.load(j)

# CampaignAlias
with open(os.path.join(this_dir, 'campaign_alias_create.json')) as j:
    campaign_alias_create = json.load(j)
with open(os.path.join(this_dir, 'campaign_alias_update.json')) as j:
    campaign_alias_update = json.load(j)

# Indicator
with open(os.path.join(this_dir, 'indicator_create.json')) as j:
    indicator_create = json.load(j)
with open(os.path.join(this_dir, 'indicator_update.json')) as j:
    indicator_update = json.load(j)

# IntelReference
with open(os.path.join(this_dir, 'intel_reference_create.json')) as j:
    intel_reference_create = json.load(j)
with open(os.path.join(this_dir, 'intel_reference_update.json')) as j:
    intel_reference_update = json.load(j)

# Null
with open(os.path.join(this_dir, 'null_create.json')) as j:
    null_create = json.load(j)

# Role
with open(os.path.join(this_dir, 'role_create.json')) as j:
    role_create = json.load(j)
with open(os.path.join(this_dir, 'role_update.json')) as j:
    role_update = json.load(j)

# User
with open(os.path.join(this_dir, 'user_create.json')) as j:
    user_create = json.load(j)
with open(os.path.join(this_dir, 'user_update.json')) as j:
    user_update = json.load(j)

# Value
with open(os.path.join(this_dir, 'value_create.json')) as j:
    value_create = json.load(j)
with open(os.path.join(this_dir, 'value_update.json')) as j:
    value_update = json.load(j)
