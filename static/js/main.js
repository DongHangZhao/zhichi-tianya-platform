// 咫尺天涯社交平台主JavaScript文件
document.addEventListener('DOMContentLoaded', function() {
    // 页面加载动画
    fadeInElements();

    // 表单验证
    initializeFormValidation();

    // 滚动效果
    initializeScrollEffects();

    // 移动端优化
    initializeMobileOptimizations();

    // 搜索功能
    initializeSearch();

    // 侧边栏交互
    initializeSidebarInteractions();
});

// 页面元素淡入效果
function fadeInElements() {
    const elements = document.querySelectorAll('.fade-in, .card, .btn, .list-group-item');
    elements.forEach((el, index) => {
        el.style.opacity = '0';
        setTimeout(() => {
            el.style.transition = 'opacity 0.5s ease-in-out, transform 0.5s ease-in-out';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 50);
    });
}

// 表单验证初始化
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// 滚动效果初始化
function initializeScrollEffects() {
    window.addEventListener('scroll', () => {
        const scrolled = document.documentElement.scrollTop;
        const header = document.querySelector('.navbar');

        if (header) {
            if (scrolled > 50) {
                header.style.boxShadow = '0 4px 20px rgba(0,0,0,0.1)';
                header.style.background = 'rgba(13, 110, 253, 0.98)';
                header.style.backdropFilter = 'blur(10px)';
            } else {
                header.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
                header.style.background = '';
                header.style.backdropFilter = 'none';
            }
        }
    });
}

// 移动端优化
function initializeMobileOptimizations() {
    // 检测是否为移动设备
    const isMobileDevice = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

    if (isMobileDevice) {
        // 为移动端添加特殊类
        document.body.classList.add('mobile-device');

        // 优化触摸事件
        const touchElements = document.querySelectorAll('.card, .btn, .list-group-item');
        touchElements.forEach(el => {
            el.addEventListener('touchstart', function() {
                this.classList.add('active-touch');
            });

            el.addEventListener('touchend', function() {
                this.classList.remove('active-touch');
            });
        });
    }
}

// 搜索功能初始化
function initializeSearch() {
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('keyup', debounce(function(e) {
            if (e.key === 'Enter') {
                performSearch(this.value);
            }
        }, 300));
    }
}

// 执行搜索
function performSearch(query) {
    if (query.trim() !== '') {
        // 这里可以添加实际的搜索逻辑
        console.log('搜索:', query);
        showToast(`正在搜索: ${query}`, 'info');
    }
}

// 侧边栏交互初始化
function initializeSidebarInteractions() {
    // 关注按钮交互
    const followButtons = document.querySelectorAll('.follow-btn');
    followButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const userId = this.dataset.userId;
            toggleFollow(userId, this);
        });
    });
}

// 关注/取消关注
function toggleFollow(userId, buttonElement) {
    const isFollowing = buttonElement.classList.contains('btn-success');
    const action = isFollowing ? 'unfollow' : 'follow';

    // 这里应该发起API调用
    console.log(`${action} user ${userId}`);

    if (isFollowing) {
        // 取消关注
        buttonElement.classList.remove('btn-success', 'btn-outline-success');
        buttonElement.classList.add('btn-outline-success');
        buttonElement.textContent = '关注';
        showToast('已取消关注', 'info');
    } else {
        // 关注
        buttonElement.classList.remove('btn-outline-success');
        buttonElement.classList.add('btn-success');
        buttonElement.textContent = '已关注';
        showToast('已关注', 'success');
    }
}

// 显示加载状态
function showLoading(element) {
    const originalText = element.innerHTML;
    element.innerHTML = '<span class="loading"></span> 处理中...';
    element.disabled = true;

    return function() {
        element.innerHTML = originalText;
        element.disabled = false;
    };
}

// 显示通知
function showToast(message, type = 'info') {
    // 创建toast元素
    const toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    toastContainer.style.zIndex = '1100';

    const toast = document.createElement('div');
    toast.className = `toast ${type === 'error' ? 'bg-danger' : type === 'success' ? 'bg-success' : 'bg-info'} text-white`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    toastContainer.appendChild(toast);
    document.body.appendChild(toastContainer);

    // 显示toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    // 自动移除
    toast.addEventListener('hidden.bs.toast', function() {
        toastContainer.remove();
    });
}

// 获取当前时间
function getCurrentTime() {
    return new Date().toLocaleString('zh-CN');
}

// 工具函数：防抖
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 检查是否为移动端
function isMobile() {
    return window.innerWidth <= 768;
}

// 平滑滚动到指定元素
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// 格式化数字
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// 深拷贝对象
function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

// 检查邮箱格式
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// 检查年龄范围
function isValidAge(age) {
    const num = parseInt(age);
    return !isNaN(num) && num >= 1 && num <= 120;
}

// 字符串截断
function truncateString(str, maxLength) {
    if (str.length <= maxLength) {
        return str;
    }
    return str.substring(0, maxLength) + '...';
}

// 时间格式化为相对时间
function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    let interval = Math.floor(seconds / 31536000);
    if (interval > 1) return interval + '年前';

    interval = Math.floor(seconds / 2592000);
    if (interval > 1) return interval + '月前';

    interval = Math.floor(seconds / 86400);
    if (interval > 1) return interval + '天前';

    interval = Math.floor(seconds / 3600);
    if (interval > 1) return interval + '小时前';

    interval = Math.floor(seconds / 60);
    if (interval > 1) return interval + '分钟前';

    return '刚刚';
}

// 图片懒加载
function initializeLazyLoad() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

// 页面加载完成后初始化懒加载
document.addEventListener('DOMContentLoaded', initializeLazyLoad);

// 点赞动画效果
function animateLike(button) {
    button.style.transform = 'scale(1.2)';
    setTimeout(() => {
        button.style.transform = 'scale(1)';
    }, 200);
}