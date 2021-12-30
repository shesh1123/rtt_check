import csv
import netmiko
import textfsm
import yaml


from getpass import getpass
from pathlib import Path

username = 'cisco'
# password = getpass()
password = 'cisco'

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

def get_rtt(devices):
	ping_response=[]
	header_row = list(devices.keys())
	header_row.insert(0,'-')
	ping_response.append(header_row)
	for hostname,values in devices.items():
		src_ip=values['loop0']
		try:
			connection = netmiko.ConnectHandler(device_type='cisco_ios', ip = values['mgmt_ip'], username=username, password=password)
			tmp=[]
			tmp.append(connection.base_prompt)
			for ping_hostname,ping_values in devices.items():
				if ping_hostname == hostname:
					tmp.append('-')
					continue
				output = connection.send_command(f'ping {ping_values["loop0"]} source {src_ip}')
				header,delay = parse_putput(output,template_file)
				tmp.append(delay[0][0])
			ping_response.append(tmp)
			connection.disconnect()
		except netmiko_exceptions as e:
			print('Failed to ', device['ip'], e)
	return (ping_response)

def main():
	
	with open("devices.yml",'r') as f:
		devices = yaml.safe_load(f)
	list_delay = get_rtt(devices)
	write_csv(list_delay,'delay')

if __name__ == '__main__':
	main()