from config import setting

ROUTE_LIST_PATH = setting.get_param("ROUTE_LIST_PATH")


def parser(data):
    try:
        temp = data.split(b"\r\n")[0].split(b" ")[1].decode()
        path = temp.split('/')[1]
        return path , 0
    except Exception:
        return None,500

def new_request(data,dest,port,rev):
    try:
        headers, body = data.split(b"\r\n\r\n")
        params = headers.split(b"\r\n")
        headers_list = {}
        method,path,version = params[0].split(b' ')
        path = path[len(rev)+1:]
        if path == b'':
            path = b'/'
        for i in params[1:]:
            key, value = i.split(b": ")
            headers_list[key] = value
        headers_list[b'Host']=b'%s:%s' % (dest.encode(),str(port).encode())
        title = b'%s %s %s\r\n' % (method,path,version)
        all_head = b''
        for key,value in headers_list.items():
            all_head+= b'%s: %s\r\n' % (key,value)
        return title+all_head+b'\r\n'
    except Exception as e :
        print(e)
        return None,500

class Router:
    route_list = {}



    @classmethod
    def init(self):
        try:
            file = open(ROUTE_LIST_PATH)
            for line in file:
                path, destination, port, source = line.rstrip('\n').split(":")
                self.route_list[path] = {}
                self.route_list[path]["destination"] = destination
                self.route_list[path]["port"] = port
                self.route_list[path]["source"] = source
            file.close()
        except FileNotFoundError:
            print("File mot found ")
        except Exception as e:
            print('Не предвиденная ошибка в классе Route : ', e)
        print("********** Init Route **********")

    @classmethod
    def routing(self,data):
        path,code = parser(data)
        if code ==0:
            try:
                if path in self.route_list:
                    return self.route_list[path]['destination'],int(self.route_list[path]['port']),path,0
                else :
                    return  None,None,None,404
            except Exception as e:
                print(e)
                return None, None,None, 500
        else :
            return None, None, None,code

#a = b'GET /manager/home HTTP/1.1\r\nHost: localhost:8443\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate, br\r\nConnection: keep-alive\r\nUpgrade-Insecure-Requests: 1\r\nSec-Fetch-Dest: document\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-Site: none\r\nSec-Fetch-User: ?1\r\nCache-Control: max-age=0\r\n\r\n'
#rout = Router()
#rout.init()
#print(rout.routing(a))
#print(rout.routing(a))
#print(parser(a))
#print(new_request(a,'kremlin.ru','80',"manager"))