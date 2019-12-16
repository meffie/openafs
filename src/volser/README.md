
DEVELOPMENT NOTE

Unfortunately, the vldb entry serverNumber (a 32-bit int) is directly used as
the primary IPv4 address of the fileserver. As noted in vsproc.c, there should
be a level of indirection between the server number and the list of addresses
for the server, if we are going to support IPv6-only file servers.

This patchset starts to separate the serverNumber from the server address.

Note: This branch does not contain the gerrit 13834, which was an earlier
      attempt to remove `inet_ntoa` calls. That commit just replaced them
      with another `inet_ntoa` type call.
