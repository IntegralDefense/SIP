User
****

.. contents::
  :backlinks: none

Summary
-------

.. qrefflask:: project:create_app()
  :endpoints: api.create_user, api.read_user, api.read_users, api.update_user, api.delete_user
  :order: path

Create
------

**JSON Schema**

Required parameters are in **bold**.

.. jsonschema:: ../../project/api/schemas/user_create.json

|

.. autoflask:: project:create_app()
  :endpoints: api.create_user

Read Single
-----------

.. autoflask:: project:create_app()
  :endpoints: api.read_user

Read Multiple
-------------

.. autoflask:: project:create_app()
  :endpoints: api.read_users

Update
------

**JSON Schema**

Required parameters are in **bold**.

.. jsonschema:: ../../project/api/schemas/user_update.json

|

.. autoflask:: project:create_app()
  :endpoints: api.update_user

Delete
------

.. autoflask:: project:create_app()
  :endpoints: api.delete_user