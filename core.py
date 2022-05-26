import select
import socket
import ssl
import time
from _thread import start_new_thread
import router
from http_code import http_code
from router import Router

REVERSE_SERVER_PORT = 8443#int(setting.get_param("REVERSE_SERVER_PORT"))
REVERSE_CONNECTIONS = 10#int(setting.get_param("REVERSE_CONNECTIONS"))
REVERSE_SERVER_WAIT = 5#int(setting.get_param("REVERSE_SERVER_WAIT"))
REVERSE_BUFFER_SIZE = 4096#int(setting.get_param("REVERSE_BUFFER_SIZE"))
REVERSE_TIMEOUT_MAX = 15#int(setting.get_param("REVERSE_TIMEOUT_MAX"))


def client_conect(host, port):
    try:
        clieSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clieSock.connect((host, port))
    except Exception as e:
        print("Ошибка при создание клиентского соединения",e)
        return None, 503
    return clieSock, 0

def reverse_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('config/server.crt', 'config/server.key')

    servRsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servRsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servRsock.bind(('', REVERSE_SERVER_PORT ))
    servRsock.listen(REVERSE_CONNECTIONS)
    servRsock.settimeout(REVERSE_SERVER_WAIT)

    sRSsock = context.wrap_socket(servRsock, server_side=True)
    while True :
        try:
            srconn, host = sRSsock.accept()
        except socket.timeout:
            None
        except Exception as e:
            print("Ошибка соединения",e)
        else:
            start_new_thread(reverse_proxy_loop, (srconn, host))

def reverse_proxy_loop(server,sours):
    temp = server.recv(REVERSE_BUFFER_SIZE)
    print(temp)
    dest, port,path, code_route = Router.routing(temp)
    if code_route !=0:
        server.send(http_code(code_route))
        server.close()
        return
    client, code_clien = client_conect(dest, port)
    if code_clien !=0:
        server.send(http_code(code_clien))
        server.close()
        return
    req = router.new_request(temp,dest,port,path)
    print(req)
    client.send(router.new_request(temp,dest,port,path))


    time_wait = 0
    while True:
        recv, _, error = select.select([server, client], [], [server, client], 3)
        if error:
            print(error)

            break
        if recv:
            for in_ in recv:
                try:
                    data = in_.recv(REVERSE_BUFFER_SIZE)
                    print(data)
                    if in_ is client:
                        out = server
                    else:
                        out = client
                    if len(data) > 0:
                        out.send(data)
                        time_wait = 0
                    else:
                        time.sleep(1)
                        time_wait += 1
                        if REVERSE_TIMEOUT_MAX == time_wait:
                            break
                except ConnectionAbortedError:
                    break
                except ConnectionResetError:
                    break
                except BrokenPipeError:
                    break
                except Exception as e:
                    print("Не предвиденная ошибка в блоке обмена : ", e)
                    break
        else:
            time.sleep(1)
            time_wait += 1
        if REVERSE_TIMEOUT_MAX == time_wait:
            break
    print("close")
    server.close()
    client.close()

if __name__ == '__main__':
    Router.init()
    reverse_server()


