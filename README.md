## address-globaliser

This is a utility for migrating SRX configurations prior to importing them to a recent versions of Junos Space Security Director. 

The utility will:
* Convert zone-based address-book entries to the global address-book and delete the zone-based address-book
* Highlight any non-unique address-book objects (since they can overlap in zone-based address-books) and make them unique, while updating them in security policy and NAT objects
* Rename source, destination and static NAT objects such that they aren't conflicting
* Output a list of configuration changes to be applied in "set" format for change management
* Optionally commit the changes directly to the SRX

###Usage

```
-> address-globaliser.py <srx-ip-address>
SRX Address-Book Globalisation Tool


Username: netadmin 
Password: *************
```

###To-Do List
* ~~Address-type ip-prefix~~
* ~~Address-type dns-name~~
* ~~Address-type wildcard~~
* ~~Address-type range~~
* ~~address-set support~~
* Support for source NAT address objects
* Support for destination NAT address objects
* Support for static NAT address objects
* Confirm unique address object name
* ~~Delete existing address objects and replace with globalised versions in Junos config~~
* ~~Add --commit option to apply configuration directly to SRX~~
* ~~generate a Junos config file for offline/scheduled changes~~
