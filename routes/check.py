from flask import Blueprint, request, jsonify, render_template
from utils.decorators import login_required
import subprocess
import re
import paramiko
import platform

# 创建监控检查蓝图
check_bp = Blueprint('check', __name__)


@check_bp.route('/check')
@login_required
def check_devices_page():
    """监控检查页面"""
    return render_template('check.html')


@check_bp.route('/api/check-device', methods=['POST'])
@login_required
def check_device():
    """检查设备状态API"""
    ip = request.form.get('ip')
    username = request.form.get('username')
    password = request.form.get('password')
    
    # 添加日志信息
    print(f"接收到的参数: ip={ip}, username={username}, password={password}")
    
    if not ip:
        return jsonify({'error': '缺少IP地址参数'}), 400
    
    # 初始化返回结果
    result = {
        'ip': ip,
        'status': False,
        'delay': None,
        'cpu_usage': None,
        'memory_usage': None,
        'disk_usage': None,
        'os_type': 'Unknown',
        'ssh_status': 'not_attempted',
        'ssh_error': None
    }
    
    try:
        # 使用ping命令检查设备状态
        # 根据操作系统选择ping命令参数
        if platform.system() != 'Windows':  # 先判断Linux/macOS
            ping_args = ['ping', '-c', '1', '-W', '1', ip]
        else:  # Windows系统
            ping_args = ['ping', '-n', '1', '-w', '1000', ip]
        
        ping_result = subprocess.run(
            ping_args,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # 检查ping是否成功
        if ping_result.returncode == 0:
            result['status'] = True
            
            # 尝试从ping结果中提取延迟
            if platform.system() == 'Windows':
                # Windows ping结果格式
                match = re.search(r'平均 = (\d+)ms', ping_result.stdout)
            else:
                # Linux/macOS ping结果格式
                match = re.search(r'time=(\d+\.\d+) ms', ping_result.stdout)
            
            if match:
                result['delay'] = float(match.group(1))
        
        # 尝试通过SSH获取更多信息
        if username and password:
            try:
                # 创建SSH客户端
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # 尝试连接
                ssh.connect(ip, username=username, password=password, timeout=10)
                result['ssh_status'] = 'success'
                
                # 尝试获取CPU使用率
                try:
                    stdin, stdout, stderr = ssh.exec_command('top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk "{print 100 - $1}"')
                    cpu_usage = stdout.read().decode('utf-8').strip()
                    if cpu_usage:
                        result['cpu_usage'] = float(cpu_usage)
                except:
                    pass
                
                # 尝试获取内存使用率
                try:
                    stdin, stdout, stderr = ssh.exec_command('free -m | awk \'/Mem:/ {print $3/$2 * 100.0}\'' )
                    memory_usage = stdout.read().decode('utf-8').strip()
                    if memory_usage:
                        result['memory_usage'] = float(memory_usage)
                except:
                    pass
                
                # 尝试获取磁盘使用率
                try:
                    stdin, stdout, stderr = ssh.exec_command('df -h | awk \'/\/$/ {print $5}\'' )
                    disk_usage = stdout.read().decode('utf-8').strip().rstrip('%')
                    if disk_usage:
                        result['disk_usage'] = float(disk_usage)
                except:
                    pass
                
                # 尝试获取操作系统类型
                try:
                    stdin, stdout, stderr = ssh.exec_command('uname -a')
                    os_info = stdout.read().decode('utf-8').strip()
                    if os_info:
                        result['os_type'] = os_info
                except:
                    pass
                
                # 关闭SSH连接
                ssh.close()
            except Exception as e:
                result['ssh_status'] = 'failed'
                result['ssh_error'] = str(e)
    except Exception as e:
        # 记录错误但不影响返回结果
        print(f"检查设备状态时出错: {str(e)}")
    
    return jsonify(result)
