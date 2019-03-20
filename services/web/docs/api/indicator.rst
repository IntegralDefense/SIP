Indicator
*********

.. contents::
  :backlinks: none

Summary
-------

.. qrefflask:: project:create_app()
  :endpoints: api.create_indicator, api.create_indicator_equal, api.read_indicator, api.read_indicators, api.update_indicator, api.delete_indicator, api.delete_indicator_equal
  :order: path

Create
------

**JSON Schema**

Required parameters are in **bold**.

*NOTE*: While only **type** and **value** are listed as required parameters,
**confidence**, **impact**, and **status** are also required. However, these three parameters
are omitted from the required list of fields because SIP will use the default values
you chose when you initially setup and configured SIP. The final requirement not listed in the
schema is that you must either supply the **username** parameter OR your API key in the
Authorization header. This is what is used to link the indicator to the user who created it.

SIP comes with a list of reasonable values that are added to the database during
its initial setup. For example, the default confidence chosen is "LOW", impact is "LOW",
and status is "NEW".

.. jsonschema:: ../../project/api/schemas/indicator_create.json

|

.. autoflask:: project:create_app()
  :endpoints: api.create_indicator

Create Equal To Relationship
----------------------------

Indicators can be directly or indirectly equal to one another, as the relationships
follow the transitive property. If you make indicator 1 equal to indicator 2, and then
make indicator 2 equal to indicator 3, then indicators 1 and 3 will be indirectly equal.

The "equal" list contains the directly equal indicator IDs.

The "all_equal" list contains directly and indirectly equal indicator IDs.

**JSON Schema**

.. jsonschema:: ../../project/api/schemas/null_create.json

|

.. autoflask:: project:create_app()
  :endpoints: api.create_indicator_equal

Create Parent/Child Relationship
--------------------------------

Indicators can have multiple child indicators, but only a single parent indicator.

The "children" list contains the first-generation child indicator IDs.

The "all_children" list contains first-generation and beyond child indicator IDs.

**JSON Schema**

.. jsonschema:: ../../project/api/schemas/null_create.json

|

.. autoflask:: project:create_app()
  :endpoints: api.create_indicator_relationship

Read Single
-----------

.. autoflask:: project:create_app()
  :endpoints: api.read_indicator

Read Multiple
-------------

.. autoflask:: project:create_app()
  :endpoints: api.read_indicators

Update
------

**JSON Schema**

Required parameters are in **bold**.

.. jsonschema:: ../../project/api/schemas/indicator_update.json

|

.. autoflask:: project:create_app()
  :endpoints: api.update_indicator

Delete
------

.. autoflask:: project:create_app()
  :endpoints: api.delete_indicator

Delete Equal To Relationship
----------------------------

Two indicators must be directly equal in order to delete the relationship.

.. autoflask:: project:create_app()
  :endpoints: api.delete_indicator_equal

Delete Parent/Child Relationship
--------------------------------

The child indicator must be first-generation in order to delete the relationship.

.. autoflask:: project:create_app()
  :endpoints: api.delete_indicator_relationship