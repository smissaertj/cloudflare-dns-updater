# Public IP

A script that fetches the current public IP address from ipify.org and sets that IP address as a value 
for a DNS A record in Cloudflare DNS, if the values do not match.  

An email notification is sent via Sengrid when a domain is updated or when an error occurs.  

Repository:  
https://gitlab.com/joerismissaert/public-ip

Cloudflare API v4 Documenation:  
https://api.cloudflare.com/

Ipify API Documentation:  
https://www.ipify.org/