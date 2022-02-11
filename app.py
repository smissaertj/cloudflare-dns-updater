#!/usr/bin/env python3

"""
A script that fetches the current public IP address from ipify.org and sets that IP address as a value 
for a DNS A record in Cloudflare DNS, if the values do not match.

An email notification is sent via Sengrid when a domain is updated or when an error occurs.

Repository:
https://gitlab.com/joerismissaert/public-ip

Cloudflare API v4 Documenation:
https://api.cloudflare.com/

Ipify API Documentation:
https://www.ipify.org/
"""

import requests
import json
import sys
import logging
import os
from decouple import config
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# API Endpoints
IPIFY_URL = "https://api.ipify.org?format=json"
CLOUDFLARE_API_BASE_URL = "https://api.cloudflare.com/client/v4"

# Load Secrets/Configs from .env file
SENDGRID_API_KEY = config('SENDGRID_API_KEY')
CLOUDFLARE_API_KEY = config('CLOUDFLARE_API_KEY')
CLOUFLARE_X_AUTH_EMAIL = config('CLOUFLARE_X_AUTH_EMAIL')
CLOUDFLARE_ZONE_ID = config('CLOUDFLARE_ZONE_ID')
CF_DOMAIN = config('CF_DOMAIN')
DNS_RECORD_TYPE = config('DNS_RECORD_TYPE')
FROM_EMAIL = config('FROM_EMAIL')
TO_EMAIL = config('TO_EMAIL')

# Headers to be sent with requests to the Cloudflare API
cf_api_headers = {"X-Auth-Email": CLOUFLARE_X_AUTH_EMAIL, "X-Auth-Key": CLOUDFLARE_API_KEY, "Content-Type": "application/json"}

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename=os.path.join(os.environ.get('HOME'),'app.log'), filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

# Functions
def send_notification(content):
    message = Mail(
    from_email=FROM_EMAIL,
    to_emails=TO_EMAIL,
    subject=f'Public IP Update for {CF_DOMAIN}',
    html_content=content)

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
    except Exception as error:
        logging.error(error)


def get_public_ip():
    """ Identify current public IP address""" 

    try:
        response = requests.get(IPIFY_URL)
        json_data = json.loads(response.content)
    except Exception as error:
        logging.error(error)
    else:
        return json_data["ip"]


def get_domain_dns(domain):
    """ Identify current record values on Cloudflare """
    try:
        response = requests.get(CLOUDFLARE_API_BASE_URL + "/zones/" + CLOUDFLARE_ZONE_ID + "/dns_records/?type=" + DNS_RECORD_TYPE + "&name=" + domain, headers=cf_api_headers)
        json_data = json.loads(response.content)
    except Exception as error:
        logging.error(error)
    else:
        if response.status_code == 200:
            return json_data["result"][0]


def update_domain_dns(public_ip, domain_id):
    """ Update the CF domain DNS A record with the value of public_ip """

    data = {"type": DNS_RECORD_TYPE, "name": CF_DOMAIN, "content": public_ip, "ttl": 3600, "proxied": True}

    try:
        response = requests.put(CLOUDFLARE_API_BASE_URL + "/zones/" + CLOUDFLARE_ZONE_ID + "/dns_records/" + domain_id, headers=cf_api_headers, data=json.dumps(data))
    except Exception as error:
        logging.error(error)
    else:
        if response.status_code == 200:
            send_notification(f"Domain DNS A Record updated: {public_ip}")
        else:
            response = json.loads(response.content)
            send_notification(f"Error updating domain DNS A record:\n{response}")
        return


def main():
    """ Entrypoint """

    public_ip = get_public_ip()
    current_dns_value = get_domain_dns(CF_DOMAIN)
    logging.debug(f'Public IP: {public_ip} - Current DNS Value: {current_dns_value}')

    if public_ip != current_dns_value['content']:
        domain_id = current_dns_value['id']
        update_domain_dns(public_ip, domain_id)
    else:
        logging.debug('No action needed')

main()
