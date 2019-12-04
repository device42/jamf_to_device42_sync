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
			location = computer_data['location']

			if general['name']:
				newtype, newsubtype = self.define_Type(hardware['model'])
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
					'name': '%s-%s' % (general['name'], computer['id']),
					'new_name': '%s-%s' % (general['name'], computer['id']),
					'type': newtype,
					'subtype': newsubtype,
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
					'purchase': purchase, 
					'location' : location
				})

		return devices

	def get_mobile_devices(self):
		mobile_devices = []
		for mobile_device in self.mobile_devices['mobile_devices']:
			device = {}
			computer_data = jamf_api.get_item('mobiledevices', mobile_device['id'])['mobile_device']
			general = computer_data['general']
			software = computer_data['applications']
			purchase = computer_data['purchasing']
			location = computer_data['location']

			if general['display_name']:
				capacity = None
				newtype, newsubtype = self.define_Type(general['model'])
				if 'capacity_mb' in general and general['capacity_mb']:
					capacity = int(general['capacity_mb']) / 1000

				device.update({
					'name': '%s-%s' % (general['name'], mobile_device['id']),
					'new_name': '%s-%s' % (general['name'], mobile_device['id']),
					'type': newtype,
					'subtype': newsubtype,
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
					'purchase': purchase, 
					'location' : location
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
		newtype = None
		newsubtype = None
		if 'imac' in hardware.lower():
			newtype = 'other'  # set device newtype to other
			newsubtype = 'desktop'  # set device newsubtype to desktop
		elif 'macmini' in hardware.lower():
			newtype = 'other'  # set device newtype to other
			newsubtype = 'desktop'  # set device newsubtype to desktop
		elif 'mac mini' in hardware.lower():
			newtype = 'other'  # set device newtype to other
			newsubtype = 'desktop'  # set device newsubtype to desktop
		elif 'macbook' in hardware.lower():
			newtype = 'other'  # set device newtype to other
			newsubtype = 'laptop'  # set device newsubtype to desktop
		elif 'ipad' in hardware.lower():
			newtype = 'other'  # set device newtype to other
			newsubtype = 'tablet'  # set device newsubtype to desktop
		elif 'iphone' in hardware.lower():
			newtype = 'other'  # set device newtype to other
			newsubtype = 'mobile phone'  # set device newsubtype to desktop
		return newtype, newsubtype
	
	@staticmethod
	def get_device_enduser(location): 
		enduser = {}

		if location['username']:
			customFields = {
				'Full_Name' : location['real_name'] if location['real_name'] else None, 
				'Position' : location['position'] if location['position'] else None, 
				'Phone' : location['phone_number'] if location['phone_number'] else None, 
				'Department' : location['department'] if location['department'] else None
			}

			enduser.update({
				'name' : location['username'],
				'email' : location['email_address'] if location['email_address'] else None, 
				'custom_fields' : customFields
			})
		return enduser

def main():
	integration = Integration()

	computers = integration.get_computers()
	mobile_devices = integration.get_mobile_devices()

	deviceData = {
		'devices': [], 
		'endusers': [], 
		'device_custom_fields': []
	}

	# computers
	for computer in computers:
		name = computer['device']['name']
		macs, ips = integration.get_device_network(computer['general'])
		software = integration.get_device_software(computer['software'])
		enduser = integration.get_device_enduser(computer['location'])

		if options['no_ips']:
			ips = []

		deviceData['devices'].append({
			'device': computer['device'],
			'macs': macs,
			'ips': ips,
			'software': software
		})

		if enduser:
			deviceData['endusers'].append(enduser)
			deviceData['device_custom_fields'].append({
				'name' : name,
				'key' : 'user', 
				'value' : enduser['name'], 
				'type' : 'related_field', 
				'related_field_name' : 'endusers'
			})

	# mobile devices
	for mobile_device in mobile_devices:
		general = mobile_device['general']
		name = mobile_device['device']['name']

		macs, ips = integration.get_device_network(general)
		software = integration.get_device_software(mobile_device['software'])
		enduser = integration.get_device_enduser(mobile_device['location'])

		if options['no_ips']:
			ips = []

		deviceData['devices'].append({
			'device': mobile_device['device'],
			'macs': macs,
			'ips': ips,
			'software': software
		})
		
		if 'last_inventory_update' in general and general['last_inventory_update']:
			deviceData['device_custom_fields'].append({
				'name' : name,
				'key' : 'last_inventory_update', 
				'value' : general['last_inventory_update']
			})

		if 'phone_number' in general and general['phone_number']:
			deviceData['device_custom_fields'].append({
				'name' : name,
				'key' : 'phone_number', 
				'value' : general['phone_number']
			})
		
		if enduser:
			deviceData['endusers'].append(enduser)
			deviceData['device_custom_fields'].append({
				'name' : name,
				'key' : 'user', 
				'value' : enduser['name'], 
				'type' : 'related_field', 
				'related_field_name' : 'endusers'
			})

	return deviceData


if __name__ == '__main__':
	elements = main()

	# Bulk import of devices
	deviceCount = 0
	for element in elements['devices']:
		print device42_api.bulk(element)
		deviceCount +=1
			
	# Import of end users and end user custom fields
	for element in elements['endusers']:
		data = {
			'name' : element['name'], 
			'email' : element['email']
		}
		print device42_api.post_enduser(data)

		if element['custom_fields']:
			for key, value in element['custom_fields'].items():
				data = {
					'name' : element['name'], 
					'key' : key, 
					'value' : value
				}
				print device42_api.put_enduserCF(data)

		# Import of device custom fields
	if elements['device_custom_fields']:
		for element in elements['device_custom_fields']:
			print device42_api.put_deviceCF(element)

	print '\n Finished'
	print '\n %s devices created or updated' %deviceCount
