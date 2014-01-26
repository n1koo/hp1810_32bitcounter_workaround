#!/usr/bin/python
 
from pysnmp.entity.rfc3413.oneliner import cmdgen
 
import csv, time, sys
 
name = 'kytkin'
community = 'public'
 
SLEEPTIME=10
FILENAME="/tmp/switching.csv"
PORTCOUNT=24

def getBulk(host, community, oid):
	oid = tuple(map(int, oid.strip('.').split('.')))
	errorIndication, errorStatus, \
	errorIndex, varBindTable = cmdgen.CommandGenerator().bulkCmd(
	cmdgen.CommunityData(host, community),
	cmdgen.UdpTransportTarget((host, 161)),
	0, PORTCOUNT,
	oid
	)
	data = []
	if errorIndication:
		print errorIndication
	else:
		if errorStatus:
			print '%s at %s\n' % (
			errorStatus.prettyPrint(),
			errorIndex and varBinds[int(errorIndex)-1] or '?'
			)
		else:
			for varBindTableRow in varBindTable:
				for name, val in varBindTableRow:
					data.append(int(val))
	return data
 
portstatus = []
try:
	infile = file(FILENAME, "rb")
	csvread = csv.reader(infile)
	for row in csvread:
		portstatus.append({"cur_in": int(row[1]),
		"cur_out": int(row[2]),
		"last_in": int(row[3]),
		"last_out": int(row[4]) })
		infile.close()
	if len(portstatus) < PORTCOUNT:
		for i in range(PORTCOUNT-len(portstatus)):
			portstatus.append({"cur_in": 0, "cur_out": 0,
			"last_in": 0, "last_out": 0 })
except:
	portstatus = []
	for i in range(PORTCOUNT):
		portstatus.append({"cur_in": 0, "cur_out": 0,
		"last_in": 0, "last_out": 0 })

outfile = file(FILENAME, "wb")
csvwrite = csv.writer(outfile)
INT_MAX = 4294967295L
	 
while True:
	start = time.time()
	inOct = getBulk(name, community, "1.3.6.1.2.1.2.2.1.10")[:PORTCOUNT]
	outOct = getBulk(name, community, "1.3.6.1.2.1.2.2.1.16")[:PORTCOUNT]
	outfile.seek(0)
	 
	for i in range(len(inOct)):
		if portstatus[i]["last_in"] > inOct[i]:
			#overflow
			#print "overflow in at %s from %s to %s" % (i, portstatus[i]["last_in"], inOct[i])
			portstatus[i]["cur_in"] += INT_MAX - (portstatus[i]["last_in"] - inOct[i])
		else:
			portstatus[i]["cur_in"] += inOct[i] - portstatus[i]["last_in"]
		if portstatus[i]["last_out"] > outOct[i]:
			#overflow
			#print "overflow out at %s from %s to %s" % (i, portstatus[i]["last_out"], outOct[i])
			portstatus[i]["cur_out"] += INT_MAX - (portstatus[i]["last_out"] - outOct[i])
		else:
			portstatus[i]["cur_out"] += outOct[i] - portstatus[i]["last_out"]	 
			portstatus[i]["last_in"] = inOct[i]
			portstatus[i]["last_out"] = outOct[i]
				 
			csvwrite.writerow([i+1, portstatus[i]["cur_in"],
			portstatus[i]["cur_out"],
			portstatus[i]["last_in"],
			portstatus[i]["last_out"] ])

	outfile.flush()
	stop = time.time()
	sleep = SLEEPTIME - (stop-start)
	if sleep > 0:
		time.sleep(sleep);
outfile.close()