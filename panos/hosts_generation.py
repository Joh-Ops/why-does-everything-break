def generate_hosts(ip, portrange):
	start, end = [int(limit) for limit in portrange.split('-')]
	return [f'{ip}:{port}' for port in range(start, end)]
