#!/usr/bin/python

import sys
import re
from getpass import getpass
from pprint import pprint
from jnpr.junos import Device
from lxml import etree

print "SRX Address-Book Globalisation Tool\n\n"
if len(sys.argv) != 2:
    print "Error: Missing parameter\n"
    print "Usage: address-globaliser.py <ip address>\n"
    sys.exit()
	
hostAddress = sys.argv[1]
username = raw_input('Username: ')
password = getpass('Password (leave blank to use SSH Key): ')

inetRegex = re.compile("^([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-1][0-9]|22[0-3])\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])$") 

address_entries=[]

if inetRegex.match(str(sys.argv[1])):
    if password != '':
        dev = Device(host=hostAddress.rstrip('\n'),user=username,passwd=password)
    else:
        dev = Device(host=hostAddress.rstrip('\n'),user=username)
    dev.open()		
    config = dev.rpc.get_config(filter_xml=etree.XML('<configuration><security><zones/></security></configuration>'))
    dev.close()
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
                        print ("set security address-book global address {} {}".format(address_name, address_prefix))
                    elif (address.find('dns-name/name') != None):
                        # This is a dns-name address
                        dns_name = address.find('dns-name/name').text
                        print ("set security address-book global address {} dns-name {}".format(address_name, dns_name))
                    elif (address.find('wildcard-address/name') != None):
                        # This is a wildcard address
                        wildcard_address = address.find('wildcard-address/name').text        
                        print ("set security address-book global address {} wildcard-address {}".format(address_name, wildcard_address))
                    elif (address.find('range-address/name') != None):
                        # This is a range address
                        range_address = address.find('range-address/name').text
                        high_address = address.find('range-address/to/range-high').text
                        print ("set security address-book global address {} range-address {} to {}".format(address_name, range_address, high_address))
                    else:
                        print "Address-type unknown"
                else:
                    pass
                    # no addresses found
            address_sets = zone.xpath('address-book/address-set')
            for address_set in address_sets:
                address_set_name = address_set.find('name').text
                member_addresses = address_set.xpath('address')
                for member_address in member_addresses:
                    member_address_name = member_address.find('name').text
                    print ("set security address-book global address-set {} address {}".format(address_set_name, member_address_name)) 
                member_address_sets = address_set.xpath('address-set')
                for member_address_set in member_address_sets:
                    member_address_set_name = member_address_set.find('name').text
                    print ("set security address-book global address-set {} address-set {}".format(address_set_name, member_address_set_name))
        # delete the zone-based address-book
            print ("delete security zones security-zone {} address-book".format(zone_name))
        else:
            # no addresses in this zone
            pass
    # done 
    print ("\n")
else:
    # ip-regex failed	
	print "Invalid IP Address"