Event
*****

.. contents::
  :backlinks: none

Summary
-------

.. qrefflask:: project:create_app()
  :endpoints: api.create_event, api.read_event, api.read_events, api.update_event, api.delete_event
  :order: path

Create
------

**JSON Schema**

Required parameters are in **bold**.

*NOTE*: While only **name** and **username** are listed as required parameters,
**disposition** and **status** are also required. However, these two parameters
are omitted from the required list of fields because SIP will use the default
values you chose when you initially setup and configured SIP.

SIP comes with a list of reasonable values that are added to the database during
its initial setup. For example, the default disposition chosen is "DELIVERY", and
the default status is "OPEN".

.. jsonschema:: ../../project/api/schemas/event_create.json

|

.. autoflask:: project:create_app()
  :endpoints: api.create_event

Read Single
-----------

.. autoflask:: project:create_app()
  :endpoints: api.read_event

Read Multiple
-------------

.. autoflask:: project:create_app()
  :endpoints: api.read_events

Update
------

**JSON Schema**

Required parameters are in **bold**.

.. jsonschema:: ../../project/api/schemas/event_update.json

|

.. autoflask:: project:create_app()
  :endpoints: api.update_event

Delete
------

.. autoflask:: project:create_app()
  :endpoints: api.delete_event