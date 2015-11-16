## address-globaliser

This is a utility for migrating SRX address-book entries from zone-based to the global address-book.  It is useful when migrating systems into Junos Space Security Director, where conflicting zone-based entries will be aliased.

###Usage

```
-> address-globaliser.py <srx-ip-address>
SRX Address-Book Globalisation Tool


Username: netadmin 
Password: *************
```

###To-Do List
* ~Address-type ip-prefix~
* ~Address-type dns-name~
* ~Address-type wildcard~
* ~Address-type range~
* Address-set support
* Support for source NAT address objects
* Support for destination NAT address objects
* Support for static NAT address objects
* Confirm unique address object name
* Delete existing address objects and replace with globalised versions in Junos config
* Add commit/dry-run option
* Add option to generate a Junos patch file for offline/scheduled changes
