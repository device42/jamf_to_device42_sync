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


class Integration:

    def __init__(self):
        self.computers = jamf_api.get_list('computers')

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
                    'hardware': hardware['model'] if hardware['model'] else None,
                    'os': hardware['os_name'] if hardware['os_name'] else None,
                    'osver': hardware['os_version'] if hardware['os_version'] else None,
                    'memory': hardware['total_ram_mb'] if hardware['total_ram_mb'] else None,
                    'cpucount': hardware['number_processors'] if hardware['number_processors'] else None,
                    'tags': general['asset_tag'] if general['asset_tag'] else None
                })

                if general['serial_number']:
                    device['serial_no'] = general['serial_number']

                if hardware['processor_speed_mhz']:
                    device['cpupower'] = hardware['processor_speed_mhz']

                if hardware['number_cores']:
                    device['cpucore'] = hardware['number_cores']

                devices.append({
                    'device': {k: v for (k, v) in device.items() if str(v) != str(-1)},
                    'general': general,
                    'software': software,
                    'purchase': purchase
                })

        return devices

    @staticmethod
    def get_device_network(general):
        macs = []
        ips = []
        if general['mac_address']:
            macs.append({
                'macaddress': general['mac_address'],
            })

        if general['alt_mac_address']:
            macs.append({
                'macaddress': general['alt_mac_address'],
            })

        if general['ip_address']:
            ips.append({
                'ipaddress': general['ip_address'],
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
            software.append({
                'software': item['name'],
                'version': item['version'],
            })

        return software


def main():
    integration = Integration()

    devices = integration.get_computers()
    data = {
        'devices': []
    }
    for device in devices:
        macs, ips = integration.get_device_network(device['general'])
        software = integration.get_device_software(device['software'])

        if options['no_ips']:
            ips = []

        data['devices'].append({
            'device': device['device'],
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
