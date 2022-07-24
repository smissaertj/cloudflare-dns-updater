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
import logging
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename=os.path.join(os.environ.get('HOME'), 'public-ip-updater.log'),
                    filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')


class Domain():
    def __init__(self, data, current_public_ip):
        self.zone_id = data['cloudflare_zone_id']
        self.name = data['domain_name']
        self.record_type = 'A'
        self.content = current_public_ip
        self.proxied = data['proxied']
        self.ttl = data['ttl']

    def send_notification(self, content):
        message = Mail(
            from_email=config_data['from_email'],
            to_emails=config_data['to_email'],
            subject=f'DNS Record Update for {self.name}',
            html_content=content)

        try:
            sg = SendGridAPIClient(config_data['sendgrid_api_key'])
            response = sg.send(message)
            logging.debug(message)
        except Exception as error:
            logging.error(error)

    def current_dns_value(self):
        """ Identify current record values on Cloudflare """
        try:
            response = requests.get(config_data[
                                        'cloudflare_api_base_url'] + "/zones/" + self.zone_id + "/dns_records/?type=" + self.record_type + "&name=" + self.name,
                                    headers=cf_api_headers)
            json_data = json.loads(response.content)
        except Exception as error:
            logging.error(error)
        else:
            if response.status_code == 200:
                return json_data["result"][0]

    def update_dns(self):
        """ Update the CF domain DNS record with self.content when required """
        current_data = self.current_dns_value()
        domain_id = current_data['id']
        new_data = {"type": self.record_type, "name": self.name, "content": self.content, "ttl": self.ttl,
                    "proxied": self.proxied}

        if current_data['content'] != new_data['content']:
            try:
                response = requests.put(
                    config_data['cloudflare_api_base_url'] + "/zones/" + self.zone_id + "/dns_records/" + domain_id,
                    headers=cf_api_headers,
                    data=json.dumps(new_data))
            except Exception as error:
                logging.error(error)
            else:
                if response.status_code == 200:
                    self.send_notification(f"Domain DNS {self.record_type} Record updated: {public_ip}")
                else:
                    response = json.loads(response.content)
                    logging.error(response)
                    self.send_notification(f"Error updating domain DNS {self.record_type} record:\n{response}")
                return


def get_public_ip(api_url):
    """ Identify current public IP address"""
    try:
        response = requests.get(api_url)
        json_data = json.loads(response.content)
    except Exception as error:
        logging.error(error)
    else:
        return json_data["ip"]


def read_config():
    """ Reads the config.json file """
    file_path = os.path.join(os.path.dirname(__file__), 'config.json')

    with open(file_path, 'r') as config_file:
        data = json.load(config_file)

    return data


if __name__ == '__main__':
    # Read config.json
    config_data = read_config()

    # Get the current Public IP
    public_ip = get_public_ip(config_data['ipify_url'])

    # Headers to be sent with requests to the Cloudflare API
    cf_api_headers = {"X-Auth-Email": config_data['cloudflare_x_auth_email'],
                      "X-Auth-Key": config_data['cloudflare_api_key'], "Content-Type": "application/json"}

    # Create a list of domain objects
    domains = [Domain(domain_data, public_ip) for domain_data in config_data['domain_settings']]

    # Call the .update_dns() method on each domain object
    list(map(lambda domain: domain.update_dns(), domains))
