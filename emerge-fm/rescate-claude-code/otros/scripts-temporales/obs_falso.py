# OBS de mentira: servidor obs-websocket 5 mínimo (con contraseña) para probar paneles de GC.
import base64, hashlib, json, os, socket, struct, sys, threading

CLAVE = 'secreto123'
PUERTO = int(sys.argv[1]) if len(sys.argv) > 1 else 4466
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'obs_falso.log')
open(LOG, 'w').close()
G = 'C:/Users/farid/Desktop/claude code/emerge-noticias-gc/gc-noticias.html'
estado = {'MARCADOR': {'settings': {'is_local_file': False, 'url': 'https://scoreleader.com/b/AMOTDIH-sb'}, 'enabled': True, 'escenas': ['escena stream']},
          'GC FURIA': {'settings': {'is_local_file': True, 'local_file': 'C:/Users/farid/Desktop/claude code/furia-promo/gc/gc-furia.html'}, 'enabled': False, 'escenas': ['La Ciudad de la Furia']},
          'GC NOTICIAS': {'settings': {'is_local_file': True, 'local_file': G}, 'enabled': False, 'escenas': ['Noticias', 'escena stream']},
          'BASE NOTICIAS': {'settings': {'is_local_file': False, 'url': 'file:///C:/Users/farid/Desktop/claude%20code/emerge-noticias-gc/gc-noticias.html?modo=base'}, 'enabled': True, 'escenas': ['Noticias']}}
ESCENAS = ['escena stream', 'La Ciudad de la Furia', 'Noticias']

def log(*a):
    with open(LOG, 'a', encoding='utf-8') as f: f.write(' '.join(str(x) for x in a) + '\n')

def leer(c, n):
    b = b''
    while len(b) < n:
        d = c.recv(n - len(b))
        if not d: raise ConnectionError
        b += d
    return b

def recibir(c):
    b0, b1 = leer(c, 2); n = b1 & 0x7F
    if n == 126: n = struct.unpack('>H', leer(c, 2))[0]
    elif n == 127: n = struct.unpack('>Q', leer(c, 8))[0]
    m = leer(c, 4) if b1 & 0x80 else b'\0\0\0\0'
    d = bytes(x ^ m[i % 4] for i, x in enumerate(leer(c, n)))
    if b0 & 0x0F == 8: raise ConnectionError
    return json.loads(d)

def enviar(c, obj, op=1):
    d = json.dumps(obj).encode() if not isinstance(obj, bytes) else obj
    cab = bytes([0x80 | op]) + (bytes([len(d)]) if len(d) < 126 else bytes([126]) + struct.pack('>H', len(d)) if len(d) < 65536 else bytes([127]) + struct.pack('>Q', len(d)))
    c.sendall(cab + d)

def b64sha(s): return base64.b64encode(hashlib.sha256(s.encode()).digest()).decode()

def atender(c):
    try:
        req = b''
        while b'\r\n\r\n' not in req: req += c.recv(4096)
        key = [l.split(b': ')[1] for l in req.split(b'\r\n') if l.lower().startswith(b'sec-websocket-key')][0]
        acc = base64.b64encode(hashlib.sha1(key + b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest())
        c.sendall(b'HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: ' + acc + b'\r\n\r\n')
        salt, reto = 'sal-de-prueba', 'reto-de-prueba'
        enviar(c, {'op': 0, 'd': {'obsWebSocketVersion': '5.5.0', 'rpcVersion': 1, 'authentication': {'challenge': reto, 'salt': salt}}})
        ident = recibir(c)
        if ident.get('op') != 1 or ident['d'].get('authentication') != b64sha(b64sha(CLAVE + salt) + reto):
            log('AUTH FALLÓ'); enviar(c, struct.pack('>H', 4009) + b'Authentication failed.', op=8); c.close(); return
        log('AUTH OK'); enviar(c, {'op': 2, 'd': {'negotiatedRpcVersion': 1}})
        while True:
            m = recibir(c)
            if m.get('op') != 6: continue
            t, rd, rid = m['d']['requestType'], m['d'].get('requestData', {}), m['d']['requestId']
            ok, resp = True, {}
            nombres = list(estado)
            if t == 'GetInputList': resp = {'inputs': [{'inputName': k, 'inputKind': 'browser_source'} for k in estado] + [{'inputName': 'Cámara', 'inputKind': 'dshow_input'}]}
            elif t == 'GetInputSettings': resp = {'inputSettings': estado[rd['inputName']]['settings'], 'inputKind': 'browser_source'}
            elif t == 'SetInputSettings': estado[rd['inputName']]['settings'].update(rd['inputSettings'])
            elif t == 'GetSceneList': resp = {'scenes': [{'sceneName': e, 'sceneIndex': i} for i, e in enumerate(ESCENAS)]}
            elif t == 'GetSceneItemId':
                if rd['sceneName'] in estado[rd['sourceName']]['escenas']: resp = {'sceneItemId': nombres.index(rd['sourceName']) + 1}
                else: ok = False
            elif t == 'SetSceneItemEnabled': estado[nombres[rd['sceneItemId'] - 1]]['enabled'] = rd['sceneItemEnabled']
            elif t == 'GetSceneItemEnabled': resp = {'sceneItemEnabled': estado[nombres[rd['sceneItemId'] - 1]]['enabled']}
            else: ok = False
            if t in ('SetInputSettings', 'SetSceneItemEnabled'): log(t, json.dumps(rd, ensure_ascii=False))
            enviar(c, {'op': 7, 'd': {'requestType': t, 'requestId': rid, 'requestStatus': {'result': ok, 'code': 100 if ok else 204}, 'responseData': resp}})
    except Exception as e:
        log('fin conexión', type(e).__name__)

s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); s.bind(('127.0.0.1', PUERTO)); s.listen(5)
print('obs falso en', PUERTO, flush=True)
while True:
    c, _ = s.accept(); threading.Thread(target=atender, args=(c,), daemon=True).start()
