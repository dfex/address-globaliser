#!/usr/bin/env python3

import sys
import re
from getpass import getpass
from pprint import pprint
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from lxml import etree

print ("SRX Address-Book Globalisation Tool\n\n")
if len(sys.argv) < 2:
    print ("Error: Missing parameter\n")
    print ("Usage: address-globaliser.py ip-address [-u username] [-p password] [--commit]\n")
    sys.exit()
	
hostAddress = sys.argv[1]
username = "nxtadmin"
password = "!!Yamaha600!!"

inetRegex = re.compile("^([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-1][0-9]|22[0-3])\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])$") 

patch_config=[]
address_object_list={}

def register_address_object(address_object_name, address_object_address, address_object_list):
    # Take an address, make sure there are no conflicts, and place it in the address_object_list
    # If there are conflicts, append something to the name so that it is unique
    if address_object_name in address_object_list:
        # Same name
        if address_object_address in address_object_list.values():
            # Same name and address - return anyway
            return address_object_name
        else:
            # Same name, different address - rename_1
            address_object_list[address_object_name + "_1"] = address_object_address
            return address_object_name + "_1"
    else:
        # Different name
        if address_object_address in address_object_list.values():
            # Different name
            address_object_list[address_object_name] = address_object_address
        return address_object_name
        
        
        # In addresses, if same address name, rename (to *_zone) => update security policy
        # In addresses, if different name but same address, keep as is
        # In address-sets, if same address-set-name, rename (to *_zone) => update security policy
        # In address-sets, if member address name is different, but address is the same, rename it to match existing (does this conflict with 2?)
        
        # Re-structure so that config is read, functions are used to register all address-objects by zone, name, type and address (and high)
        # Then global address-book is generated AFTER when all information is in a dict/list
        
        #address_objects=[
        # Object Zone: zone
        # Object Type: address
        # Object Name: name
        # Address Style: ip-prefix / dns-name / wildcard-address / range-address
        # Address: string
        # High-Address: string
        # ]
        # 
        # address_set_objects=[
        # Object Zone: zone
        # Object Type: address-set
        # Object Name: name
        # Addresses: [string, string]
        # Address-sets: [string, string]
        # ]
        
        #addrdict={'add1':'192.168.100.10/32','add2':'192.168.100.11/32','add3':'google.com'}
        #>>> addrdict
        #{'add3': 'google.com', 'add2': '192.168.100.11/32', 'add1': '192.168.100.10/32'}
        #>>> "add3" in addrdict
        #True
        #>>> "google.com" in addrdict.values()
        #True


if inetRegex.match(str(sys.argv[1])):
    if password != '':
        dev = Device(host=hostAddress.rstrip('\n'),user=username,passwd=password)
    else:
        dev = Device(host=hostAddress.rstrip('\n'),user=username)
    dev.open()		
    config = dev.rpc.get_config(filter_xml=etree.XML('<configuration><security><zones/></security></configuration>'))
    zones = config.xpath('//security-zone')
    for zone in zones:
        zone_name = zone.find('name').text
        addresses = zone.xpath('address-book/address')
        if addresses:
            for address in addresses:
                address_name = address.find('name').text
                if address_name != None:
                    if (address.find('ip-prefix') != None):
                        # This is an ip-prefix address
                        address_prefix = address.find('ip-prefix').text
                        unique_address_name = register_address_object(address_name, address_prefix, address_object_list)
                        patch_config.append("set security address-book global address " + unique_address_name + " " + address_prefix)
                    elif (address.find('dns-name/name') != None):
                        # This is a dns-name address
                        dns_name = address.find('dns-name/name').text
                        unique_address_name = register_address_object(address_name, dns_name, address_object_list)
                        patch_config.append("set security address-book global address " + unique_address_name + " dns-name " + dns_name)
                    elif (address.find('wildcard-address/name') != None):
                        # This is a wildcard address
                        wildcard_address = address.find('wildcard-address/name').text
                        unique_address_name = register_address_object(address_name, wildcard_address, address_object_list)                                
                        patch_config.append("set security address-book global address " + unique_addresss_name + " wildcard-address " + wildcard_address)
                    elif (address.find('range-address/name') != None):
                        # This is a range address
                        range_address = address.find('range-address/name').text
                        high_address = address.find('range-address/to/range-high').text
                        print ("set security address-book global address " + address_name + " range-address " + range_address + " to " + high_address)
                    else:
                        pass
                        # address type unknown
                else:
                    pass
                    # no addresses found
            address_sets = zone.xpath('address-book/address-set')
            for address_set in address_sets:
                address_set_name = address_set.find('name').text
                member_addresses = address_set.xpath('address')
                for member_address in member_addresses:
                    member_address_name = member_address.find('name').text
                    unique_member_address_name = register_address_object(address_set.find('name').text, member_address_name, address_object_list)
                    patch_config.append ("set security address-book global address-set " + address_set_name + " address " + member_address_name) 
                member_address_sets = address_set.xpath('address-set')
                for member_address_set in member_address_sets:
                    member_address_set_name = member_address_set.find('name').text
                    patch_config.append ("set security address-book global address-set " + address_set_name + " address-set " + member_address_set_name)
        # delete the zone-based address-book
            patch_config.append ("delete security zones security-zone " + zone_name + " address-book")
        else:
            # no addresses in this zone
            pass
    if "--commit" in sys.argv:
         # take the patch_config list and convert it into a single string preserving line-breaks
        candidate_config = "\n".join(patch_config)
        print ("Candidate configuration generated")
        cu = Config(dev)
        cu.load(candidate_config, format="set")
        print ("Committing configuration")
        cu.commit()
        print ("Commit complete, closing device connection")
    else: 
        # output patch file to STDOUT
        for config_line in patch_config:
            print (config_line)
    # and we're done - close device connection
    dev.close()
else:
    # ip-regex failed	
	print ("Invalid IP Address")
	


