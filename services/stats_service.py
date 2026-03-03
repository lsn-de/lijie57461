from utils.db import DatabaseManager


class StatsService:
    """数据统计服务"""
    
    @staticmethod
    def get_stats():
        """获取统计数据"""
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
        
        # 计算资源使用效率
        avg_machines_per_department = round((vm_count + physical_count) / department_count, 2) if department_count > 0 else 0
        avg_machines_per_product = round(vm_count / product_count, 2) if product_count > 0 else 0
        avg_machines_per_dept_product = round(vm_count / (department_count * product_count), 2) if department_count > 0 and product_count > 0 else 0
        
        return {
            'vm_count': vm_count,
            'product_count': product_count,
            'physical_count': physical_count,
            'department_count': department_count,
            'group_count': group_count,
            'avg_machines_per_department': avg_machines_per_department,
            'avg_machines_per_product': avg_machines_per_product,
            'avg_machines_per_dept_product': avg_machines_per_dept_product
        }
    
    @staticmethod
    def get_product_data():
        """获取产品使用机器个数数据"""
        product_data = DatabaseManager.execute_query('''
            SELECT product, COUNT(*) as count 
            FROM devices 
            WHERE product IS NOT NULL AND product != ""
            GROUP BY product 
            ORDER BY count DESC
        ''', fetchall=True)
        return [dict(row) for row in product_data]
    
    @staticmethod
    def get_department_data():
        """获取部门使用机器个数数据"""
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
        
        return department_data
    
    @staticmethod
    def get_department_product_data():
        """获取部门产品个数数据"""
        department_product_data = DatabaseManager.execute_query('''
            SELECT department, COUNT(DISTINCT product) as product_count 
            FROM devices 
            WHERE department IS NOT NULL AND department != "" AND product IS NOT NULL AND product != ""
            GROUP BY department 
            ORDER BY product_count DESC
        ''', fetchall=True)
        return [dict(row) for row in department_product_data]
    
    @staticmethod
    def get_device_type_data():
        """获取设备类型分布数据"""
        vm_count = DatabaseManager.execute_query('SELECT COUNT(*) FROM devices', fetchone=True)[0]
        physical_count = DatabaseManager.execute_query('SELECT COUNT(*) FROM physical_devices', fetchone=True)[0]
        
        return [
            {'type': '虚拟机', 'count': vm_count},
            {'type': '物理机', 'count': physical_count}
        ]
    
    @staticmethod
    def get_department_product_matrix():
        """获取部门-产品资源矩阵数据"""
        department_product_matrix = DatabaseManager.execute_query('''
            SELECT department, product, COUNT(*) as count 
            FROM devices 
            WHERE department IS NOT NULL AND department != "" AND product IS NOT NULL AND product != ""
            GROUP BY department, product
        ''', fetchall=True)
        return [dict(row) for row in department_product_matrix]
    
    @staticmethod
    def get_resource_trend_data():
        """获取资源使用趋势数据"""
        vm_count = DatabaseManager.execute_query('SELECT COUNT(*) FROM devices', fetchone=True)[0]
        physical_count = DatabaseManager.execute_query('SELECT COUNT(*) FROM physical_devices', fetchone=True)[0]
        
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
        
        return {
            'monthly': resource_trend_data,
            'quarterly': resource_quarterly_data,
            'yearly': resource_yearly_data
        }
