import sqlite3
import os

# 获取数据库路径（使用持久化目录）
if os.name == 'posix':  # Linux/Mac
    # 在Linux系统中，使用用户主目录下的.ems目录
    home_dir = os.path.expanduser('~')
    persist_dir = os.path.join(home_dir, '.ems')
else:  # Windows
    # 在Windows系统中，使用应用数据目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    persist_dir = os.path.join(current_dir, 'data')

# 确保持久化目录存在
os.makedirs(persist_dir, exist_ok=True)

# 数据库文件路径
db_path = os.path.join(persist_dir, 'device_management.db')
print(f"初始化数据库: {db_path}")

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 创建roles表
try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT
    )''')
    print("roles表创建成功")
except Exception as e:
    print(f"创建roles表失败: {e}")

# 创建users表
try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role_id INTEGER,
        department TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (role_id) REFERENCES roles (id)
    )''')
    print("users表创建成功")
except Exception as e:
    print(f"创建users表失败: {e}")

# 创建devices表
try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product TEXT,
        department TEXT,
        device_group TEXT,
        vm_name TEXT NOT NULL,
        ip_address TEXT NOT NULL UNIQUE,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        remark TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    print("devices表创建成功")
except Exception as e:
    print(f"创建devices表失败: {e}")

# 创建或更新physical_devices表
try:
    # 首先尝试创建表（如果不存在）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS physical_devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product TEXT,
        department TEXT NOT NULL,
        device_code TEXT,
        ip_address TEXT NOT NULL UNIQUE,
        oob_ip TEXT,
        account TEXT NOT NULL,
        password TEXT NOT NULL,
        remark TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    print("physical_devices表创建/检查成功")
except Exception as e:
    print(f"创建或更新physical_devices表失败: {e}")

# 首次启动时，只创建表结构和插入默认用户/角色
# 不插入设备数据，也不清空数据
print("首次启动初始化，只创建表结构和默认用户/角色")

# 插入默认角色
try:
    # 使用 INSERT OR IGNORE 确保角色存在但不重复插入
    cursor.execute("INSERT OR IGNORE INTO roles (name, description) VALUES (?, ?)", ('admin', '管理员角色'))
    cursor.execute("INSERT OR IGNORE INTO roles (name, description) VALUES (?, ?)", ('user', '普通用户角色'))
    print("默认角色插入成功")
except Exception as e:
    print(f"插入默认角色失败: {e}")

# 插入默认用户
try:
    # 使用 INSERT OR IGNORE 确保用户存在但不重复插入
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role_id) VALUES (?, ?, ?)", ('admin', 'admin123', 1))
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role_id) VALUES (?, ?, ?)", ('user', 'user123', 2))
    print("默认用户插入成功")
except Exception as e:
    print(f"插入默认用户失败: {e}")

# 创建department_management表（先创建表，再检查列）
try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS department_management (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        department TEXT,
        device_group TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    print("department_management表创建成功")
except Exception as e:
    print(f"创建department_management表失败: {e}")

# 对于已存在的表，添加缺失的列
try:
    # 检查devices表是否有缺失的列
    cursor.execute('PRAGMA table_info(devices)')
    devices_columns = [column[1] for column in cursor.fetchall()]
    
    # 检查并添加product列
    if 'product' not in devices_columns:
        cursor.execute('ALTER TABLE devices ADD COLUMN product TEXT')
        print("给devices表添加product列成功")
    else:
        print("devices表已经有product列，无需添加")
    
    # 检查并添加department列
    if 'department' not in devices_columns:
        cursor.execute('ALTER TABLE devices ADD COLUMN department TEXT')
        print("给devices表添加department列成功")
    else:
        print("devices表已经有department列，无需添加")
    
    # 检查并添加device_group列
    if 'device_group' not in devices_columns:
        cursor.execute('ALTER TABLE devices ADD COLUMN device_group TEXT')
        print("给devices表添加device_group列成功")
    else:
        print("devices表已经有device_group列，无需添加")
    
    # 检查users表是否有department列
    cursor.execute('PRAGMA table_info(users)')
    users_columns = [column[1] for column in cursor.fetchall()]
    if 'department' not in users_columns:
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN department TEXT')
            print("给users表添加department列成功")
        except Exception as e:
            print(f"添加缺失列时出错: {e}")

    # 检查department_management表是否存在必要的列
    cursor.execute('PRAGMA table_info(department_management)')
    dept_management_columns = [column[1] for column in cursor.fetchall()]
    if 'department' not in dept_management_columns:
        try:
            cursor.execute('ALTER TABLE department_management ADD COLUMN department TEXT')
            print("给department_management表添加department列成功")
        except Exception as e:
            print(f"添加缺失列时出错: {e}")
    if 'device_group' not in dept_management_columns:
        try:
            cursor.execute('ALTER TABLE department_management ADD COLUMN device_group TEXT')
            print("给department_management表添加device_group列成功")
        except Exception as e:
            print(f"添加缺失列时出错: {e}")
    
    # 检查physical_devices表是否有product列
    cursor.execute('PRAGMA table_info(physical_devices)')
    physical_columns = [column[1] for column in cursor.fetchall()]
    if 'product' not in physical_columns:
        try:
            cursor.execute('ALTER TABLE physical_devices ADD COLUMN product TEXT')
            print("给physical_devices表添加product列成功")
        except Exception as e:
            print(f"添加缺失列时出错: {e}")
    else:
        print("physical_devices表已经有product列，无需添加")
except Exception as e:
    print(f"检查和添加缺失列时出错: {e}")

# 提交事务
conn.commit()

# 关闭连接
conn.close()
print("数据库初始化完成！")
