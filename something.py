
def get_ip():
    import http.client
    conn = http.client.HTTPConnection("ifconfig.me")
    conn.request("GET", "/ip")
    print(str(conn.getresponse().read())[2:-1])
