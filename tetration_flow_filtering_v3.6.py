#!/usr/bin/env python

import pandas as pd
from openpyxl import load_workbook
import socket
import re
import glob
import os
import sys
import xlwt

pd.options.display.max_rows = 999

def file_check(user_input_file,user_output_file):
	json_file = bool(re.search(r'.json',user_input_file))
	excel_file = bool(re.search(r'(?:.xls|.xlsx)',user_output_file))
	if json_file == False:
		print('\nHalted - json file needs extension of .json')
		raise SystemExit(0)
	if excel_file == False:
		print('\nHalted - output file needs either a .xls or .xlsx file extension')
		raise SystemExit(0)
	print('both file extensions are acceptable, moving forward')


def json(user_input_file):
	user_input_file = ''.join(str(e) for e in user_input_file)
	df_org = pd.read_json(('{}').format(user_input_file))
	df_org = df_org.drop(df_org.columns[[1,2,3,5,9,10,11]], axis=1)
	df_org = df_org[['src_ip', 'dst_ip', 'protocol', 'portNumber', 'byteCount', 'packetCount']]
	df_src_ip = df_org[['src_ip']]
	src_ip_list = df_src_ip["src_ip"].tolist()
	df_dst_ip = df_org[['dst_ip']]
	dst_ip_list = df_dst_ip["dst_ip"].tolist()
	return src_ip_list,dst_ip_list,df_org

def dns (src_ip_list,dst_ip_list):
	dns_src_list = []
	del dns_src_list[:]
	dns_dst_list = []
	del dns_dst_list[:]
	src_ip_list_dup=[ii for n,ii in enumerate(src_ip_list) if ii not in src_ip_list[:n]]
	src_ip_list = src_ip_list_dup
	dst_ip_list_dup=[ii for n,ii in enumerate(dst_ip_list) if ii not in dst_ip_list[:n]]
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
	return dns_src_list,dns_dst_list


def dns_filter(dns_src_list,dns_dst_list):
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
	return(dns_list_src,dns_list_dst)


def sort_data (dns_list_src,dns_list_dst,df_org):
	df_dns_src = pd.DataFrame(dns_list_src, columns=['src_dns_name'])
	df_dns_src[['src_dns_name','src_ip']] = df_dns_src['src_dns_name'].str.split(' ',expand=True)
	df_dns_dst = pd.DataFrame(dns_list_dst, columns=['dst_dns_name'])
	df_dns_dst[['dst_dns_name','dst_ip']] = df_dns_dst['dst_dns_name'].str.split(' ',expand=True)
	df_new_1 = pd.merge(df_org, df_dns_src, on='src_ip', how='inner')
	df_new_2 = pd.merge(df_new_1, df_dns_dst, on='dst_ip', how='inner')
	fw_rules = df_new_2.drop_duplicates(subset=['src_ip', 'dst_ip', 'protocol', 'portNumber', 'byteCount', 'packetCount'], inplace=False)
	unique = df_new_2.drop_duplicates(subset=['src_ip'], inplace=False)
	fw_rules = fw_rules[['src_ip', 'src_dns_name', 'dst_ip', 'dst_dns_name', 'protocol', 'portNumber', 'byteCount', 'packetCount']]
	unique = unique[['src_ip', 'src_dns_name', 'dst_ip', 'dst_dns_name', 'protocol', 'portNumber', 'byteCount', 'packetCount']]
	unique = unique.drop(unique.columns[[4,5,6,7]], axis=1)
	unique = unique.reset_index(drop=True)
	fw_rules = fw_rules.reset_index(drop=True)
	return(unique,fw_rules)

#write from pd to excel format
def excel_writer(fw_rules,unique,user_output_file):
	os.system('rm -f {}.xlsx'.format(user_output_file))
	writer = pd.ExcelWriter('{}'.format(user_output_file))
	fw_rules.to_excel(writer,'flows')
	unique.to_excel(writer,'unique_flows')
	writer.save()

def main():
	if '-i' not in sys.argv and '-o' not in sys.argv:
		print("\nHalted - Please provide both input and output file names using - i (for input) and -o (for output)\n\n")
		raise SystemExit(0)
	if '-i' not in sys.argv:
		print("\nHalted - Please provide input file name using -i\n\n")
		raise SystemExit(0)
	if '-o' not in sys.argv:
		print("\nHalted - Please provide output file name using -o\n\n")
		raise SystemExit(0)
	for index,argument in enumerate(sys.argv):
		if argument == '-o':
			if (index+1) < len(sys.argv):
				user_output_file = sys.argv[index+1]
				print(user_output_file)
			else:
			# Need a valid output file after the -o argument
				print("\nHalted - No Output file provided\n\n")
				raise SystemExit(0)
		if argument == '-i':
			if (index+1) < len(sys.argv):
				user_input_file = sys.argv[index+1]
				print(user_input_file)
			else:
			# Need a valid input file after the -i argument
				print("\nHalted - No Input file provided\n\n")
				raise SystemExit(0)


	file_check(user_input_file,user_output_file)
	src_ip_list,dst_ip_list,df_org = json(user_input_file)
	dns_src_list,dns_dst_list = dns(src_ip_list,dst_ip_list)
	dns_list_src,dns_list_dst = dns_filter (dns_src_list,dns_dst_list)
	unique,fw_rules = sort_data (dns_list_src,dns_list_dst,df_org)
	excel_writer(fw_rules,unique,user_output_file)
	#used for testing
	#user_input_file = 'sample.json'
	#user_output_file = 'test.xls'

if __name__ == '__main__':
  main()





