
code_list = {
    '404':'Not Found',
    '400':'Bad Request',
    '403':'Forbidden',
    '500':'Internal Server Error',
    '503':'Service Unavailable',
    '504':'Gateway Timeout'
    #'':'',
}

def http_code(code):
    text = code_list[str(code)]
    return ('HTTP/1.1 %s %s\r\n\r\n' % (code,text)).encode()

#print(http_code(403))