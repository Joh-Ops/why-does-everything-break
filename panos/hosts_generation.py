from random import choice

def generate_hosts(ip, portrange):
	start, end = [int(limit) for limit in portrange.split('-')]
	return [f'{ip}:{port}' for port in range(start, end)]

def randomize_hosts(ips, portrange):
	return generate_hosts(choice(ips), portrange)