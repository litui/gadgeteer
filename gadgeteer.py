import daemon
import json
import os
import socket
import threading
import time
from sp_usb import GadgetManager

SOCKET_ADDR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '.gadgeteer.socket'
)

def bind_socket():
    try:
        os.unlink(SOCKET_ADDR)
    except OSError:
        if os.path.exists(SOCKET_ADDR):
            raise

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(SOCKET_ADDR)
    os.chown(path=SOCKET_ADDR, uid=0, gid=1000)
    os.chmod(path=SOCKET_ADDR, mode=0o770)
    return sock

def handle_get(dtarget, gdm=None):
    if dtarget == 'status':
        return json.dumps({
            'type': 'status',
            'msg': {
                'active': gdm.active
            }
        })

def handle_set(dtarget, dmsg={}, gdm=None):
    if dtarget == 'active':
        if not dmsg:
            return json.dumps({
                'type': 'error',
                'msg': {
                    'err_msg': 'No msg dict set on request.'
                }
            })

        g_type = dmsg.pop('mode') if dmsg.get('mode') else ''
        if not g_type or g_type == 'none':
            gdm.deactivate()
            return json.dumps({
                'type': 'status',
                'msg': {
                    'active': ''
                }
            })
        
        kw = dmsg
        gdm.run(g_type, **kw)

        if gdm.active != g_type:
            return json.dumps({
                'type': 'error',
                'msg': {
                    'err_msg': 'Reboot required'
                }
            })
        return json.dumps({
            'type': 'status',
            'msg': {
                'active': gdm.active
            }
        })

def controller(data, gdm=None):
    dtype = data.get('type')
    dtarget = data.get('target')
    dmsg = data.get('msg')
    if dtype and dtarget:
        if dtype == 'get':
            return handle_get(dtarget, gdm=gdm)
        elif dtype == 'set':
            return handle_set(dtarget, dmsg, gdm=gdm)

    return None

def socket_handler(gdm):
    while gdm.running:
        try:
            sock = bind_socket()
            sock.listen(1)
            
            while gdm.running:
                conn, client_addr = sock.accept()
                try:
                    data_bytes: bytes = conn.recv(1024)
                    data_string = json.loads(data_bytes)
                    response = controller(data_string, gdm=gdm)

                    conn.sendall(response.encode('utf-8'))
                except json.decoder.JSONDecodeError:
                    pass
                except ConnectionResetError:
                    pass
                except BrokenPipeError:
                    pass
                finally:
                    conn.close()
        except socket.timeout:
            pass

def main():
    gdm = GadgetManager()

    sh = threading.Thread(target=socket_handler, args=[gdm])
    sh.daemon = True
    sh.start()

    # Threaded all the above so this can manage other tricks
    while True:
        pass


if __name__ == "__main__":
    with daemon.DaemonContext():
        main()