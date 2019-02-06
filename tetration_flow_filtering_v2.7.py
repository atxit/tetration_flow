#!/usr/bin/env python

import pandas as pd
from openpyxl import load_workbook
import socket
import re
import os
import glob

json = (glob.glob("*.json"))
os.system("rm -f json_to_excel_output.xlsx")
json = ''.join(str(e) for e in json)
df_org = pd.read_json(('{}').format(json))
df_org = df_org.drop(df_org.columns[[1,2,3,5,9,10,11]], axis=1)
df_org = df_org[['src_ip', 'dst_ip', 'protocol', 'portNumber', 'byteCount', 'packetCount']]

df_src_ip = df_org[['src_ip']]
src_ip_list = df_src_ip["src_ip"].tolist()

df_dst_ip = df_org[['dst_ip']]
dst_ip_list = df_dst_ip["dst_ip"].tolist()


pd.options.display.max_rows = 999

dns_src_list = []
del dns_src_list[:]


dns_dst_list = []
del dns_dst_list[:]


src_list = filter(None, src_ip_list)
src_ip_list_dup=[ii for n,ii in enumerate(src_list) if ii not in src_list[:n]]
src_ip_list = src_ip_list_dup
dst_list = filter(None, dst_ip_list)
dst_ip_list_dup=[ii for n,ii in enumerate(dst_list) if ii not in dst_list[:n]]
dst_ip_list = dst_ip_list_dup


for src_ip in src_ip_list:
	try:
		print(src_ip)
		ip_add = socket.gethostbyaddr(src_ip)
		print(ip_add)
		dns_src_list.append(ip_add)
	except:
		print("No DNS Entry")
		dns_src_list.append("No_DNS_Entry "+ src_ip)
		pass

for dst_ip in dst_ip_list:
	try:
		print(dst_ip)
		ip_add = socket.gethostbyaddr(dst_ip)
		print(ip_add)
		dns_dst_list.append(ip_add)
	except:
		print("No DNS Entry")
		dns_dst_list.append("No_DNS_Entry "+ dst_ip)
		pass

dns_list_src_str = ''.join(str(e) for e in dns_src_list)
dns_list_src_str = dns_list_src_str.replace('[]','')
dns_list_src_str = dns_list_src_str.replace(r' ','')
dns_list_src_str = dns_list_src_str.replace(r"(",'\n')
dns_list_src_str = dns_list_src_str.replace(r"'])No",'No')
dns_list_src_str = dns_list_src_str.replace('_Entry','_Entry ')
dns_list_src_str = dns_list_src_str.replace(r"'",'')
dns_list_src_str = dns_list_src_str.replace(r")",'')
dns_list_src_str = dns_list_src_str.replace(r"]",'')
dns_list_src_str = dns_list_src_str.replace(r",,[",' ')
dns_list_src_str = dns_list_src_str.replace(r"No_DNS_Entry", "\nNo_DNS_Entry")
dns_list_src_str = dns_list_src_str.lstrip("\n")
dns_list_src = dns_list_src_str.split('\n')

dns_list_dst_str = ''.join(str(e) for e in dns_dst_list)
dns_list_dst_str = dns_list_dst_str.replace('[]','')
dns_list_dst_str = dns_list_dst_str.replace(r' ','')
dns_list_dst_str = dns_list_dst_str.replace(r"(",'\n')
dns_list_dst_str = dns_list_dst_str.replace(r"'])No",'No')
dns_list_dst_str = dns_list_dst_str.replace('_Entry','_Entry ')
dns_list_dst_str = dns_list_dst_str.replace(r"'",'')
dns_list_dst_str = dns_list_dst_str.replace(r")",'')
dns_list_dst_str = dns_list_dst_str.replace(r"]",'')
dns_list_dst_str = dns_list_dst_str.replace(r",,[",' ')
dns_list_dst_str = dns_list_dst_str.replace(r"No_DNS_Entry", "\nNo_DNS_Entry")
dns_list_dst_str = dns_list_dst_str.lstrip("\n")
dns_list_dst = dns_list_dst_str.split('\n')


df_dns_src = pd.DataFrame(dns_list_src, columns=['Source DNS Name'])
df_dns_src[['Source DNS Name','src_ip']] = df_dns_src['Source DNS Name'].str.split(' ',expand=True)
df_dns_dst = pd.DataFrame(dns_list_dst, columns=['Destination DNS Name'])
df_dns_dst[['Destination DNS Name','dst_ip']] = df_dns_dst['Destination DNS Name'].str.split(' ',expand=True)



df_new_1 = pd.merge(df_org, df_dns_src, on='src_ip', how='inner')
df_new_2 = pd.merge(df_new_1, df_dns_dst, on='dst_ip', how='inner')
fw_rules = df_new_2.drop_duplicates(subset=['src_ip', 'dst_ip', 'protocol', 'portNumber', 'byteCount', 'packetCount'], inplace=False)
unique = df_new_2.drop_duplicates(subset=['src_ip'], inplace=False)
fw_rules = fw_rules[['src_ip', 'Source DNS Name', 'dst_ip', 'Destination DNS Name', 'protocol', 'portNumber', 'byteCount', 'packetCount']]
unique = unique[['src_ip', 'Source DNS Name', 'dst_ip', 'Destination DNS Name', 'protocol', 'portNumber', 'byteCount', 'packetCount']]
unique = unique.drop(unique.columns[[4,5,6,7]], axis=1)


unique = unique.reset_index(drop=True)
fw_rules = fw_rules.reset_index(drop=True)

writer = pd.ExcelWriter('json_to_excel_output.xlsx')
fw_rules.to_excel(writer,'FW rules')
unique.to_excel(writer,'unique flows')
writer.save()

