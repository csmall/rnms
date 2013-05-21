
*********************
Users and Permissions
*********************
Rosenberg uses the repoze.what method of authorization which is based upon
three sets of models.

Users
=====
The first model is the User. This is usually a person although it can be 
a role.  A User has a username and a password and the combination of these
permits access to Rosenberg.  All Attributes within the system are owned
by a User, which can provide them with a limited read-only access to the
state of the Attribute.

A User model also has an email_address which is used to send Triggers
if they are setup for it.

Permissions
===========
For each method within each controller the second model called a Permission
is used to determine access. The following permissions are defined for
Rosenberg:

=======  ===============================================
 Name    Description
=======  ===============================================
UserRO   Read-Only Access to User, Group and Permissions
UserRW   Read/Write Access to User, Group and Permissions
HostRO   Read-Only Access to Host and Attribute
HostRW   Read/Write Access to Host and Attribute
AdminRO  Read-Only Access to remaining models
AdminRW  Read/Write Access to remaining models
=======  ===============================================

There is likely to me more Permissions created in future versions of Rosenberg
depending on user feedback.

Groups
======
Groups are the glue between Permissions and Users. Users cannot have
permissions granted to them directly, but belong to Groups which do have
Permissions assigned to them.  A User can belong to none, one or many Groups
and a Group can be assigned multiple Permissions.  As the relationship 
between a Group and a Permission is many-to-many, different Groups can
have the same Permision assigned to them.

There are several pre-defined Groups within a standard installation
of Rosenberg.

=============   =======================
Group Name      Permissions
=============   =======================
User View       UserRO
User Admin      UserRW
Host View       HostRO
Host Admin      HostRW
System View     UserRO, HostRO, AdminRO
System Admin    UserRW, HostRW, AdminRW
=============   =======================


.. rubric:: Footnotes

.. [#f1] In JFFNMS users (which had admin access) and clients (which owned the interface) were separate models, they are combined in Rosenberg.
