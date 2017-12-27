#!/usr/bin/env python
import subprocess
import multiprocessing
from multiprocessing import Process, Queue
import os
import time
import fileinput
import atexit
import sys
import socket

#myip = subprocess.check_output("ifconfig | grep tap0 -A1 | cut -d" " -f 10")
myip = "192.168.41.31"
start = time.time()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Creates a function for multiprocessing. Several things at once.
def multProc(targetin, scanip, port):
    jobs = []
    p = multiprocessing.Process(target=targetin, args=(scanip,port))
    jobs.append(p)
    p.start()
    return

def connect_to_port(ip_address, port, service):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip_address, int(port)))
    banner = s.recv(1024)

    if service == "ftp":
        s.send("USER anonymous\r\n")
        user = s.recv(1024)
        s.send("PASS anonymous\r\n")
        password = s.recv(1024)
        total_communication = banner + "\r\n" + user + "\r\n" + password
        write_to_file(ip_address, "ftp-connect", total_communication)
    elif service == "smtp":
        total_communication = banner + "\r\n"
        write_to_file(ip_address, "smtp-connect", total_communication)
    elif service == "ssh":
        total_communication = banner
        write_to_file(ip_address, "ssh-connect", total_communication)
    elif service == "pop3":
        s.send("USER root\r\n")
        user = s.recv(1024)
        s.send("PASS root\r\n")
        password = s.recv(1024)
        total_communication = banner +  user +  password
        write_to_file(ip_address, "pop3-connect", total_communication)
    s.close()



def write_to_file(ip_address, enum_type, data):
    file_path_linux = '/root/Dropbox/Engagements/%s/mapping-linux.md' % (ip_address)
    file_path_windows = '/root/Dropbox/Engagements/%s/mapping-windows.md' % (ip_address)
    paths = [file_path_linux, file_path_windows]
    print bcolors.OKGREEN + "INFO: Writing " + enum_type + " to template files:\n " + file_path_linux + "   \n" + file_path_windows + bcolors.ENDC

    for path in paths:
        if enum_type == "portscan":
            subprocess.check_output("replace INSERTTCPSCAN \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "dirb":
            subprocess.check_output("replace INSERTDIRBSCAN \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "nikto":
            subprocess.check_output("replace INSERTNIKTOSCAN \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "ftp-connect":
            subprocess.check_output("replace INSERTFTPTEST \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "smtp-connect":
            subprocess.check_output("replace INSERTSMTPCONNECT \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "ssh-connect":
            subprocess.check_output("replace INSERTSSHCONNECT \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "pop3-connect":
            subprocess.check_output("replace INSERTPOP3CONNECT \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "curl":
            subprocess.check_output("replace INSERTCURLHEADER \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "wig":
            subprocess.check_output("replace INSERTWIGSCAN \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "smbmap":
            subprocess.check_output("replace INSERTSMBMAP \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "rpcmap":
            subprocess.check_output("replace INSERTRPCMAP \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "samrdump":
            subprocess.check_output("replace INSERTSAMRDUMP \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "vulnscan":
            subprocess.check_output("replace INSERTVULNSCAN \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "nfsscan":
            subprocess.check_output("replace INSERTNFSSCAN \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "ssl-scan":
            subprocess.check_output("replace INSERTSSLSCAN \"" + data + "\"  -- " + path, shell=True)
    return

def dirb(ip_address, port, url_start):
    print bcolors.HEADER + "INFO: Starting dirb scan for " + ip_address + bcolors.ENDC
    DIRBSCAN = "gobuster -u %s://%s:%s -w /usr/share/wordlists/dirb/common.txt -t 100 > /root/Dropbox/Engagements/%s/dirb-%s.txt" % (url_start, ip_address, port, ip_address, ip_address)
    #DIRBSCAN = "dirb %s://%s:%s -S -o /root/Dropbox/Engagements/%s/dirb-%s.txt" % (url_start, ip_address, port, ip_address, ip_address)
    print bcolors.HEADER + DIRBSCAN + bcolors.ENDC
    results_dirb = subprocess.check_output(DIRBSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with dirb scan for " + ip_address + bcolors.ENDC
    print results_dirb
    write_to_file(ip_address, "dirb", results_dirb)
    return

def wig(ip_address, port, url_start):
    print bcolors.HEADER + "INFO: Starting wig scan for " + ip_address + bcolors.ENDC
    WIGSCAN = "wig-git %s://%s:%s -a -m  -w /root/Dropbox/Engagements/%s/wig-%s.txt | sed -r 's/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g'" % (url_start, ip_address, port, ip_address, ip_address)
    print bcolors.HEADER + WIGSCAN + bcolors.ENDC
    results_wig = subprocess.check_output(WIGSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with wig scan for " + ip_address + bcolors.ENDC
    print results_wig
    write_to_file(ip_address, "wig", results_wig)
    return

def nikto(ip_address, port, url_start):
    print bcolors.HEADER + "INFO: Starting nikto scan for " + ip_address + bcolors.ENDC
    NIKTOSCAN = "nikto -h %s://%s:%s -o /root/Dropbox/Engagements/%s/nikto-%s-%s:%s.txt" % (url_start, ip_address, port, ip_address, url_start, ip_address, port)
    print bcolors.HEADER + NIKTOSCAN + bcolors.ENDC
    results_nikto = subprocess.check_output(NIKTOSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with NIKTO-scan for " + ip_address + bcolors.ENDC
    print results_nikto
    write_to_file(ip_address, "nikto", results_nikto)
    return

def httpEnum(ip_address, port):
    print bcolors.HEADER + "INFO: Detected http on " + ip_address + ":" + port + bcolors.ENDC
    print bcolors.HEADER + "INFO: Performing nmap web script scan for " + ip_address + ":" + port + bcolors.ENDC
    dirb_process = multiprocessing.Process(target=dirb, args=(ip_address,port,"http"))
    dirb_process.start()
    nikto_process = multiprocessing.Process(target=nikto, args=(ip_address,port,"http"))
    nikto_process.start()
    wig_process = multiprocessing.Process(target=wig, args=(ip_address,port,"http"))
    wig_process.start()
    #CURLSCAN = "curl -I http://%s" % (ip_address)
    #print bcolors.HEADER + CURLSCAN + bcolors.ENDC
    #curl_results = subprocess.check_output(CURLSCAN, shell=True)
    #write_to_file(ip_address, "curl", curl_results)
    #print curl_results
    return

def httpsEnum(ip_address, port):
    print bcolors.HEADER + "INFO: Detected https on " + ip_address + ":" + port + bcolors.ENDC
    print bcolors.HEADER + "INFO: Performing nmap web script scan for " + ip_address + ":" + port + bcolors.ENDC
    dirb_process = multiprocessing.Process(target=dirb, args=(ip_address,port,"https"))
    dirb_process.start()
    nikto_process = multiprocessing.Process(target=nikto, args=(ip_address,port,"https"))
    nikto_process.start()
    wig_process = multiprocessing.Process(target=wig, args=(ip_address,port,"https"))
    wig_process.start()
    SSLSCAN = "sslscan %s:%s >> /root/Dropbox/Engagements/%s/ssl_scan_%s" % (ip_address, port, ip_address, ip_address)
    print bcolors.HEADER + SSLSCAN + bcolors.ENDC
    ssl_results = subprocess.check_output(SSLSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: CHECK FILE - Finished with SSLSCAN for " + ip_address + bcolors.ENDC
    write_to_file(ip_address, "ssl-scan", ssl_results)
    #HTTPSCANS = "nmap -sV -Pn -vv -p %s --script=http-vhosts,http-userdir-enum,http-apache-negotiation,http-backup-finder,http-config-backup,http-default-accounts,http-methods,http-method-tamper,http-passwd,http-robots.txt,http-devframework,http-enum,http-frontpage-login,http-git,http-iis-webdav-vuln,http-php-version,http-robots.txt,http-shellshock,http-vuln-cve2015-1635 -oN /root/Dropbox/Engagements/%s/%s_http.nmap %s" % (port, ip_address, ip_address, ip_address)
    #print bcolors.HEADER + HTTPSCANS + bcolors.ENDC
    #https_results = subprocess.check_output(HTTPSCANS, shell=True)
    #print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with HTTPS-scan for " + ip_address + bcolors.ENDC
    #print https_results
    return

def mssqlEnum(ip_address, port):
    print bcolors.HEADER + "INFO: Detected MS-SQL on " + ip_address + ":" + port + bcolors.ENDC
    print bcolors.HEADER + "INFO: Performing nmap mssql script scan for " + ip_address + ":" + port + bcolors.ENDC
    MSSQLSCAN = "nmap -sV -Pn -p %s --script=ms-sql-info,ms-sql-config,ms-sql-dump-hashes --script-args=mssql.instance-port=1433,smsql.username-sa,mssql.password-sa -oN /root/Dropbox/Engagements/%s/mssql_%s.nmap %s" % (port, ip_address, ip_address)
    print bcolors.HEADER + MSSQLSCAN + bcolors.ENDC
    mssql_results = subprocess.check_output(MSSQLSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with MSSQL-scan for " + ip_address + bcolors.ENDC
    print mssql_results
    return

def smtpEnum(ip_address, port):
    print bcolors.HEADER + "INFO: Detected smtp on " + ip_address + ":" + port  + bcolors.ENDC
    connect_to_port(ip_address, port, "smtp")
    SMTPSCAN = "nmap -sV -Pn -p %s --script=smtp-commands,smtp-enum-users,smtp-vuln-cve2010-4344,smtp-vuln-cve2011-1720,smtp-vuln-cve2011-1764 %s -oN /root/Dropbox/Engagements/%s/smtp_%s.nmap" % (port, ip_address, ip_address, ip_address)
    print bcolors.HEADER + SMTPSCAN + bcolors.ENDC
    smtp_results = subprocess.check_output(SMTPSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with SMTP-scan for " + ip_address + bcolors.ENDC
    print smtp_results
    write_to_file(ip_address, "smtp-connect", smtp_results)
    return
    
def smbEnum(ip_address, port):
    print "INFO: Detected SMB on " + ip_address + ":" + port
    print bcolors.HEADER + "INFO: Performing SMB based scans for " + ip_address + ":" + port + bcolors.ENDC
    SMBMAP = "smbmap -H %s -R > /root/Dropbox/Engagements/%s/smbmap_%s" % (ip_address, ip_address, ip_address)
    smbmap_results = subprocess.check_output(SMBMAP, shell=True)
    print bcolors.OKGREEN + "INFO: CHECK FILE - Finished with SMBMap-scans for " + ip_address + bcolors.ENDC
    print smbmap_results
    write_to_file(ip_address, "smbmap", smbmap_results)
    return

def rpcEnum(ip_address, port): 
    print bcolors.HEADER + "INFO: Detected RPC on " + ip_address + ":" + port  + bcolors.ENDC
    RPCMAP = "impacket-rpcdump %s  > /root/Dropbox/Engagements/%s/rpcmap_%s" % (ip_address, ip_address, ip_address)
    rpcmap_results = subprocess.check_output(RPCMAP, shell=True)
    print bcolors.OKGREEN + "INFO: CHECK FILE - Finished with RPC-scans for " + ip_address + bcolors.ENDC
    print rpcmap_results
    write_to_file(ip_address, "rpcmap", rpcmap_results)
    return

def samrEnum(ip_address, port):
    print bcolors.HEADER + "INFO: Detected SAMR on " + ip_address + ":" + port  + bcolors.ENDC
    SAMRDUMP = "impacket-samrdump %s > /root/Dropbox/Engagements/%s/samrdump_%s" % (ip_address, ip_address, ip_address)
    samrdump_results = subprocess.check_output(SAMRDUMP, shell=True)
    print bcolors.OKGREEN + "INFO: CHECK FILE - Finished with samrdump-scans for " + ip_address + bcolors.ENDC
    print samrdump_results
    write_to_file(ip_address, "samrdump", samrdump_results)
    return

def ftpEnum(ip_address, port):
    print bcolors.HEADER + "INFO: Detected ftp on " + ip_address + ":" + port  + bcolors.ENDC
    connect_to_port(ip_address, port, "ftp")
    FTPSCAN = "nmap -sV -Pn -vv -p %s --script=ftp-anon,ftp-bounce,ftp-libopie,ftp-proftpd-backdoor,ftp-vsftpd-backdoor,ftp-vuln-cve2010-4221 -oN '/root/Dropbox/Engagements/%s/ftp_%s.nmap' %s" % (port, ip_address, ip_address, ip_address)
    print bcolors.HEADER + FTPSCAN + bcolors.ENDC
    results_ftp = subprocess.check_output(FTPSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with FTP-Nmap-scan for " + ip_address + bcolors.ENDC
    print results_ftp
    return

def udpScan(ip_address):
    print bcolors.HEADER + "INFO: Detected UDP on " + ip_address + bcolors.ENDC
    UDPSCAN = "nmap -vv -Pn -A -sC -sU -T 4 --top-ports 200 -oN '/root/Dropbox/Engagements/%s/udp_%s.nmap' %s"  % (ip_address, ip_address, ip_address)
    print bcolors.HEADER + UDPSCAN + bcolors.ENDC
    udpscan_results = subprocess.check_output(UDPSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with UDP-Nmap scan for " + ip_address + bcolors.ENDC
    print udpscan_results
    UNICORNSCAN = "unicornscan -mU -v -I %s > /root/Dropbox/Engagements/%s/unicorn_udp_%s.txt" % (ip_address, ip_address, ip_address)
    unicornscan_results = subprocess.check_output(UNICORNSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: CHECK FILE - Finished with UNICORNSCAN for " + ip_address + bcolors.ENDC

def nfsEnum(ip_address, port):
    print bcolors.HEADER + "INFO: Detected NFS on " + ip_address + bcolors.ENDC
    SHOWMOUNT = "showmount -e %s > '/root/Dropbox/Engagements/%s/nfs_%s.nmap'"  % (ip_address, ip_address, ip_address)
    print bcolors.HEADER + SHOWMOUNT + bcolors.ENDC
    nfsscan_results = subprocess.check_output(SHOWMOUNT, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with NFS scan for " + ip_address + bcolors.ENDC
    print nfsscan_results
    write_to_file(ip_address, "nfsscan", nfsscan_results)

def sshScan(ip_address, port):
    print bcolors.HEADER + "INFO: Detected SSH on " + ip_address + ":" + port  + bcolors.ENDC
    connect_to_port(ip_address, port, "ssh")

def pop3Scan(ip_address, port):
    print bcolors.HEADER + "INFO: Detected POP3 on " + ip_address + ":" + port  + bcolors.ENDC
    connect_to_port(ip_address, port, "pop3")

def vulnEnum(ip_address):
    print bcolors.HEADER + "INFO: Detected vulns on " + ip_address  + bcolors.ENDC
    print bcolors.HEADER + "INFO: Performing Vulnerability based scans for " + ip_address + bcolors.ENDC
    VULN = "nmap --script=vuln %s -oN /root/Dropbox/Engagements/%s/vuln_%s.nmap" % (ip_address, ip_address, ip_address)
    vuln_results = subprocess.check_output(VULN, shell=True)
    print bcolors.OKGREEN + "INFO: CHECK FILE - Finished with Vuln-scans for " + ip_address + bcolors.ENDC
    print vuln_results
    write_to_file(ip_address, "vulnscan", vuln_results)
    return

def nmapScan(ip_address):
    ip_address = ip_address.strip()
    print bcolors.OKGREEN + "INFO: Running general TCP/UDP nmap scans for " + ip_address + bcolors.ENDC
    TCPSCAN = "nmap -sV -O %s -oN '/root/Dropbox/Engagements/%s/%s.nmap'"  % (ip_address, ip_address, ip_address)
    print bcolors.HEADER + TCPSCAN + bcolors.ENDC
    results = subprocess.check_output(TCPSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with BASIC Nmap-scan for " + ip_address + bcolors.ENDC
    print results
    p = multiprocessing.Process(target=udpScan, args=(scanip,))
    p.start()
    l = multiprocessing.Process(target=vulnEnum, args=(scanip,))
    l.start()
    write_to_file(ip_address, "portscan", results)
    lines = results.split("\n")
    serv_dict = {}
    for line in lines:
        ports = []
        line = line.strip()
        if ("tcp" in line) and ("open" in line) and not ("Discovered" in line):
            # print line
            while "  " in line:
                line = line.replace("  ", " ");
            linesplit= line.split(" ")
            service = linesplit[2] # grab the service name

            port = line.split(" ")[0] # grab the port/proto
            # print port
            if service in serv_dict:
                ports = serv_dict[service] # if the service is already in the dict, grab the port list

            ports.append(port)
            # print ports
            serv_dict[service] = ports # add service to the dictionary along with the associated port(2)



   # go through the service dictionary to call additional targeted enumeration functions
    for serv in serv_dict:
        ports = serv_dict[serv]
        if (serv == "http") or (serv == "http-proxy") or (serv == "http-alt") or (serv == "http?"):
            for port in ports:
                port = port.split("/")[0]
                multProc(httpEnum, ip_address, port)
        elif (serv == "ssl/http") or ("https" == serv) or ("https?" == serv):
            for port in ports:
                port = port.split("/")[0]
                multProc(httpsEnum, ip_address, port)
        elif "smtp" in serv:
            for port in ports:
                port = port.split("/")[0]
                multProc(smtpEnum, ip_address, port)
        elif "ftp" in serv:
            for port in ports:
                port = port.split("/")[0]
                multProc(ftpEnum, ip_address, port)
        elif ("microsoft-ds" in serv) or ("netbios-ssn" == serv):
            for port in ports:
                port = port.split("/")[0]
                multProc(smbEnum, ip_address, port)
                multProc(rpcEnum, ip_address, port)
                multProc(samrEnum, ip_address, port)
        elif "ms-sql" in serv:
            for port in ports:
                port = port.split("/")[0]
                multProc(mssqlEnum, ip_address, port)
        elif "rpcbind" in serv:
            for port in ports:
                port = port.split("/")[0]
                multProc(nfsEnum, ip_address, port)
        elif "ssh" in serv:
            for port in ports:
                port = port.split("/")[0]
                multProc(sshScan, ip_address, port)
      #  elif:
       #     multProc(vulnEnum, ip_address, 80)
        #elif "snmp" in serv:
        #    for port in ports:
        #        port = port.split("/")[0]
        #        multProc(snmpEnum, ip_address, port)
  #     elif ("domain" in serv):
    #  for port in ports:
     #    port = port.split("/")[0]
     #    multProc(dnsEnum, ip_address, port)

    return


print bcolors.HEADER
print "------------------------------------------------------------"
print "!!!!                      RECON SCAN                   !!!!!"
print "!!!!            A multi-process service scanner        !!!!!"
print "!!!!        dirb, nikto, ftp, ssh, mssql, pop3, tcp    !!!!!"
print "!!!!                    udp, smtp, smb                 !!!!!"
print "------------------------------------------------------------"



if len(sys.argv) < 2:
    print ""
    print "Usage: python reconscan.py <ip> <ip> <ip>"
    print "Example: python reconscan.py 192.168.1.101 192.168.1.102"
    print ""
    print "############################################################"
    pass
    sys.exit()

print bcolors.ENDC

if __name__=='__main__':

    # Setting ip targets
    targets = sys.argv
    targets.pop(0)

    dirs = os.listdir("/root/Dropbox/Engagements/")
    for scanip in targets:
        scanip = scanip.rstrip()
        if not scanip in dirs:
            print bcolors.HEADER + "INFO: No folder was found for " + scanip + ". Setting up folder." + bcolors.ENDC
            subprocess.check_output("mkdir /root/Dropbox/Engagements/" + scanip, shell=True)
            subprocess.check_output("mkdir /root/Dropbox/Engagements/" + scanip + "/exploits", shell=True)
            subprocess.check_output("mkdir /root/Dropbox/Engagements/" + scanip + "/privesc", shell=True)
            print bcolors.OKGREEN + "INFO: Folder created here: " + "/root/Dropbox/Engagements/" + scanip + bcolors.ENDC
            subprocess.check_output("cp /root/Dropbox/Scripts/oscp/windows-template.md /root/Dropbox/Engagements/" + scanip + "/mapping-windows.md", shell=True)
            subprocess.check_output("cp /root/Dropbox/Scripts/oscp/linux-template.md /root/Dropbox/Engagements/" + scanip + "/mapping-linux.md", shell=True)
            print bcolors.OKGREEN + "INFO: Added pentesting templates: " + "/root/Dropbox/Engagements/" + scanip + bcolors.ENDC
            subprocess.check_output("sed -i -e 's/INSERTIPADDRESS/" + scanip + "/g' /root/Dropbox/Engagements/" + scanip + "/mapping-windows.md", shell=True)
            subprocess.check_output("sed -i -e 's/MYIPADDRESS/" + myip + "/g' /root/Dropbox/Engagements/" + scanip + "/mapping-windows.md", shell=True)
            subprocess.check_output("sed -i -e 's/INSERTIPADDRESS/" + scanip + "/g' /root/Dropbox/Engagements/" + scanip + "/mapping-linux.md", shell=True)
            subprocess.check_output("sed -i -e 's/MYIPADDRESS/" + myip + "/g' /root/Dropbox/Engagements/" + scanip + "/mapping-linux.md", shell=True)
           



        p = multiprocessing.Process(target=nmapScan, args=(scanip,))
        p.start()
