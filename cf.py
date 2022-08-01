import CloudFlare
import sys
# Initialize Cloudflare API client
cf = CloudFlare.CloudFlare(
	email="lemonhall2012@qq.com",
	token="xxxxxxxxxxxxxxxxxxxxxx"
)

def dns_updater(hostname,ipv6_address):
	# Get zone ID (for the domain). This is why we need the API key and the domain API token won't be sufficient
	zone = ".".join(hostname.split(".")[-2:]) # domain = test.mydomain.com => zone = mydomain.com
	zones = cf.zones.get(params={"name": zone})

	if len(zones) == 0:
		print(f"Could not find CloudFlare zone {zone}, please check domain {hostname}")
		sys.exit(2)

	zone_id = zones[0]["id"]

	# Fetch existing A record
	aaaa_records = cf.zones.dns_records.get(zone_id, params={"name": hostname, "type": "AAAA"})

	if len(aaaa_records): # Have an existing record
	    print("Found existing record, updating...")
	    a_record = aaaa_records[0]
	    # Update record & save to cloudflare
	    a_record["content"] = ipv6_address
	    cf.zones.dns_records.put(zone_id, a_record["id"], data=a_record)
	else: # No existing record. Create !
	    print("Record doesn't existing, creating new record...")
	    a_record = {}
	    a_record["type"] = "AAAA"
	    a_record["name"] = hostname
	    a_record["ttl"] = 60 # 1 == auto
	    a_record["content"] = ipv6_address
	    cf.zones.dns_records.post(zone_id, data=a_record)

#hostname = "docker01.lemonhall.me"
#ipv6_address= "240e:3b4:303c:d979:1000:242:ac10:c802"
dns_updater(hostname,ipv6_address)
