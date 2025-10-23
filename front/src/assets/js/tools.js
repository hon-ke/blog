

function formatTime(timeStr) {
    if (!timeStr) return '未知时间';

    try {
        // 处理各种时间格式
        let postTime;

        // 如果是ISO格式或标准格式
        if (timeStr.includes('T') || timeStr.includes('-')) {
            postTime = new Date(timeStr);
        }
        // 如果是时间戳
        else if (!isNaN(timeStr)) {
            postTime = new Date(parseInt(timeStr));
        }
        // 其他格式
        else {
            postTime = new Date(timeStr);
        }

        // 检查时间是否有效
        if (isNaN(postTime.getTime())) {
            console.warn('无效的时间格式:', timeStr);
            return '时间格式错误';
        }

        const now = new Date();
        const diff = now.getTime() - postTime.getTime();

        // 处理未来时间
        if (diff < 0) {
            const futureDays = Math.ceil(-diff / (1000 * 60 * 60 * 24));
            if (futureDays === 1) return '明天';
            if (futureDays === 2) return '后天';
            if (futureDays <= 7) return `${futureDays}天后`;
            return postTime.toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        }

        // 正常的时间差计算
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days === 0) {
            if (hours === 0) {
                return minutes < 1 ? '刚刚' : `${minutes}分钟前`;
            }
            return `${hours}小时前`;
        }
        if (days === 1) return '昨天';
        if (days < 7) return `${days}天前`;
        if (days < 30) return `${Math.floor(days / 7)}周前`;
        if (days < 365) return `${Math.floor(days / 30)}个月前`;
        return `${Math.floor(days / 365)}年前`;

    } catch (error) {
        console.error('时间格式化异常:', error, '时间字符串:', timeStr);
        return '时间解析失败';
    }
}


export {
    formatTime
}