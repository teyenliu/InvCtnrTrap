'''
Created on Sep 7, 2011

@author: liudanny
'''

import socket
import os
import time
from ConfigParser import SafeConfigParser


CONF_FILE = "InvCtnrTrap.conf"
PID_FILE = "InvCtnrTrap.pid"

SNMPTRAPD_DESTINATION = ["'127.0.0.1'"]
SNMPTRAP_PORT = "162"
SNMPTRAP_COMMUNITY = "public"
SNMPTRAP_ENTERPRISE_OID = "'.1.3.6.1.4.1.6569'"
SNMPTRAP_MSG_NUMBER = 6; # general trap msg 0~5, enterprise 6
SNMPTRAP_SPECIAL_NUMBER = 0; #non-useful
SNMPTRAP_OBJ_OID = "" # for instance: '.1.3.6.1.4.1.2789.1247.1'"
SNMPTRAP_OBJ_TYPE = "string"
 
SNMPTRAP_V1 = "snmptrap -v 1 -c public {0} {1} {2} {3} {4} {5} {6} s {7}"
SNMPTRAP_V2 = "snmptrap -v 2c -c public {0} {1} {2} {3} s {4}"

RACK_NUM = 12
FAN_TRAY_NUM = 60

CONTAINER_THERMAL_COOLING_OID = {
                                 '010101020003':"'.1.3.6.1.4.1.6569.6165.1'", 
                                 '010101020004':"'.1.3.6.1.4.1.6569.6165.2'",
                                 '010101020005':"'.1.3.6.1.4.1.6569.6165.3'",
                                 '010101020006':"'.1.3.6.1.4.1.6569.6165.4'",
                                 '010101020007':"'.1.3.6.1.4.1.6569.6165.5'",
                                 '010101020008':"'.1.3.6.1.4.1.6569.6165.6'",
                                 '010101020009':"'.1.3.6.1.4.1.6569.6165.7'",
                                 '01010102000A':"'.1.3.6.1.4.1.6569.6165.8'",
                                 '010400020200':"'.1.3.6.1.4.1.6569.6165.9'",
                                 '030000020000':"'.1.3.6.1.4.1.6569.6165.10'",
                                 '020B00020001':"'.1.3.6.1.4.1.6569.6165.11'",
                                 '020B00020002':"'.1.3.6.1.4.1.6569.6165.12'",
                                 '020B00020003':"'.1.3.6.1.4.1.6569.6165.13'",
                                 '020B00020004':"'.1.3.6.1.4.1.6569.6165.14'",
                                 '020B00020005':"'.1.3.6.1.4.1.6569.6165.15'",
                                 '020B00020006':"'.1.3.6.1.4.1.6569.6165.16'",
                                 '03000002000C':"'.1.3.6.1.4.1.6569.6165.17'"
                                }

server_start_time = time.time()

def getUpTime():
    return str(int(round(time.time() - server_start_time, 0)))

class UDPParser():
    
    def sendTrap(self, trap_cmd):
        os.system(trap_cmd)
        print "Result ==> ", trap_cmd

    def judge(self, _key, _payload, ni_addr):
        print "key:", _key, "payload:", _payload
        
        msg = ''
        payload_len = _payload.__len__()
        
        # Get the correct OID
        SNMPTRAP_OBJ_OID = CONTAINER_THERMAL_COOLING_OID.get(_key)
        
        # format string description
        desc_str = "'" + _payload + "'"

        # Generate the snmptrap command string
        for trap_ip in SNMPTRAPD_DESTINATION:
            trap_cmd = SNMPTRAP_V1.format(trap_ip, SNMPTRAP_ENTERPRISE_OID, ni_addr, SNMPTRAP_MSG_NUMBER, SNMPTRAP_SPECIAL_NUMBER, 
                           getUpTime(), SNMPTRAP_OBJ_OID, desc_str)
            self.sendTrap(trap_cmd)
        
            trap_cmd = SNMPTRAP_V2.format(trap_ip, getUpTime(),
            SNMPTRAP_ENTERPRISE_OID, SNMPTRAP_OBJ_OID, desc_str)
            self.sendTrap(trap_cmd)
        
    
    def parse(self, data, ni_addr):
        if(data.__len__() > 12):
            key = data[0:12]
            payload = data[12:]
            
            self.judge(key, payload, ni_addr)
        else:
            return

class UDPServer():
    
    # Initialize the UDP Parser
    my_udp_parser = UDPParser()
    
    def __init__(self, host_ip, port):

        # Listen on port
        self.listen_addr = (host_ip, port)
        # Set up a UDP server
        self.UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.UDPSock.bind(self.listen_addr)
          
    def run(self):
        while True:
            data, addr = self.UDPSock.recvfrom(4096)
            #print "Addr:", addr, " Receive UDP data:", data.strip()
            self.my_udp_parser.parse(data, addr[1])
    
    def close(self):
        self.UDPSock.close()


''' Main Function '''
if __name__ == '__main__':
    print "InvCtnrTrap Starts..."
    
    parser = SafeConfigParser()
    parser.read(CONF_FILE)
    
    # initilize variables
    IP_List = str(parser.get('ip','trap_host')).split(',')
    for ip in IP_List:
        SNMPTRAPD_DESTINATION.append("'" + ip + "'")
    
    # Write all the lines at once:
    myfile = open(PID_FILE,"w")
    myfile.writelines(str(os.getpid()))
    myfile.close()
    
    my_udp_server = UDPServer("",10002)
    try:
        my_udp_server.run()
    except:
        print Exception.message
    finally:
        my_udp_server.close()

