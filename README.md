# jamfexplore
Script to sync JAMF to Device42 (http://www.device42.com)
This script was tested with JSS v9.97.1483031164 and Device42 v12.

# Requirements
Take the file `config.yaml.example` and rename it to `config.yaml`. Then change the settings to correct ones.
Please install requirements `pip install -r requirements.txt`

# Run
Puppet :
```
python starter.py
```

# Specification
Current script version migrate `devices, ips, macs and software data`. If you have any requests\improvements, feel free to contact us.