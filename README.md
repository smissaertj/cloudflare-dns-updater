# Public IP

This script is an alternative to popular Dynamic DNS providers like noip.com or dyno.com.
It fetches the current public IP address for the host it is run on from ipify.org and sets that IP address as a value 
for a DNS record in Cloudflare DNS, if the values do not match.  

An email notification is sent via Sendgrid when a domain is updated or when an error occurs.  

Repository:  
https://gitlab.com/joerismissaert/public-ip

Cloudflare API v4 Documenation:  
https://api.cloudflare.com/

Ipify API Documentation:  
https://www.ipify.org/

## Instructions
- Clone the repository
- Install the requirements: `pip3 install -r requirements.txt`
- Create a dot env file inside the cloned repository with the below variables:  
```
SENDGRID_API_KEY=<Sendgrid API Key>
CLOUDFLARE_API_KEY=<Cloudflare API Key>
CLOUFLARE_X_AUTH_EMAIL=<Email address associated with your Cloudflare account>
CLOUDFLARE_ZONE_ID=<Cloudflare DNS Zone ID>
CF_DOMAIN=<Domain on Cloudflare you wish to update a DNS record for>
DNS_RECORD_TYPE=<DNS Record type>
FROM_EMAIL=<From email address used for Sendgrid notifications>
TO_EMAIL=<Destination email address used for Sendgrid notifications>
```
- Setup a cronjob or Systemd Timer for recurring script execution.

### Example .env file:
```
SENDGRID_API_KEY=Scb1da762423843918d22e656dd7198be
CLOUDFLARE_API_KEY=788f776dee8e4f8d84fd422e23806c96
CLOUFLARE_X_AUTH_EMAIL=foo@bar.com
CLOUDFLARE_ZONE_ID=2be989be363346dfb6c182984ec75bf7
CF_DOMAIN=example.com
DNS_RECORD_TYPE=A
FROM_EMAIL=bar@foo.com
TO_EMAIL=foo@bar.com
```

### Logging
Each time the script is run an `app.log` file is updated under the home directory of the user executing the script.
The log file contains debug information. 