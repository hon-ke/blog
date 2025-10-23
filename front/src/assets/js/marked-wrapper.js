// src/utils/marked-wrapper.js
import { marked } from "marked";
import hljs from 'highlight.js';

// 生成标题 ID 的辅助函数
function generateHeadingId(text, existingIds = new Set()) {
  let id = text
    .toLowerCase()
    .replace(/[^\w\u4e00-\u9fa5]+/g, '-')
    .replace(/^-+|-+$/g, '');

  if (!id) id = 'heading';

  let uniqueId = id;
  let counter = 1;
  while (existingIds.has(uniqueId)) {
    uniqueId = `${id}-${counter}`;
    counter++;
  }

  return uniqueId;
}

// 存储已使用的 ID
const usedIds = new Set();

// 重置 ID 记录
function resetHeadingIds() {
  usedIds.clear();
}

// 解析行开头为|的自定义结构
// |cloud|名称|描述|下载地址 解析为 云盘的样式
// |名称|描述|头像|链接 解析为 友链
function parsePipeSyntax(text) {
  const lines = text.split('\n');
  let result = [];
  let currentFriendGroup = [];

  for (const line of lines) {
    const strippedLine = line.trim();

    // 检测友链语法：以 | 开头
    if (strippedLine.startsWith('|')) {
      const parts = strippedLine.slice(1).split('|');

      // 严格检查：必须正好有4个字段
      if (parts.length === 4) {
        const name = parts[0].trim();
        const description = parts[1].trim();
        const avatar = parts[2].trim();
        const link = parts[3].trim();

        // 验证必要字段
        if (name && link) {
          // 检查是否是云盘链接
          if (name === 'cloud') {
            // 生成云盘链接 HTML
            const cloudHtml = `
<div class="cloud-wrapper link">
  <span class="cloud">
    <div class="cloud__logo _default"></div>
        <div class="cloud__describe">
          <div class="cloud__describe-title">${description}</div>
          <div class="cloud__describe-type">${avatar}</div>
        </div>
    <a class="cloud__btn" href="${link}" target="_blank" rel="noopener noreferrer nofollow">
      <i class="czs-download-l"></i>
    </a>
  </span>
</div>`;
            result.push(cloudHtml);
            continue;
          } else {
            // 设置默认值
            const finalAvatar = avatar || "https://via.placeholder.com/64x64?text=Avatar";
            const finalDescription = description || "一个有趣的博客";

            // 生成友链 HTML
            const html = `
        <div class="friend-link-item">
            <a class="friend-link" href="${link}" title="${name}" target="_blank">
                <img class="friend-avatar"
                    src="${finalAvatar}"
                    alt="${name}"
                    onerror="this.src='/img/friend_404.gif'">
                <div class="friend-info">
                    <div class="friend-name">${name}</div>
                    <div class="friend-desc">${finalDescription}</div>
                </div>
            </a>
        </div>`;

            currentFriendGroup.push(html);
            continue;
          }
        }
      } else if (parts.length > 0) {
        console.warn(`友链格式错误，需要4个字段，当前有${parts.length}个: ${strippedLine}`);
      }
    }

    // 如果不是友链行
    if (currentFriendGroup.length > 0) {
      // 把当前连续的友链组放到容器里
      result.push(`<div class="friend-links-group">${currentFriendGroup.join('')}</div>`);
      currentFriendGroup = [];
    }

    // 非友链内容保持原样
    result.push(line);
  }

  // 处理最后一组友链
  if (currentFriendGroup.length > 0) {
    result.push(`<div class="friend-links-group">${currentFriendGroup.join('')}</div>`);
  }

  return result.join('\n');
}

// 解析段落和行内 tokens 的辅助函数
function parseInlineTokens(tokens) {
  let html = '';

  tokens.forEach(token => {
    switch (token.type) {
      case 'text':
        html += token.text;
        break;
      case 'html':
        // HTML token 直接使用原始内容
        html += token.text;
        break;
      case 'image':
        html += customRenderer.image(token);
        break;
      case 'strong':
        html += `<strong>${parseInlineTokens(token.tokens || [])}</strong>`;
        break;
      case 'em':
        html += `<em>${parseInlineTokens(token.tokens || [])}</em>`;
        break;
      case 'codespan':
        html += `<code>${token.text}</code>`;
        break;
      case 'link':
        html += `<a href="${token.href}"${token.title ? ` title="${token.title}"` : ''}>${parseInlineTokens(token.tokens || [])}</a>`;
        break;
      case 'del':
        html += `<del>${parseInlineTokens(token.tokens || [])}</del>`;
        break;
      default:
        // 对于其他类型的 token，尝试递归处理或使用原始文本
        if (token.tokens && token.tokens.length > 0) {
          html += parseInlineTokens(token.tokens);
        } else {
          html += token.text || token.raw || '';
        }
        break;
    }
  });

  return html;
}

// 解析 tokens 的辅助函数（用于列表等）
function parseTokens(tokens) {
  let html = '';

  tokens.forEach(token => {
    switch (token.type) {
      case 'text':
        html += token.text;
        break;
      case 'list_item':
        html += customRenderer.listitem(token);
        break;
      case 'html':
        html += token.text;
        break;
      default:
        console.warn(`Unknown token type: ${token.type}`);
        break;
    }
  });

  return html;
}

// 自定义 renderer
const customRenderer = {
  // 标题处理 - 自动添加 ID
  heading(heading) {
    const level = heading.depth;
    const text = heading.text;
    const id = generateHeadingId(text, usedIds);
    usedIds.add(id);

    return `<h${level} id="${id}">${text}</h${level}>`;
  },

  // 图片修改
  image(image) {
    const href = image.href
    const title = image.title
    const text = image.text

    const href_origin = href.replace("compressed", "uploads", 1)

    return `<img src="${href}" alt="${text}" title="${title}" data-src="${href_origin}" class="custom-img pointer" data-fancybox="">`;
  },

  // 段落处理 - 检测友链
  paragraph(paragraph) {
    // 检查段落是否只包含图片
    const nonEmptyTokens = paragraph.tokens.filter(token => {
      if (token.type === 'text') {
        return token.text.trim().length > 0;
      }
      return true;
    });

    const isImageOnlyParagraph = nonEmptyTokens.length > 0 &&
      nonEmptyTokens.every(token => token.type === 'image');

    if (isImageOnlyParagraph) {
      const imageCount = nonEmptyTokens.length;
      let className = '';

      if (imageCount === 1) {
        className = 'single-image';
      } else if (imageCount === 2) {
        className = 'double-image';
      } else if (imageCount >= 3) {
        className = 'grid-image';
      }

      const content = parseInlineTokens(paragraph.tokens);
      return `<p class="${className}">${content}</p>`;
    }

    // 检查是否包含友链语法
    const textContent = paragraph.tokens.map(token => {
      if (token.type === 'text') return token.text;
      return token.raw || '';
    }).join('');

    const trimmedContent = textContent.trim();
    if (trimmedContent.startsWith('|')) {
      return parsePipeSyntax(textContent);
    }

    // 对于普通段落，正确解析所有 tokens
    const content = parseInlineTokens(paragraph.tokens);
    return `<p>${content}</p>`;
  },

  // 代码块处理 - 排除友链内容
  code(code) {
    // 如果代码块内容以 | 开头，按友链处理
    const trimmedText = code.text.trim();
    if (trimmedText.startsWith('|')) {
      return parsePipeSyntax(code.text);
    }

    const lang = code.lang ? code.lang : null;
    const isSpecialLang = ['seq', 'flow', 'katex', 'math', null].includes(lang || '');

    if (isSpecialLang || !lang) {
      return `<pre><code>${code.text}</code></pre>`;
    }

    try {
      const highlighted = hljs.highlight(code.text, { language: code.lang }).value;
      return `<pre><code class="hljs language-${lang}">${highlighted}</code></pre>`;
    } catch (e) {
      return `<pre><code>${code.text}</code></pre>`;
    }
  },

  // 任务列表
  listitem(tokens) {
    let content = '';

    if (tokens.tokens && tokens.tokens.length > 0) {
      content = parseInlineTokens(tokens.tokens);
    } else {
      content = tokens.text;
    }

    if (tokens.task) {
      const checkbox = tokens.checked ? '<input type="checkbox" checked disabled>' : '<input type="checkbox" disabled>';
      return `<li class="task-item">${checkbox} ${content}</li>`;
    } else {
      return `<li>${content}</li>`;
    }
  },

  // HTML 块处理 - 避免重复处理
  html(html) {
    // 确保 html 是字符串类型
    if (typeof html !== 'string') {
      return String(html);
    }

    // 如果已经是友链 HTML，直接返回
    if (html.includes('friend-link-item') || html.includes('friend-links-group')) {
      return html;
    }
    return html;
  },

  // 文本处理
  text(text) {
    return text.text;
  }
};

// 创建 marked 实例
const md = marked.use({
  renderer: customRenderer
});

export { md, parseTokens, resetHeadingIds };