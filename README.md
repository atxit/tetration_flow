Propose: Takes an .json file generated from Tetration (created from ADM, filtering on a target IP) and presents the file information in more readable format (excel). Tetration was responsible for generating the original request, the output format is JSON file which displays data flows communicating with the target IP address of 172.17.69.34 (target_svr.lab.local). In this scenario, 172.17.69.34 (target_svr.lab.local) has been identified as a potential candidate for cloud migration. 

    Because of this, we need to understand:

    •	Who is communicating with this server?

    •	What ports are being utilised?

    •	The volume of data being passed between the client and server over a set time period 
             (a filter found within Tetration)



#Supported versions:

    Python 2.7.15

    Python 3.6


#Libraries and Modules

    Pandas, getpass, openpyxl, xlwt, socket, re, glob, os, sys


#System Arguments

    -i (input) sample.json
    
    -o (output) test.xls
    
    Both system arguments must be supplied otherwise the python code will generate an error.


#How to use

    python tetration_flow_filtering_v2.7.py -i sample.json -o flow_example.xls

    python3.6 tetration_flow_filtering_v3.6.py -i sample.json -o flow_example.xls

    Both system arguments must be supplied otherwise the python code will generate an error. 


#Output:

    Two tabs will be generated on the output sheet. 

  Flows: 

    •	source

    •	source DNS name (if available)  

    •	destination (Tetration filter target)

    •	destination DNS name (if available)

    •	destination protocol 

    •	destination port

    •	byte count

    •	packet count


    When flows are seen from between the same source and destination but using different protocol and/or ports 
    numbers, they are grouped together within the output file. 

   Unique_flows:

    Provides a summary view of communication without the protocol, port, byte count and packet count information. 
