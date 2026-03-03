// 公共工具函数

// 原生AJAX函数
function ajax(options) {
    return new Promise(function(resolve, reject) {
        const xhr = new XMLHttpRequest();
        xhr.open(options.method || 'GET', options.url);
        
        // 设置请求头
        if (options.headers) {
            Object.keys(options.headers).forEach(key => {
                xhr.setRequestHeader(key, options.headers[key]);
            });
        }
        
        // 处理响应
        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                let response;
                try {
                    response = JSON.parse(xhr.responseText);
                } catch (e) {
                    response = xhr.responseText;
                }
                resolve(response);
            } else {
                let errorMessage = '请求失败';
                try {
                    const errorResponse = JSON.parse(xhr.responseText);
                    errorMessage = errorResponse.error || errorResponse.message || errorMessage;
                } catch (e) {
                    errorMessage = xhr.statusText || errorMessage;
                }
                reject(new Error(errorMessage));
            }
        };
        
        // 处理错误
        xhr.onerror = function() {
            reject(new Error('网络错误，请检查网络连接'));
        };
        
        // 发送请求
        if (options.data) {
            if (options.contentType === 'application/json') {
                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.send(JSON.stringify(options.data));
            } else if (options.formData) {
                // 发送FormData时不设置Content-Type，浏览器会自动设置
                xhr.send(options.data);
            } else {
                // 表单数据
                xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                xhr.send(options.data);
            }
        } else {
            xhr.send();
        }
    });
}

// 显示提示框
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    
    // 根据类型设置不同的背景色
    if (type === 'success') {
        toast.style.backgroundColor = '#28a745';
    } else if (type === 'error') {
        toast.style.backgroundColor = '#dc3545';
    } else if (type === 'warning') {
        toast.style.backgroundColor = '#ffc107';
        toast.style.color = '#333';
    } else {
        toast.style.backgroundColor = '#333';
        toast.style.color = '#fff';
    }
    
    toast.classList.add('show');
    
    setTimeout(function() {
        toast.classList.remove('show');
    }, 2000);
}

// 显示错误对话框
function showErrorDialog(title, message) {
    // 检查是否已存在对话框
    let dialog = document.getElementById('errorDialog');
    if (dialog) {
        dialog.remove();
    }
    
    // 创建对话框元素
    dialog = document.createElement('div');
    dialog.id = 'errorDialog';
    dialog.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 20px;
        max-width: 500px;
        width: 90%;
        z-index: 10000;
    `;
    
    // 对话框内容
    dialog.innerHTML = `
        <div style="margin-bottom: 15px;">
            <h4 style="margin: 0 0 10px 0; color: #dc3545;">${title}</h4>
            <p style="margin: 0; white-space: pre-wrap;">${message}</p>
        </div>
        <div style="text-align: right;">
            <button onclick="document.getElementById('errorDialog').remove(); document.getElementById('errorDialogBackdrop').remove();" style="
                padding: 8px 16px;
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            ">我已知晓</button>
        </div>
    `;
    
    // 添加到文档
    document.body.appendChild(dialog);
    
    // 创建背景遮罩
    let backdrop = document.createElement('div');
    backdrop.id = 'errorDialogBackdrop';
    backdrop.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 9999;
    `;
    document.body.appendChild(backdrop);
}


// 打开模态框
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        modal.classList.add('show');
        document.body.classList.add('modal-open');
        
        // 添加背景遮罩
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop fade show';
        backdrop.id = modalId + 'Backdrop';
        document.body.appendChild(backdrop);
        document.body.style.overflow = 'hidden';
    }
}

// 关闭模态框
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('show');
    }
    document.body.classList.remove('modal-open');
    
    // 移除背景遮罩
    const backdrop = document.getElementById(modalId + 'Backdrop');
    if (backdrop) {
        backdrop.remove();
    }
    document.body.style.overflow = '';
}