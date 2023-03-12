import struct
import json
from micropython import const

CDP_PID = b"\x20\x00"

CDP_TYPE_DEVICE_ID = const(0x0001)
CDP_TYPE_SOFTWARE_VERSION = const(0x0005)
CDP_TYPE_PLATFORM = const(0x0006)
CDP_TYPE_ADDRESS = const(0x0002)
CDP_TYPE_PORT_ID = const(0x0003)
CDP_TYPE_CAPABILITIES = const(0x0004)
CDP_TYPE_PROTO_HELLO = const(0x0008)
CDP_TYPE_VTP_MGMT_DOMAIN = const(0x0009)
CDP_TYPE_NATIVE_VLAN = const(0x000a)
CDP_TYPE_DUPLEX = const(0x000b)
CDP_TYPE_TRUST_BITMAP = const(0x0012)
CDP_TYPE_UNTRUST_COS = const(0x0013)
CDP_TYPE_MGMT_ADDRESS = const(0x0016)
CDP_TYPE_POWER_AVAILABLE = const(0x001a)

CDP_ADDR_TYPE_NLPID = const(0x01)
CDP_ADDR_PROTOCOL_IP = const(0xcc)

def parsePacket(data):
    LogicalLinkControl = { 'DSAP': None, 'SSAP': None, 'Control field': None, 'Organization Code': None, 'PID': None }
    CDP = {
            'Version': None,
            'TTL': None,
            'Checksum': None,
            'Device ID': None,
            'Software Version': None,
            'Platform': None,
            'Addresses': None,
            'Port ID': None,
            'Capabilities': None,
            'Protocol Hello': None,
            'VTP Management Domain': None,
            'Native VLAN': None,
            'Duplex': None,
            'Trust Bitmap': None,
            'Untrusted port CoS': None,
            'Management Addresses': None,
            'Power Available': None
            }
    llc_DSAP    = data[0]
    llc_SSAP    = data[1]
    llc_FTYPE   = data[2]
    llc_OUI     = data[const(3):const(6)]
    llc_PID     = data[const(6):const(8)]
    
    cdp_VERSION = data[8]
    cdp_TTL = data[9]

# \xaa\xaa\x03\x00\x00\x0c \x00\x02\xb4\x8e\x98\x00\x01\x00,1010-BEDROOM-SW1.lan.productionservers.n\x00\x05\x00\xfcCisco IOS Software, C3750 Software (C3750-IPSERVICESK9-M), Version 12.2(55)SE10, RELEASE SOFTWARE (fc2)\nTechnical Support: http://www.cisco.com/techsupport\nCopyright (c) 1986-2015 by Cisco Systems, Inc.\nCompiled Wed 11-Feb-15 11:40 by prod_rel_team\x00\x06\x00\x16cisco WS-C3750-48P\x00\x02\x00\x11\x00\x00\x00\x01\x01\x01\xcc\x00\x04\xac\x10\n\x06\x00\x03\x00\x15FastEthernet1/0/9\x00\x04\x00\x08\x00\x00\x00)\x00\x08\x00$\x00\x00\x0c\x01\x12\x00\x00\x00\x00\xff\xff\xff\xff\x01\x02!\xff\x00\x00\x00\x00\x00\x00\x00\x1dE\xa6\x90\x80\xff\x00\x00\x00\t\x00\rENGLEHORN\x00\n\x00\x06\x00\n\x00\x0b\x00\x05\x01\x00\x0e\x00\x07\x01\x002\x00\x12\x00\x05\x00\x00\x13\x00\x05\x00\x00\x16\x00\x11\x00\x00\x00\x01\x01\x01\xcc\x00\x04\xac\x10\n\x06\x00

def getPacketType(data):
    tData = data[0:12]
    (_llc_dsap,
    _llc_ssap,
    _llc_ftype,
    _llc_oui,
    _llc_pid,
    _cdp_version,
    _cdp_ttl,
    _cdp_checksum) = struct.unpack('!bbb3s2sbb2s', tData)
    pid = _llc_pid
    print("pid: {} | realPid: {}".format(pid, CDP_PID))
    if pid == CDP_PID:
        return True
    else:
        return False

def getCdpVersion(data):
    tData = data[0:12]
    (_llc_dsap,
    _llc_ssap,
    _llc_ftype,
    _llc_oui,
    _llc_pid,
    _cdp_version,
    _cdp_ttl,
    _cdp_checksum) = struct.unpack('!bbb3s2sbb2s', tData)
    version = _cdp_version
    if version == 2:
        return 2
    elif version == 1:
        return 1
    else:
        return -1

def CDPv2(data):
    print(data)
    tData = data[0:12]
    (_llc_dsap,
    _llc_ssap,
    _llc_ftype,
    _llc_oui,
    _llc_pid,
    _cdp_version,
    _cdp_ttl,
    _cdp_checksum) = struct.unpack('!bbb3s2sbb2s', tData)
    #version = int.from_bytes(_cdp_version, 'big')
    version = _cdp_version
    #ttl = int.from_bytes(_cdp_ttl, 'big')
    ttl = _cdp_ttl
    testval = {
            'version': version,
            'ttl': ttl,
            }
    if version == 2:
        cdpData = data[12:len(data)]
    else:
        print("[CDPv2] WRONG VERSION: {}".format(version))
        return None

    i = int()
    retval = []
    while i < (len(cdpData) - 4):
        thisType = int.from_bytes(cdpData[i:i+2], 'big')
        thisLength = cdpData[i+2:i+4]
        iLength = int((thisLength[0] << 8) | thisLength[1])
        returndata = {
                'type': None,
                'length': None,
                'data': None
                }
        if thisType == CDP_TYPE_DEVICE_ID:
            print("Device ID")
            returndata['type'] = "Device ID"
            returndata['length'] = iLength
            returndata['data'] = cdpData[i+4:i+iLength].decode()
            print("DEVICE_ID: {}".format(json.dumps(returndata)))
            retval.append(returndata)
        elif thisType == CDP_TYPE_SOFTWARE_VERSION:
            print("Software Version")
            returndata['type'] = "Software Version"
            returndata['length'] = iLength
            returndata['data'] = cdpData[i+4:i+iLength].decode('ascii')
            retval.append(returndata)
        elif thisType == CDP_TYPE_PLATFORM:
            print("Platform")
            returndata['type'] = "Platform"
            returndata['length'] = iLength
            returndata['data'] = cdpData[i+4:i+iLength].decode('ascii')
            retval.append(returndata)
        elif thisType == CDP_TYPE_ADDRESS:
            print("IP Address")
            addrNum = int.from_bytes(cdpData[i+4:i+8], 'big')
            addrProtType = cdpData[i+8]
            returndata['type'] = "IP Address"
            returndata['length'] = iLength
            returndata['Number of addresses'] = addrNum
            if addrProtType == 1:
                returndata['Protocol Type'] = 'NLPID'
                protLength = cdpData[i+9]
                returndata['Protocol Length'] = protLength
                protocol = int.from_bytes(cdpData[i+10:i+10+protLength], 'big')
                if protocol == CDP_ADDR_PROTOCOL_IP:
                    returndata['Protocol'] = 'IP'
                    addrLength = int.from_bytes(cdpData[i+10+protLength:i+12+protLength], 'big')
                    returndata['Address Length'] = addrLength
                    addressBytes = cdpData[i+12+protLength:i+12+protLength+addrLength]
                    iaddress = []
                    for byte in addressBytes:
                        iaddress.append(str(byte))
                    address = str.join('.', iaddress)
                    returndata['address'] = address
            retval.append(returndata)
        elif thisType == CDP_TYPE_PORT_ID:
            print("Port ID")
            returndata['type'] = "Port ID"
            returndata['length'] = iLength
            returndata['data'] = cdpData[i+4:i+iLength].decode('ascii')
            retval.append(returndata)
        else:
            print("Other: {}".format(thisType))
            returndata['type'] = thisType
            returndata['length'] = iLength
            returndata['i'] = i
            returndata['iLength'] = iLength
            returndata['iSum'] = iLength + i
        i += iLength

    return retval

def CDPv1(data):
    print(data)
    tData = data[0:12]
    (_llc_dsap,
    _llc_ssap,
    _llc_ftype,
    _llc_oui,
    _llc_pid,
    _cdp_version,
    _cdp_ttl,
    _cdp_checksum) = struct.unpack('!bbb3s2sbb2s', tData)
    #version = int.from_bytes(_cdp_version, 'big')
    version = _cdp_version
    #ttl = int.from_bytes(_cdp_ttl, 'big')
    ttl = _cdp_ttl
    testval = {
            'version': version,
            'ttl': ttl,
            }
    if version == 1:
        cdpData = data[12:len(data)]
    else:
        print("[CDPv1] WRONG VERSION: {}".format(version))
        return None

    print(json.dumps(testval))
    print(cdpData)
    i = int()
    retval = []
    while i < (len(cdpData) - 4):
        thisType = int.from_bytes(cdpData[i:i+2], 'big')
        thisLength = cdpData[i+2:i+4]
        iLength = int((thisLength[0] << 8) | thisLength[1])
        returndata = {
                'type': None,
                'length': None,
                'data': None
                }
        if thisType == CDP_TYPE_DEVICE_ID:
            print("Device ID")
            returndata['type'] = "Device ID"
            returndata['length'] = iLength
            returndata['data'] = cdpData[i+4:i+iLength].decode()
            print("DEVICE_ID: {}".format(json.dumps(returndata)))
            retval.append(returndata)
        elif thisType == CDP_TYPE_SOFTWARE_VERSION:
            print("Software Version")
            returndata['type'] = "Software Version"
            returndata['length'] = iLength
            returndata['data'] = cdpData[i+4:i+iLength].decode('ascii')
            retval.append(returndata)
        elif thisType == CDP_TYPE_PLATFORM:
            print("Platform")
            returndata['type'] = "Platform"
            returndata['length'] = iLength
            returndata['data'] = cdpData[i+4:i+iLength].decode('ascii')
            retval.append(returndata)
        elif thisType == CDP_TYPE_ADDRESS:
            print("IP Address")
            addrNum = int.from_bytes(cdpData[i+4:i+8], 'big')
            addrProtType = cdpData[i+8]
            returndata['type'] = "IP Address"
            returndata['length'] = iLength
            returndata['Number of addresses'] = addrNum
            if addrProtType == 1:
                returndata['Protocol Type'] = 'NLPID'
                protLength = cdpData[i+9]
                returndata['Protocol Length'] = protLength
                protocol = int.from_bytes(cdpData[i+10:i+10+protLength], 'big')
                if protocol == CDP_ADDR_PROTOCOL_IP:
                    returndata['Protocol'] = 'IP'
                    addrLength = int.from_bytes(cdpData[i+10+protLength:i+12+protLength], 'big')
                    returndata['Address Length'] = addrLength
                    addressBytes = cdpData[i+12+protLength:i+12+protLength+addrLength]
                    iaddress = []
                    for byte in addressBytes:
                        iaddress.append(str(byte))
                    address = str.join('.', iaddress)
                    returndata['address'] = address
            retval.append(returndata)
        elif thisType == CDP_TYPE_PORT_ID:
            print("Port ID")
            returndata['type'] = "Port ID"
            returndata['length'] = iLength
            returndata['data'] = cdpData[i+4:i+iLength].decode('ascii')
            retval.append(returndata)
        else:
            print("Other: {}".format(hex(thisType)))
            returndata['type'] = thisType
            returndata['length'] = iLength
            returndata['i'] = i
            returndata['iLength'] = iLength
            returndata['iSum'] = iLength + i
        i += iLength

    return retval

