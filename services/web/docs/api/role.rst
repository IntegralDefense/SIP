Role
****

.. contents::
  :backlinks: none

Summary
-------

.. qrefflask:: project:create_app()
  :endpoints: api.create_role, api.read_role, api.read_roles, api.update_role, api.delete_role
  :order: path

Create
------

**JSON Schema**

Required parameters are in **bold**.

.. jsonschema:: ../../project/api/schemas/role_create.json

|

.. autoflask:: project:create_app()
  :endpoints: api.create_role

Read Single
-----------

.. autoflask:: project:create_app()
  :endpoints: api.read_role

Read Multiple
-------------

.. autoflask:: project:create_app()
  :endpoints: api.read_roles

Update
------

**JSON Schema**

Required parameters are in **bold**.

.. jsonschema:: ../../project/api/schemas/role_update.json

|

.. autoflask:: project:create_app()
  :endpoints: api.update_role

Delete
------

.. autoflask:: project:create_app()
  :endpoints: api.delete_role