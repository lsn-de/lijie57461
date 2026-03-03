from flask import Blueprint, render_template
from utils.db import DatabaseManager
from utils.decorators import login_required, admin_required

# 创建数据统计蓝图
stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/stats')
@login_required
@admin_required
def stats():
    """数据统计页面"""
    # 计算虚拟机数量
    vm_count = DatabaseManager.execute_query('SELECT COUNT(*) FROM devices', fetchone=True)[0]
    
    # 计算物理机数量
    physical_count = DatabaseManager.execute_query('SELECT COUNT(*) FROM physical_devices', fetchone=True)[0]
    
    # 计算产品数量（去重）
    product_count = DatabaseManager.execute_query('SELECT COUNT(DISTINCT product) FROM devices WHERE product IS NOT NULL AND product != ""', fetchone=True)[0]
    
    # 计算部门数量（去重）
    department_count = DatabaseManager.execute_query('SELECT COUNT(DISTINCT department) FROM devices WHERE department IS NOT NULL AND department != ""', fetchone=True)[0]
    physical_department_count = DatabaseManager.execute_query('SELECT COUNT(DISTINCT department) FROM physical_devices WHERE department IS NOT NULL AND department != ""', fetchone=True)[0]
    department_count = max(department_count, physical_department_count)
    
    # 计算组别数量（去重）
    group_count = DatabaseManager.execute_query('SELECT COUNT(DISTINCT device_group) FROM devices WHERE device_group IS NOT NULL AND device_group != ""', fetchone=True)[0]
    
    # 计算每个产品使用的机器个数
    product_data = DatabaseManager.execute_query('''
        SELECT product, COUNT(*) as count 
        FROM devices 
        WHERE product IS NOT NULL AND product != ""
        GROUP BY product 
        ORDER BY count DESC
    ''', fetchall=True)
    product_data = [dict(row) for row in product_data]
    
    # 计算每个部门使用的机器个数（包括虚拟机和物理机）
    # 先获取虚拟机部门数据
    vm_department_data = DatabaseManager.execute_query('''
        SELECT department, COUNT(*) as count 
        FROM devices 
        WHERE department IS NOT NULL AND department != ""
        GROUP BY department
    ''', fetchall=True)
    
    # 再获取物理机部门数据
    physical_department_data = DatabaseManager.execute_query('''
        SELECT department, COUNT(*) as count 
        FROM physical_devices 
        WHERE department IS NOT NULL AND department != ""
        GROUP BY department
    ''', fetchall=True)
    
    # 合并部门数据
    department_dict = {}
    for row in vm_department_data:
        department_dict[row['department']] = department_dict.get(row['department'], 0) + row['count']
    for row in physical_department_data:
        department_dict[row['department']] = department_dict.get(row['department'], 0) + row['count']
    
    # 转换为列表并排序
    department_data = [{'department': dept, 'count': count} for dept, count in department_dict.items()]
    department_data.sort(key=lambda x: x['count'], reverse=True)
    
    # 计算每个部门的产品个数
    department_product_data = DatabaseManager.execute_query('''
        SELECT department, COUNT(DISTINCT product) as product_count 
        FROM devices 
        WHERE department IS NOT NULL AND department != "" AND product IS NOT NULL AND product != ""
        GROUP BY department 
        ORDER BY product_count DESC
    ''', fetchall=True)
    department_product_data = [dict(row) for row in department_product_data]
    
    # 计算设备类型分布
    device_type_data = [
        {'type': '虚拟机', 'count': vm_count},
        {'type': '物理机', 'count': physical_count}
    ]
    
    # 计算部门-产品资源矩阵
    department_product_matrix = DatabaseManager.execute_query('''
        SELECT department, product, COUNT(*) as count 
        FROM devices 
        WHERE department IS NOT NULL AND department != "" AND product IS NOT NULL AND product != ""
        GROUP BY department, product
    ''', fetchall=True)
    department_product_matrix = [dict(row) for row in department_product_matrix]
    
    # 计算资源使用趋势（模拟数据，实际应根据创建时间统计）
    # 月度数据
    resource_trend_data = [
        {'month': '1月', 'vm_count': vm_count // 12 * 8, 'physical_count': physical_count // 12 * 8},
        {'month': '2月', 'vm_count': vm_count // 12 * 8, 'physical_count': physical_count // 12 * 8},
        {'month': '3月', 'vm_count': vm_count // 12 * 9, 'physical_count': physical_count // 12 * 9},
        {'month': '4月', 'vm_count': vm_count // 12 * 9, 'physical_count': physical_count // 12 * 9},
        {'month': '5月', 'vm_count': vm_count // 12 * 10, 'physical_count': physical_count // 12 * 10},
        {'month': '6月', 'vm_count': vm_count // 12 * 10, 'physical_count': physical_count // 12 * 10},
        {'month': '7月', 'vm_count': vm_count // 12 * 11, 'physical_count': physical_count // 12 * 11},
        {'month': '8月', 'vm_count': vm_count // 12 * 11, 'physical_count': physical_count // 12 * 11},
        {'month': '9月', 'vm_count': vm_count // 12 * 12, 'physical_count': physical_count // 12 * 12},
        {'month': '10月', 'vm_count': vm_count, 'physical_count': physical_count},
        {'month': '11月', 'vm_count': vm_count, 'physical_count': physical_count},
        {'month': '12月', 'vm_count': vm_count, 'physical_count': physical_count}
    ]
    
    # 季度数据
    resource_quarterly_data = [
        {'quarter': 'Q1', 'vm_count': (vm_count // 12 * 8 + vm_count // 12 * 8 + vm_count // 12 * 9) // 3, 'physical_count': (physical_count // 12 * 8 + physical_count // 12 * 8 + physical_count // 12 * 9) // 3},
        {'quarter': 'Q2', 'vm_count': (vm_count // 12 * 9 + vm_count // 12 * 10 + vm_count // 12 * 10) // 3, 'physical_count': (physical_count // 12 * 9 + physical_count // 12 * 10 + physical_count // 12 * 10) // 3},
        {'quarter': 'Q3', 'vm_count': (vm_count // 12 * 11 + vm_count // 12 * 11 + vm_count // 12 * 12) // 3, 'physical_count': (physical_count // 12 * 11 + physical_count // 12 * 11 + physical_count // 12 * 12) // 3},
        {'quarter': 'Q4', 'vm_count': (vm_count + vm_count + vm_count) // 3, 'physical_count': (physical_count + physical_count + physical_count) // 3}
    ]
    
    # 年份数据（假设只有一年）
    resource_yearly_data = [
        {'year': '2025', 'vm_count': vm_count, 'physical_count': physical_count}
    ]
    
    # 计算资源使用效率
    avg_machines_per_department = round((vm_count + physical_count) / department_count, 2) if department_count > 0 else 0
    avg_machines_per_product = round(vm_count / product_count, 2) if product_count > 0 else 0
    avg_machines_per_dept_product = round(vm_count / (department_count * product_count), 2) if department_count > 0 and product_count > 0 else 0
    
    # 准备统计数据
    stats_data = {
        'vm_count': vm_count,
        'product_count': product_count,
        'physical_count': physical_count,
        'department_count': department_count,
        'group_count': group_count,
        'avg_machines_per_department': avg_machines_per_department,
        'avg_machines_per_product': avg_machines_per_product,
        'avg_machines_per_dept_product': avg_machines_per_dept_product
    }
    
    return render_template('stats.html', stats=stats_data, product_data=product_data, department_data=department_data, department_product_data=department_product_data, device_type_data=device_type_data, department_product_matrix=department_product_matrix, resource_trend_data=resource_trend_data, resource_quarterly_data=resource_quarterly_data, resource_yearly_data=resource_yearly_data)
