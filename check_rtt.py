import csv
import netmiko
import textfsm


from getpass import getpass
from pathlib import Path

username = 'cisco'
# password = getpass()
password = 'cisco'

r1 = {"ip":"192.168.86.75","lo":"10.0.0.1"}
r2 = {"ip":"192.168.86.76","lo":"10.0.0.2"}
r3 = {"ip":"192.168.86.77","lo":"10.0.0.3"}
devices = [r1,r2,r3]


netmiko_exceptions = (netmiko.ssh_exception.NetMikoTimeoutException,
                      netmiko.ssh_exception.NetMikoAuthenticationException)

template_file = Path.cwd()/'templates'/'ping.template'

def write_csv(data,file_name):
	file = Path.cwd()/f'{file_name}.csv'
	with open(file,'w', newline='') as f:
		write = csv.writer(f)
		for rows in data:
			write.writerow(rows)

def parse_putput(data, template_file):
    with open(template_file) as template:
        re_table = textfsm.TextFSM(template)
        header = re_table.header
        result = re_table.ParseText(data)
        return(header,result)


def get_rtt():
	ping_response=[]
	header_row=['','R1','R2','R3']
	ping_response.append(header_row)
	for device in devices:
		src_ip=device['lo']
		try:
			connection = netmiko.ConnectHandler(device_type='cisco_ios', ip = device['ip'], username='cisco', password='cisco')
			router = connection.base_prompt
			tmp=[]
			tmp.append(connection.base_prompt)
			for ping_device in devices:
				if ping_device == device:
					tmp.append('-')
					continue
				output = connection.send_command(f'ping {ping_device["lo"]} source {src_ip}')
				header,delay = parse_putput(output,template_file)
				tmp.append(delay[0][0])
			ping_response.append(tmp)
			connection.disconnect()
		except netmiko_exceptions as e:
			print('Failed to ', device['ip'], e)
	return (ping_response)

def main():
	list_delay = get_rtt()
	write_csv(list_delay,'delay')

if __name__ == '__main__':
	main()