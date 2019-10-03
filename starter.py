import sys
reload(sys)
sys.setdefaultencoding('utf8')

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

#TODO create and checkout branch D42-13883

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


def main():
    integration = Integration()

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

        if options['no_ips']:
            ips = []

        data['devices'].append({
            'device': mobile_device['device'],
            'macs': macs,
            'ips': ips,
            'software': software
        })

    return data


if __name__ == '__main__':
    elements = main()
    for element in elements['devices']:
        print device42_api.bulk(element)
    print '\n Finished'
