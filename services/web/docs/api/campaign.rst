Campaign
********

.. contents::
  :backlinks: none

Summary
-------

.. qrefflask:: project:create_app()
  :endpoints: api.create_campaign, api.read_campaign, api.read_campaigns, api.update_campaign, api.delete_campaign
  :order: path

Create
------

**JSON Schema**

Required parameters are in **bold**.

.. jsonschema:: ../../project/api/schemas/campaign_create.json

|

.. autoflask:: project:create_app()
  :endpoints: api.create_campaign

Read Single
-----------

.. autoflask:: project:create_app()
  :endpoints: api.read_campaign

Read Multiple
-------------

.. autoflask:: project:create_app()
  :endpoints: api.read_campaigns

Update
------

**JSON Schema**

Required parameters are in **bold**.

.. jsonschema:: ../../project/api/schemas/campaign_update.json

|

.. autoflask:: project:create_app()
  :endpoints: api.update_campaign

Delete
------

.. autoflask:: project:create_app()
  :endpoints: api.delete_campaign