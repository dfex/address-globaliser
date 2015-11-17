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
    addresses = config.xpath('//address-book/address')
    for address in addresses:
        address_name = address.find('name').text
        if address_name != None:
            if (address.find('ip-prefix') != None):
                # This is an ip-prefix address
                address_prefix = address.find('ip-prefix').text
                address_entries.append({'name':address_name, 'ip-prefix':address_prefix})
                #print ("Address Name: {}, Address Prefix: {}".format(address_name, address_prefix))
                sys.stdout.write(".")
            elif (address.find('dns-name/name') != None):
                # This is a dns-name address
                dns_name = address.find('dns-name/name').text
                address_entries.append({'name':address_name, 'dns-name':dns_name})            
                sys.stdout.write(".")
                #print ("Address Name: {}, DNS Name: {}".format(address_name, dns_name))
            elif (address.find('wildcard-address/name') != None):
                # This is a wildcard address
                wildcard_address = address.find('wildcard-address/name').text
                address_entries.append({'name':address_name, 'wildcard-address':wildcard_address})            
                sys.stdout.write(".")
                #print ("Address Name: {}, Wildcard Address: {}".format(address_name, wildcard_address))
            elif (address.find('range-address/name') != None):
                # This is a range address
                range_address = address.find('range-address/name').text
                high_address = address.find('range-address/to/range-high').text
                address_entries.append({'name':address_name, 'range-address':range_address, 'range-high':high_address})            
                sys.stdout.write(".")
                #print ("Address Name: {}, Range Address: {} to {}".format(address_name, range_address, high_address))                
            else:
                print "Address-type unknown"
    #print address_entries
    address_sets = config.xpath('address-book/address/address-set')
	dev.close()
else:	
	print "Invalid IP Address"

#Pastey
#from jnpr.junos import Device
#from lxml import etree
#dev=Device(host='192.168.56.100',user='lattice',passwd='lattice123')
#dev.open()		
#config = dev.rpc.get_config(filter_xml=etree.XML('<configuration><security><zones/></security></configuration>'))
    
    
#for element in config.iter("{*}address-book/address"):
#    print("Address Name: {}, Address: {}".format(element.find('name').text, element.find('{*}ip-prefix').text))
