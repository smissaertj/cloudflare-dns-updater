# Public IP

This script is an alternative to popular Dynamic DNS providers like noip.com or dyno.com.
It fetches the current public IP address for the host it is run on from ipify.org and sets that IP address as a value 
for a DNS record in Cloudflare DNS, if the values do not match.  

An email notification is sent via Sendgrid when a domain is updated or when an error occurs.  

Repository:  
https://github.com/smissaertj/cloudflare-dns-updater  

Cloudflare API v4 Documentation:  
https://api.cloudflare.com/

Ipify API Documentation:  
https://www.ipify.org/

## Instructions
- Clone the repository
- Install the requirements: `pip3 install -r requirements.txt`
- Rename the `config.json.example` file to `config.json` and populate it.


### Logging
When the script is executed, a `public-ip-updater.log` file is updated under the home directory of the user executing the script.
The log file contains debug information. 