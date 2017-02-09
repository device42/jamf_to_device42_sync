import yaml
from jamf import JamfApi
from device42 import Device42Api
from netaddr import IPNetwork

with open('config.yaml', 'r') as cfg:
    config = yaml.load(cfg.read())

device42 = config['device42']
jamf = config['jamf']
options = config['options']

jamf_api = JamfApi(jamf, options)
device42_api = Device42Api(device42, options)


class Integration:

    def __init__(self):
        self.buildings = jamf_api.get_list('buildings')
        self.network_segments = jamf_api.get_list('networksegments')
        self.computers = jamf_api.get_list('computers')
        self.licensed_software = jamf_api.get_list('licensedsoftware')

    def add_buildings(self):
        # in current JAMF implementation ( 02.06.2017 )
        # building GET /buildings/id/{id} don't return detailed data
        # in this way we send information from GET /buildings/

        for building in self.buildings['buildings']:
            device42_api.post({
                'name': building['name']
            }, 'buildings')

    def add_networks(self):
        for network_segment in self.network_segments['network_segments']:
            network = str(IPNetwork(network_segment['starting_address'] + '/255.255.255.0').cidr).split('/')
            device42_api.post({
                'network': network[0],
                'name': network_segment['name'],
                'mask_bits': network[1],
                'range_begin': network_segment['starting_address'],
                'range_end': network_segment['ending_address']
            }, 'subnets')

    def add_computers(self):
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

                # clear -1 and POST device
                device42_api.post({k: v for (k, v) in device.items() if v != str(-1)}, 'devices')
                devices.append({
                    'general': general,
                    'software': software,
                    'purchase': purchase
                })

        return devices

    @staticmethod
    def add_device_network(general):
        if general['mac_address']:
            device42_api.post({
                'macaddress': general['mac_address'],
                'device': general['name']
            }, 'macs')

        if general['alt_mac_address']:
            device42_api.post({
                'macaddress': general['alt_mac_address'],
                'device': general['name']
            }, 'ips')

        # get previous ip and delete it if it's outdated
        previous_ips = {x['ip']: x['id'] for x in device42_api.get_list({'device': general['name']}, 'ips')['ips']}

        if general['ip_address']:
            if general['ip_address'] in previous_ips:
                previous_ips.pop(general['ip_address'], None)
            else:
                device42_api.post({
                    'ipaddress': general['ip_address'],
                    'device': general['name']
                }, 'ips')

        if general['last_reported_ip']:
            if general['last_reported_ip'] in previous_ips:
                previous_ips.pop(general['last_reported_ip'], None)
            else:
                device42_api.post({
                    'ipaddress': general['last_reported_ip'],
                    'device': general['name']
                }, 'ips')

        # remove unvalidated ips
        for ip in previous_ips:
            device42_api.delete(previous_ips[ip], 'ips')

    @staticmethod
    def add_purchases(general, purchase):
        # purchase
        a = 'is_purchased' in purchase and purchase['is_purchased']
        b = 'is_leased' in purchase and purchase['is_purchased']
        if purchase and a or b:
            already_in = False
            old_purchases = device42_api.get_list(None, 'purchases')['purchases']
            for old_purchase in old_purchases:
                for line_item in old_purchase['line_items']:
                    a = [
                        old_purchase['order_no'],
                        line_item['line_start_date'],
                        line_item['line_end_date']
                    ]
                    b = [
                        purchase['po_number'],
                        purchase['po_date'],
                        purchase['warranty_expires'] if purchase['warranty_expires'] else purchase['lease_expires']
                    ]
                    if a == b:
                        already_in = True
                        continue

            if already_in is False:
                device42_api.post({
                    'completed': 'yes',
                    'line_item_type': 'device',
                    'line_start_date': purchase['po_date'] if purchase['po_date'] else None,
                    'line_end_date': purchase['warranty_expires'] if purchase['warranty_expires']
                    else purchase['lease_expires'],
                    'line_device_serial_nos': '4312321321321', # general['serial_number'] if general['serial_number'] else None,
                    'order_no': purchase['po_number'] if purchase['po_number'] else None,
                    'line_type': 'contract' if purchase['is_purchased'] else 'device',
                    'vendor': purchase['vendor'] if purchase['vendor'] else None,
                    'cost': purchase['purchase_price'] if purchase['purchase_price'] else None,
                    'line_cost': purchase['purchase_price'] if purchase['purchase_price'] else None,
                    'po_date': purchase['po_date'] if purchase['po_date'] else None,
                    'notes': 'AppleCareID: %s' % purchase['applecare_id'] if purchase['applecare_id'] else None,
                }, 'purchases')

    @staticmethod
    def add_device_software(general, software):
        for item in software['applications']:
            # create component
            device42_api.post({
                'name': item['name'],
            }, 'software')

            # assign to device
            device42_api.post({
                'software': item['name'],
                'device': general['name'],
                'version': item['version'],
            }, 'software_details')


def main():
    integration = Integration()
    integration.add_buildings()
    integration.add_networks()

    devices = integration.add_computers()
    for device in devices:
        integration.add_device_network(device['general'])
        integration.add_device_software(device['general'], device['software'])
        integration.add_purchases(device['general'], device['purchase'])


if __name__ == '__main__':
    main()
    print '\n Finished'
