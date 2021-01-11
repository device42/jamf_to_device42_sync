# starter.py v2

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import json
import yaml
from jamf import JamfApi
from device42 import Device42Api

with open('config.yaml', 'r') as cfg:
	config = yaml.load(cfg.read())

device42 = config['device42']
jamf = config['jamf']
options = config['options']

jamf_api = JamfApi(jamf, options)
device42_api = Device42Api(device42, options)

mobile_deviceCF = config['custom_fields']['mobile_device']
computerCF = config['custom_fields']['computer']
enduserCF = config['custom_fields']['enduser']

class Integration:

    def __init__(self):
        self.computers = jamf_api.get_list('computers')
        self.mobile_devices = jamf_api.get_list('mobiledevices')

    def get_computers(self):
        devices = []
        for computer in self.computers['computers']:
            device = {}
            computer_data = jamf_api.get_item('computers', computer['id'])['computer']
            general = computer_data['general']
            hardware = computer_data['hardware']
            software = computer_data['software']
            purchase = computer_data['purchasing']
            storage = hardware['storage']

            if general['name']:

                hdd_count = 0
                hdd_size = 0
                if storage:
                    for disk in storage:
                        if int(disk['drive_capacity_mb']) > 0:
                            hdd_count += 1
                            hdd_size += int(disk['drive_capacity_mb'])

                    if hdd_size > 0:
                        hdd_size = 1.0 * hdd_size / 1000  # convert to Gb

                device.update({
                    'name': general['name'],
                    'new_name': general['name'],
                    'type': 'physical',
                    'manufacturer': 'Apple Inc.',
                    'hddcount': hdd_count,
                    'hddsize': hdd_size,
                    'uuid': general['udid'] if general['udid'] else None,
                    'serial_no': general['serial_number'] if general['serial_number'] else None,
                    'hardware': hardware['model'] if hardware['model'] else None,
                    'os': hardware['os_name'] if hardware['os_name'] else None,
                    'osver': hardware['os_version'] if hardware['os_version'] else None,
                    'memory': hardware['total_ram_mb'] if hardware['total_ram_mb'] else None,
                    'cpucount': hardware['number_processors'] if hardware['number_processors'] else None,
                    'cpupower': hardware['processor_speed_mhz'] if hardware['processor_speed_mhz'] else None,
                    'cpucore': hardware['number_cores'] if hardware['number_cores'] else None,
                    'tags': general['asset_tag'] if general['asset_tag'] else None
                })

                devices.append({
                    'device': {k: v for (k, v) in device.items() if str(v) != str(-1)},
                    'general': general,
                    'software': software,
                    'purchase': purchase
                })

        return devices

    def get_mobile_devices(self):
        mobile_devices = []
        for mobile_device in self.mobile_devices['mobile_devices']:
            device = {}
            computer_data = jamf_api.get_item('mobile_devices', mobile_device['id'])['mobile_device']
            general = computer_data['general']
            software = computer_data['applications']
            purchase = computer_data['purchasing']

            if general['display_name']:
                capacity = None

                if 'capacity_mb' in general and general['capacity_mb']:
                    capacity = int(general['capacity_mb']) / 1000

                device.update({
                    'name': general['display_name'],
                    'new_name': general['display_name'],
                    'type': 'physical',
                    'manufacturer': 'Apple Inc.',
                    'hddcount': None if capacity is None else 1,
                    'hddsize': capacity,
                    'uuid': general['udid'] if general['udid'] else None,
                    'serial_no': general['serial_number'] if general['serial_number'] else None,
                    'hardware': general['model'] if general['model'] else None,
                    'os': general['os_type'] if general['os_type'] else None,
                    'osver': general['os_version'] if general['os_version'] else None,
                    'tags': general['asset_tag'] if general['asset_tag'] else None
                })

                mobile_devices.append({
                    'device': {k: v for (k, v) in device.items() if str(v) != str(-1)},
                    'general': general,
                    'software': software,
                    'purchase': purchase
                })

        return mobile_devices

    @staticmethod
    def get_device_network(general):
        macs = []
        ips = []

        if general['ip_address']:
            ips.append({
                'ipaddress': general['ip_address'],
            })

        if 'display_name' in general:  # mobile device
            if general['wifi_mac_address']:
                macs.append({
                    'macaddress': general['wifi_mac_address']
                })
        else:  # computer
            if general['mac_address']:
                macs.append({
                    'macaddress': general['mac_address'],
                })

            if general['alt_mac_address']:
                macs.append({
                    'macaddress': general['alt_mac_address'],
                })

            if general['last_reported_ip']:
                ips.append({
                    'ipaddress': general['last_reported_ip'],
                })

        return macs, ips

    @staticmethod
    def get_device_software(applications):
        software = []
        for item in applications['applications']:
            if 'name' in item and item['name']:  # computer
                software.append({
                    'software': item['name'],
                    'version': item['version'],
                })

            elif 'application_name' in item and item['application_name']:  # mobile device
                software.append({
                    'software': item['application_name'],
                    'version': item['application_version'],
                })

        return software

			if general['last_reported_ip']:
				ips.append({
					'ipaddress': general['last_reported_ip'],
				})

		return macs, ips

	def get_device_software(self, applications):
		software = []
		for item in applications:
			if 'name' in item and item['name']:  # computer
				software.append({
					'software': item['name'],
					'version': item['version'],
				})

			elif 'application_name' in item and item['application_name']:  # mobile device
				software.append({
					'software': item['application_name'],
					'version': item['application_version'],
				})

		return software

	def define_Type(self, hardware):
		newtype = 'other'
		newsubtype = None
		if 'imac' in hardware.lower():
			newsubtype = 'desktop'  # set device newsubtype to desktop
		elif 'macmini' in hardware.lower():
			newsubtype = 'desktop'  # set device newsubtype to desktop
		elif 'mac mini' in hardware.lower():
			newsubtype = 'desktop'  # set device newsubtype to desktop
		elif 'macbook' in hardware.lower():
			newsubtype = 'laptop'  # set device newsubtype to desktop
		elif 'ipad' in hardware.lower():
			newsubtype = 'tablet'  # set device newsubtype to desktop
		elif 'iphone' in hardware.lower():
			newsubtype = 'mobile phone'  # set device newsubtype to desktop
		return newtype, newsubtype

	# Takes a list of custom fields, checks to see if they are in the element and appends them to cfList
	def get_device_custom_fields(self, customFields, cfList, element): 
		for cf in customFields:
			if cf['dict'] in element and element[cf['dict']]:
				dataDict = element[cf['dict']]
				key = cf['key']
				if key in dataDict and dataDict[key]: 
					cfList.append({
						'name' : element['device']['name'], 
						'key' : key, 
						'value' : dataDict[key], 
						'type' : cf['type'], 
						'related_field_name' : cf['related_field_name'] if cf['related_field_name'] else None
					})

	# Takes a list of custom fields, checks to see if they are in the element and appends them to cfList
	def get_enduser_custom_fields(self, customFields, cfList, element): 
		for cf in customFields:
			if cf['dict'] in element and element[cf['dict']]:
				dataDict = element[cf['dict']]
				key = cf['key']
				if key in dataDict and dataDict[key]: 
					cfList.append({
						'name' : element['enduser']['name'], 
						'key' : key, 
						'value' : dataDict[key], 
						'type' : cf['type'], 
						'related_field_name' : cf['related_field_name'] if cf['related_field_name'] else None
					})
	
	# Takes the location dictionary from computer/mobile_device and returns a enduser
	def get_enduser(self, location): 
		data = {}
		enduser = {}

		if location['username']:
			enduser.update({
				'name' : location['username'],
				'email' : location['email_address'] if location['email_address'] else None, 
				'contact' : location['phone_number'] if location['phone_number'] else None
			})
			data.update({
				'enduser' : enduser, 
				'location' : location
			})
		return data

def main():
	integration = Integration()
	computers = integration.get_computers()
	mobile_devices = integration.get_mobile_devices()
	buildings = integration.get_buildings()

	deviceData = {
		'devices': [], 
		'device_custom_fields': [],
		'endusers': [], 
		'enduser_custom_fields': [], 
		'buildings': buildings
	}

	# computers
	for computer in computers:
		macs, ips = integration.get_device_network(computer['general'])
		software = integration.get_device_software(computer['software'])
		enduser = integration.get_enduser(computer['location'])

		if options['no_ips']:
			ips = []


    computers = integration.get_computers()
    mobile_devices = integration.get_mobile_devices()

    data = {
        'devices': []
    }

    # computers
    for computer in computers:
        macs, ips = integration.get_device_network(computer['general'])
        software = integration.get_device_software(computer['software'])

        if options['no_ips']:
            ips = []

        data['devices'].append({
            'device': computer['device'],
            'macs': macs,
            'ips': ips,
            'software': software
        })

    # mobile devices
    for mobile_device in mobile_devices:
        macs, ips = integration.get_device_network(mobile_device['general'])
        software = integration.get_device_software(mobile_device['software'])

		# Grab computer custom fields
		integration.get_device_custom_fields(computerCF, deviceData['device_custom_fields'], computer)

        data['devices'].append({
            'device': mobile_device['device'],
            'macs': macs,
            'ips': ips,
            'software': software
        })

	# mobile devices
	for mobile_device in mobile_devices:
		macs, ips = integration.get_device_network(mobile_device['general'])
		software = integration.get_device_software(mobile_device['software'])
		enduser = integration.get_enduser(mobile_device['location'])

		if options['no_ips']:
			ips = []

		deviceData['devices'].append({
			'device': mobile_device['device'],
			'macs': macs,
			'ips': ips,
			'software': software
		})

		# Grab mobile device custom fields
		integration.get_device_custom_fields(mobile_deviceCF, deviceData['device_custom_fields'], mobile_device)

		# Grab enduser and any associated custom fields
		if enduser:
			integration.get_enduser_custom_fields(enduserCF, deviceData['enduser_custom_fields'], enduser)
			deviceData['endusers'].append(enduser['enduser'])

	return deviceData


if __name__ == '__main__':
	elements = main()

	# Import buildings
	for element in elements['buildings']:
		print device42_api.post_building(element)

	# Bulk import of devices
	for element in elements['devices']:
		print device42_api.bulk(element)
			
	# Import endusers
	for element in elements['endusers']:
		print device42_api.post_enduser(element)

	# Import enduser custom fields
	for element in elements['enduser_custom_fields']:
		print device42_api.put_enduserCF(element)

	# Import device custom fields
	for element in elements['device_custom_fields']:
		print device42_api.put_deviceCF(element)

	print '\n Finished'
