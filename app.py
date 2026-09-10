from flask import Flask, render_template, request, jsonify
import paramiko
import socket
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_command():
    data = request.get_json()
    router_ip = data.get('ip')
    command = data.get('command')
    
    username = "admin"
    password = "cisco"
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((router_ip, 22))
        
        transport = paramiko.Transport(sock)
        
        opt = transport.get_security_options()
        opt.kex = (
            'diffie-hellman-group14-sha1',
            'diffie-hellman-group1-sha1',
            'diffie-hellman-group-exchange-sha1'
        )
        opt.ciphers = (
            'aes128-cbc',
            '3des-cbc',
            'aes192-cbc',
            'aes256-cbc',
            'aes128-ctr',
            'aes192-ctr',
            'aes256-ctr'
        )
        opt.key_types = ('ssh-rsa', 'ssh-dss')
        
        transport.connect(username=username, password=password)
        
        # เปิด Interactive Shell เพื่อจำลอง Terminal จริง
        channel = transport.open_session()
        channel.get_pty()
        channel.invoke_shell()
        
        time.sleep(1)
        if channel.recv_ready():
            channel.recv(4096)  # เคลียร์ Banner ต้อนรับตอนแรกออก
            
        # ส่งคำสั่งพร้อมกด Enter
        channel.send(command + '\n')
        time.sleep(1.5)
        
        output = ""
        while channel.recv_ready():
            output += channel.recv(4096).decode('utf-8', errors='ignore')
            
        channel.close()
        transport.close()
        sock.close()
        
        return jsonify({"success": True, "output": output.strip()})
        
    except Exception as e:
        return jsonify({"success": False, "output": f"Connection Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
