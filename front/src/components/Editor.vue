<template>
  <div class="editor-container">
    <div class="editor-tools">
      <!-- 模板选择 -->
      <div class="template-selector">
        <select v-model="selectedTemplate" @change="insertTemplate" class="template-select">
          <option value="" disabled selected>选择预设</option>
          <option v-for="(template, index) in templates" :key="index" :value="index">
            {{ template.name }}
          </option>
        </select>
      </div>

      <!-- 格式工具 -->
      <span class="editor-btn" @click="applyBold"><strong>B</strong></span>
      <span class="editor-btn" @click="applyItalic"><i>I</i></span>

      <!-- 插入工具 -->
      <span class="editor-btn" @click="triggerFileUpload"><i class="czs-folder-l"></i></span>
      <!-- <span class="editor-btn" @click="insertImage"><i class="czs-image-l"></i></span>
      <span class="editor-btn" @click="insertTable"><i class="czs-prototype-l"></i></span> -->
      <span class="editor-btn" @click="togglePreview"><i :class="!previewMode ? 'czs-eye-l' : 'czs-web-edit-l'"></i></span>

      <!-- 元数据操作 -->
      <span v-if="type === '文章' && !hasFrontMatter" class="editor-btn" @click="insertMetadataTemplate">
        插入元数据
      </span>
      <span v-if="hasFrontMatter" class="editor-btn" @click="toggleMetadata" :class="showMetadata ? 'czs-setting' : 'czs-setting-l'">
      </span>

      <!-- 状态指示器 -->
      <div class="status-indicator">
        <span class="mode-indicator" @click="togglePreview">
          {{ previewMode ? '预览' : '编辑' }}
        </span>
        <span class="save-status" :class="{ saved: autoSaveStatus === 'saved' }" @click="saveContent">
          {{ autoSaveStatusText }}
        </span>
      </div>
    </div>

    <!-- 隐藏的文件上传输入框 -->
    <input type="file" ref="fileInput" multiple style="display: none" @change="handleFileUpload"
      accept="image/*,video/*,.pdf,.doc,.docx,.txt,.zip,.rar">

    <!-- 上传进度和状态 -->
    <div v-if="showUploadProgress" class="upload-status">
      <div class="upload-header">
        <span class="upload-progress-text">
          上传进度: {{ currentFileIndex }}/{{ totalFiles }}
          <span class="current-file-name">({{ currentFileName }})</span>
        </span>
        <span class="upload-percentage">
          {{ totalProgress }}%
        </span>
      </div>
      <div class="upload-progress">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: totalProgress + '%' }"
            :class="{ 'upload-error': hasUploadError }"></div>
        </div>
        <span class="progress-text">
          <span v-if="hasUploadError" class="error-text">上传失败</span>
          <span v-else-if="totalProgress === 100" class="success-text">上传完成</span>
          <span v-else>上传中...</span>
        </span>
      </div>
    </div>

    <!-- 编辑器区域 -->
    <div v-show="!previewMode" class="editor-content">
      <!-- 元数据区域 -->
      <div v-if="hasFrontMatter && showMetadata" class="metadata-section">
        <div class="metadata-header">
          <span class="metadata-title">元数据</span>
          <span class="metadata-tip">（YAML格式，手动编辑）</span>
        </div>
        <div class="metadata-content">
          <pre class="metadata-code">{{ frontMatterContent }}</pre>
        </div>
      </div>

      <!-- 正文编辑器 -->
      <textarea ref="editor" v-model="content" class="editor-textarea"
        :class="{ 'with-metadata': hasFrontMatter && showMetadata }" :placeholder="placeholderText"
        @input="handleInput">
      </textarea>
    </div>

    <!-- 预览区域 -->
    <div v-show="previewMode" @click="previewMode=false" class="preview-area markdown-body" v-html="previewHtml"></div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { md } from '@/assets/js/marked-wrapper'
// Props
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: '笔记',
    validator: (value) => ['笔记', '文章', '朋友圈'].includes(value)
  },
  apiKey: {
    type: String,
    default: ''
  },
  autoSave: {
    type: Boolean,
    default: true
  },
  saveDelay: {
    type: Number,
    default: 1000
  }
})

// Emits
const emit = defineEmits([
  'update:modelValue',
  'save',
  'status-change',
  'upload-progress',
  'error'
])

// Refs
const editor = ref(null)
const fileInput = ref(null)
const content = ref(props.modelValue)
const previewMode = ref(false)
const selectedTemplate = ref('')
const autoSaveStatus = ref('saved')
const saveTimeout = ref(null)
const showMetadata = ref(true)

// 上传进度相关变量
const showUploadProgress = ref(false)
const totalProgress = ref(0)
const currentFileIndex = ref(0)
const totalFiles = ref(0)
const currentFileName = ref('')
const hasUploadError = ref(false)

// 本地存储键名
const STORAGE_KEY = 'editor-content'
const PREVIEW_MODE_STORAGE = 'preview-mode'
const METADATA_VISIBILITY_STORAGE = 'metadata-visibility'

// 模板数据
const templates = ref([
  { name: "测试", content: "## 测试\n\n ### 测试数据" },
  { name: '待办事项', content: '\n- [ ] 任务一\n- [ ] 任务二\n- [ ] 任务三' },
  { name: '代码块', content: '\n```javascript\n\n```' },
  { name: '图片示例', content: '\n![]( "图片标题")' },
  { name: "table", content: `\n| 列1 | 列2 | 列3 |\n|-----|-----|-----|\n| 内容1 | 内容2 | 内容3 |\n| 内容4 | 内容5 | 内容6 |` },
  { name: "🥃发病", content: "\n<span class='chip c-hand text-primary'>🥃发病</span> " },
  { name: "📝日常", content: "\n<span class='chip c-hand text-primary'>📝日常</span> " },
  { name: "📫多说", content: "\n<span class='chip c-hand text-primary'>📫多说</span> " },
  { name: "🗒️摘抄", content: "\n<span class='chip c-hand text-primary'>🗒️摘抄</span> " },
  { name: "🚀捣鼓", content: "\n<span class='chip c-hand text-primary'>🚀捣鼓</span> " },
  { name: "🛒出售", content: "\n<span class='chip c-hand text-primary'>🛒出售</span> " },
  { name: "🏃🏻‍♂️运动", content: "\n<span class='chip c-hand text-primary'>🏃🏻‍♂️运动</span> " },
  { name: "📅打卡", content: "\n<span class='chip c-hand text-primary'>📅打卡</span> " },
  { name: "🛠️开发", content: "\n<span class='chip c-hand text-primary'>🛠️开发</span> " },
  { name: "⏱️时刻", content: "\n<span class='chip c-hand text-primary'>⏱️时刻</span> " },
  { name: "🏔️旅行", content: "\n<span class='chip c-hand text-primary'>🏔️旅行</span> " },
  {
    name: '时间',
    content: new Date().toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    })
  },

])

// 文件上传 API 类
class UploadAPI {
  constructor(baseURL = '') {
    this.baseURL = baseURL;
  }

  // 上传单个文件
  async uploadFile(file, options = {}) {
    const { onProgress = null, timeout = 30000, apiKey = '' } = options;

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const formData = new FormData();
      formData.append('file', file);

      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && onProgress) {
          const progress = Math.round((event.loaded * 100) / event.total);
          onProgress(progress);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          try {
            const result = JSON.parse(xhr.responseText);
            if (result.success && result.url) {
              resolve(result);
            } else {
              reject(new Error(result.error || '上传失败'));
            }
          } catch (error) {
            reject(new Error('响应解析失败'));
          }
        } else {
          reject(new Error(`上传失败: ${xhr.status}`));
        }
      });

      xhr.addEventListener('error', () => reject(new Error('网络错误')));
      xhr.addEventListener('timeout', () => reject(new Error('请求超时')));

      xhr.timeout = timeout;

      // 构建上传 URL
      let uploadUrl = `${this.baseURL}/api/upload/single`;
      if (apiKey) {
        uploadUrl += `?api_key=${apiKey}`;
      }

      xhr.open('POST', uploadUrl);
      xhr.send(formData);
    });
  }

  // 上传多个文件
  async uploadMultipleFiles(files, options = {}) {
    const { onProgress = null, timeout = 30000, apiKey = '' } = options;

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const formData = new FormData();

      // 添加所有文件到 FormData
      files.forEach(file => {
        formData.append('files', file);
      });

      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && onProgress) {
          const progress = Math.round((event.loaded * 100) / event.total);
          onProgress(progress);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          try {
            const result = JSON.parse(xhr.responseText);
            resolve(result);
          } catch (error) {
            reject(new Error('响应解析失败'));
          }
        } else {
          reject(new Error(`上传失败: ${xhr.status}`));
        }
      });

      xhr.addEventListener('error', () => reject(new Error('网络错误')));
      xhr.addEventListener('timeout', () => reject(new Error('请求超时')));

      xhr.timeout = timeout;

      // 构建多文件上传 URL
      let uploadUrl = `${this.baseURL}/api/file/multi`;
      if (apiKey) {
        uploadUrl += `?api_key=${apiKey}`;
      }

      xhr.open('POST', uploadUrl);
      xhr.send(formData);
    });
  }

  validateFile(file) {
    const maxSize = 50 * 1024 * 1024;
    const allowedTypes = [
      'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp',
      'video/mp4', 'video/avi', 'video/mov', 'video/webm',
      'application/pdf', 'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain', 'application/zip', 'application/x-rar-compressed'
    ];

    if (file.size > maxSize) {
      return { valid: false, error: `文件大小超过限制 (${(maxSize / 1024 / 1024).toFixed(1)}MB)` };
    }

    if (file.type && !allowedTypes.includes(file.type)) {
      const ext = file.name.split('.').pop().toLowerCase();
      const allowedExts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'mp4', 'avi', 'mov', 'webm', 'pdf', 'doc', 'docx', 'txt', 'zip', 'rar'];
      if (!allowedExts.includes(ext)) {
        return { valid: false, error: `不支持的文件类型: ${file.type || ext}` };
      }
    }

    return { valid: true };
  }
}

const uploadAPI = new UploadAPI();

// 编辑器核心类
class EditorCore {
  constructor(editorRef, content, apiKey) {
    this.editorRef = editorRef;
    this.content = content;
    this.apiKey = apiKey;
  }

  // 插入文本到编辑器
  insertText(text, cursorOffset = 0) {
    if (!this.editorRef.value) return null;

    const textarea = this.editorRef.value;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;

    const beforeText = this.content.value.substring(0, start);
    const afterText = this.content.value.substring(end);

    this.content.value = beforeText + text + afterText;

    const newCursorPos = start + text.length + cursorOffset;
    return { start, newCursorPos };
  }

  // 设置光标位置
  setCursorPosition(position) {
    if (!this.editorRef.value) return;

    nextTick(() => {
      this.editorRef.value.focus();
      this.editorRef.value.setSelectionRange(position, position);
    });
  }

  // 应用加粗格式
  applyBold() {
    if (!this.editorRef.value) return;

    const textarea = this.editorRef.value;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;

    if (start === end) {
      alert('请先选择要加粗的文本');
      return;
    }

    const selectedText = this.content.value.substring(start, end);
    const result = this.insertText(`**${selectedText}**`, -2);

    if (result) {
      this.setCursorPosition(result.newCursorPos);
    }
  }

  // 从URL中提取文件名
  getFileNameFromUrl(url) {
    return url.split('/').pop() || '文件';
  }

  // 插入文件URL到编辑器
  insertFileUrl(url, fileType, fileName = null) {
    let markdownText = '';
    const displayName = fileName || this.getFileNameFromUrl(url);

    if (fileType.startsWith('image/')) {
      markdownText = `![${displayName}](${url} "${displayName}")`;
    } else if (fileType.startsWith('video/')) {
      markdownText = `<video controls src="${url}" title="${displayName}"></video>`;
    } else {
      markdownText = `[${displayName}](${url})`;
    }

    this.insertText(markdownText);
  }

  // 插入多个图片URL
  insertMultipleImageUrls(results) {
    if (!this.editorRef.value) return;

    let markdownText = '';
    results.forEach((result, index) => {
      const fileName = result.filename || this.getFileNameFromUrl(result.url);
      markdownText += `![${fileName}](${result.url} "${fileName}")`;
      if (index < results.length - 1) {
        markdownText += ' ';
      }
    });

    this.insertText(markdownText);
  }

  // 插入多个文件URL
  insertMultipleFileUrls(results) {
    if (!this.editorRef.value) return;

    let markdownText = '';
    results.forEach((result, index) => {
      const fileName = result.filename || this.getFileNameFromUrl(result.url);
      const fileType = result.mime_type || '';

      console.log(result);

      if (fileType.startsWith('image/')) {
        // 图片如果有压缩版本，优先使用压缩版本
        if (result.compressed) {
          markdownText += `![${fileName}](${result.compressed_url} "${fileName}")`;
        } else {
          markdownText += `![${fileName}](${result.url} "${fileName}")`;

        }
      } else if (fileType.startsWith('video/')) {
        markdownText += `<video controls src="${result.url}" title="${fileName}"></video>`;
      } else {
        markdownText += `[${fileName}](${result.url})`;
      }

      if (index < results.length - 1) {
        markdownText += '\n';
      }
    });

    this.insertText(markdownText);
  }
}

// 元数据工具类
class MetadataUtils {
  // 解析front matter
  static parseFrontMatter(content) {
    const frontMatterRegex = /^---\s*\r?\n([\s\S]*?)\r?\n---\s*\r?\n?([\s\S]*)$/
    const match = content.match(frontMatterRegex)

    if (!match) {
      return {
        metadata: {},
        content: content
      }
    }

    const metadataText = match[1]
    const bodyContent = match[2]
    const metadata = {}

    const lines = metadataText.split('\n')
    lines.forEach(line => {
      const trimmedLine = line.trim()
      if (!trimmedLine || trimmedLine.startsWith('#')) return

      const colonIndex = trimmedLine.indexOf(':')
      if (colonIndex > 0) {
        const key = trimmedLine.slice(0, colonIndex).trim()
        let value = trimmedLine.slice(colonIndex + 1).trim()

        if ((value.startsWith('"') && value.endsWith('"')) ||
          (value.startsWith("'") && value.endsWith("'"))) {
          value = value.slice(1, -1)
        }

        if (value === 'true') value = true
        else if (value === 'false') value = false
        else if (!isNaN(value) && value !== '' && value.trim() !== '') {
          value = Number(value)
        }
        else if (value === 'null' || value === '') {
          value = null
        }

        metadata[key] = value
      }
    })

    return {
      metadata,
      content: bodyContent
    }
  }

  // 检查是否有front matter
  static hasFrontMatter(content) {
    return /^---\s*\r?\n[\s\S]*?\r?\n---\s*\r?\n?/.test(content)
  }

  // 获取front matter内容
  static getFrontMatterContent(content) {
    if (!this.hasFrontMatter(content)) return ''

    const match = content.match(/^---\s*\r?\n([\s\S]*?)\r?\n---\s*\r?\n?([\s\S]*)$/)
    return match ? match[1] : ''
  }

  // 获取主体内容
  static getBodyContent(content) {
    if (!this.hasFrontMatter(content)) return content

    const match = content.match(/^---\s*\r?\n[\s\S]*?\r?\n---\s*\r?\n?([\s\S]*)$/)
    return match ? match[1] : content
  }
}

// 初始化编辑器核心
const editorCore = computed(() => new EditorCore(editor, content, props.apiKey))

// 计算属性
const hasFrontMatter = computed(() => MetadataUtils.hasFrontMatter(content.value, props.type))
const frontMatterContent = computed(() => MetadataUtils.getFrontMatterContent(content.value))
const bodyContent = computed(() => MetadataUtils.getBodyContent(content.value))

const editorData = computed(() => {
  if (props.type === '文章' && hasFrontMatter.value) {
    const parsed = MetadataUtils.parseFrontMatter(content.value)
    return {
      metadata: parsed.metadata,
      content: parsed.content
    }
  }
  return {
    metadata: {},
    content: content.value
  }
})

const placeholderText = computed(() => {
  const placeholderMap = {
    '笔记': '在这里记录您的笔记...',
    '文章': '在这里撰写您的文章...',
    '朋友圈': '在这里分享您的想法和见闻...'
  }
  return placeholderMap[props.type] || '在这里输入您的文本...'
})

const autoSaveStatusText = computed(() => {
  switch (autoSaveStatus.value) {
    case 'saving': return '保存中...'
    case 'unsaved': return '未保存'
    case 'saved': return '已保存'
    default: return ''
  }
})

const previewHtml = computed(() => {
  if (!content.value.trim()) {
    return '<div class="preview-placeholder">输入文本后预览将显示在这里...</div>'
  }

  try {
    let contentToRender = content.value;
    if (hasFrontMatter.value) {
      const match = content.value.match(/^---\s*\r?\n[\s\S]*?\r?\n---\s*\r?\n?([\s\S]*)$/);
      if (match && match[1]) {
        contentToRender = match[1];
      } else {
        const lines = content.value.split('\n');
        let contentStartIndex = 0;
        let foundFirstSeparator = false;
        for (let i = 0; i < lines.length; i++) {
          if (lines[i].trim() === '---') {
            if (!foundFirstSeparator) {
              foundFirstSeparator = true;
            } else {
              contentStartIndex = i + 1;
              break;
            }
          }
        }
        contentToRender = lines.slice(contentStartIndex).join('\n');
      }
    }

    let html = md(contentToRender);
    html = html.replace(/(<p>!\[.*?\]\(.*?\)<\/p>\s*)+/g, (match) => {
      const images = match.match(/<p>(!\[.*?\]\(.*?\))<\/p>/g);
      if (images && images.length > 1) {
        const combinedImages = images.map(img =>
          img.replace(/<p>(.*?)<\/p>/, '$1')
        ).join(' ');
        return `<p>${combinedImages}</p>`;
      }
      return match;
    });
    return html;
  } catch (error) {
    console.error('Markdown渲染错误:', error)
    return `<div class="preview-error">预览渲染错误: ${error.message}</div>`
  }
})

// 本地存储方法
const loadFromStorage = () => {
  try {
    const savedContent = localStorage.getItem(STORAGE_KEY)
    const savedPreviewMode = localStorage.getItem(PREVIEW_MODE_STORAGE)
    const savedMetadataVisibility = localStorage.getItem(METADATA_VISIBILITY_STORAGE)

    if (savedContent !== null) {
      content.value = savedContent
      emit('update:modelValue', savedContent)
    }
    if (savedPreviewMode !== null) {
      previewMode.value = JSON.parse(savedPreviewMode)
    }
    if (savedMetadataVisibility !== null) {
      showMetadata.value = JSON.parse(savedMetadataVisibility)
    }
  } catch (error) {
    console.error('加载本地存储失败:', error)
  }
}

const saveToStorage = () => {
  try {
    localStorage.setItem(STORAGE_KEY, content.value)
    localStorage.setItem(PREVIEW_MODE_STORAGE, JSON.stringify(previewMode.value))
    localStorage.setItem(METADATA_VISIBILITY_STORAGE, JSON.stringify(showMetadata.value))
    autoSaveStatus.value = 'saved'
  } catch (error) {
    console.error('保存到本地存储失败:', error)
    autoSaveStatus.value = 'unsaved'
  }
}

// 方法
const handleInput = () => {
  autoSaveStatus.value = 'unsaved'
  emit('update:modelValue', content.value)

  if (props.autoSave) {
    if (saveTimeout.value) {
      clearTimeout(saveTimeout.value)
    }

    saveTimeout.value = setTimeout(() => {
      autoSaveStatus.value = 'saving'
      saveContent()
    }, props.saveDelay)
  }
}

const saveContent = async () => {
  autoSaveStatus.value = 'saving'
  emit('status-change', 'saving')

  try {
    // 保存到本地存储
    saveToStorage()

    // 模拟保存延迟
    await new Promise(resolve => setTimeout(resolve, 500))

    autoSaveStatus.value = 'saved'
    emit('save', editorData.value)
    emit('status-change', 'saved')
  } catch (error) {
    autoSaveStatus.value = 'unsaved'
    emit('error', error)
    emit('status-change', 'error')
  }
}

// 工具栏方法
const applyBold = () => {
  editorCore.value.applyBold()
  handleInput()
}

const applyItalic = () => {
  if (!editor.value) return

  const textarea = editor.value
  const start = textarea.selectionStart
  const end = textarea.selectionEnd

  if (start === end) {
    alert('请先选择要设置为斜体的文本')
    return
  }

  const selectedText = content.value.substring(start, end)
  const result = editorCore.value.insertText(`*${selectedText}*`, -1)

  if (result) {
    editorCore.value.setCursorPosition(result.newCursorPos)
  }
  handleInput()
}

const insertLink = () => {
  const linkText = prompt('请输入链接文本:', '链接')
  if (linkText === null) return

  const linkUrl = prompt('请输入链接URL:', 'https://')
  if (linkUrl === null) return

  editorCore.value.insertText(`[${linkText}](${linkUrl})`)
  handleInput()
}

const insertCode = () => {
  editorCore.value.insertText('\n```\n// 在这里输入代码\n```\n')
  handleInput()
}

const insertImage = () => {
  const altText = prompt('请输入图片描述:', '')
  if (altText === null) return

  const imageUrl = prompt('请输入图片URL:', 'https://')
  if (imageUrl === null) return

  editorCore.value.insertText(`![${altText}](${imageUrl})`)
  handleInput()
}

const insertTable = () => {
  const tableTemplate = `
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 内容1 | 内容2 | 内容3 |
| 内容4 | 内容5 | 内容6 |
`
  editorCore.value.insertText(tableTemplate)
  handleInput()
}

const insertTemplate = () => {
  if (!selectedTemplate.value || !editor.value) return

  const templateIndex = parseInt(selectedTemplate.value)
  const template = templates.value[templateIndex]

  if (!template) return

  editorCore.value.insertText(template.content)
  selectedTemplate.value = ''
  handleInput()
}

const insertMetadataTemplate = () => {
  const template = templates.value[1]
  if (template && editor.value) {
    editorCore.value.insertText(template.content)
    showMetadata.value = true
    handleInput()
  }
}

const toggleMetadata = () => {
  showMetadata.value = !showMetadata.value
  saveToStorage()
}

const togglePreview = () => {
  previewMode.value = !previewMode.value
  saveToStorage()
}

// 文件上传 - 修改为支持多文件上传
const triggerFileUpload = () => {
  fileInput.value.click()
}

const handleFileUpload = async (event) => {
  const files = Array.from(event.target.files)
  if (files.length === 0) return

  event.target.value = ''

  if (!props.apiKey) {
    alert('请先设置 API Key')
    emit('error', new Error('API Key 未设置'))
    return
  }

  // 限制文件数量
  if (files.length > 20) {
    alert('一次最多上传20个文件')
    return
  }

  // 验证所有文件
  const validFiles = []
  const invalidFiles = []

  files.forEach(file => {
    const validation = uploadAPI.validateFile(file)
    if (validation.valid) {
      validFiles.push(file)
    } else {
      invalidFiles.push({ file, error: validation.error })
    }
  })

  // 显示无效文件警告
  if (invalidFiles.length > 0) {
    const errorMessages = invalidFiles.map(item => `${item.file.name}: ${item.error}`).join('\n')
    alert(`以下文件不符合要求:\n${errorMessages}`)
  }

  if (validFiles.length === 0) return

  await startUpload(validFiles)
}

const startUpload = async (files) => {
  if (files.length === 0) return

  showUploadProgress.value = true
  totalProgress.value = 0
  currentFileIndex.value = 0
  totalFiles.value = files.length
  hasUploadError.value = false

  try {
    // 使用多文件上传接口
    const result = await uploadAPI.uploadMultipleFiles(files, {
      apiKey: props.apiKey,
      onProgress: (progress) => {
        totalProgress.value = progress
      }
    })

    if (result.success) {
      // 处理上传结果
      const successfulUploads = result.results.filter(r => r.success)
      const failedUploads = result.results.filter(r => !r.success)

      if (successfulUploads.length > 0) {
        // 一次性插入所有成功的文件
        editorCore.value.insertMultipleFileUrls(successfulUploads)
      }

      // 显示上传结果
      if (failedUploads.length > 0) {
        const errorMessages = failedUploads.map(item =>
          `${item.filename}: ${item.error}`
        ).join('\n')
        alert(`以下文件上传失败:\n${errorMessages}`)
        hasUploadError.value = true
      } else {
        // 所有文件上传成功
        totalProgress.value = 100
      }
    } else {
      hasUploadError.value = true
      alert('上传失败: ' + (result.message || '未知错误'))
    }
  } catch (error) {
    console.error('上传过程出错:', error)
    hasUploadError.value = true
    alert('上传失败: ' + error.message)
  } finally {
    // 延迟隐藏进度条，让用户看到完成状态
    setTimeout(() => {
      showUploadProgress.value = false
      totalProgress.value = 0
      currentFileIndex.value = 0
      totalFiles.value = 0
      currentFileName.value = ''
    }, 2000)
  }

  handleInput()
}

// 暴露给父组件的方法
defineExpose({
  // 内容操作
  setContent: (newContent) => {
    content.value = newContent
    autoSaveStatus.value = 'saved'
    saveToStorage()
  },
  getContent: () => content.value,
  getData: () => editorData.value,

  // 编辑器操作
  focus: () => {
    if (editor.value) {
      editor.value.focus()
    }
  },
  insertText: (text) => {
    editorCore.value.insertText(text)
    handleInput()
  },

  // 状态控制
  togglePreview: () => togglePreview(),
  setPreview: (preview) => {
    previewMode.value = preview
    saveToStorage()
  },

  // 保存操作
  save: () => saveContent(),

  // 元数据操作
  insertMetadata: () => insertMetadataTemplate(),
  toggleMetadata: () => toggleMetadata(),

  // 获取状态
  getStatus: () => ({
    isDirty: autoSaveStatus.value === 'unsaved',
    isSaving: autoSaveStatus.value === 'saving',
    isPreview: previewMode.value,
    hasFrontMatter: hasFrontMatter.value
  }),

  // 本地存储操作
  clearStorage: () => {
    localStorage.removeItem(STORAGE_KEY)
    localStorage.removeItem(PREVIEW_MODE_STORAGE)
    localStorage.removeItem(METADATA_VISIBILITY_STORAGE)
    content.value = ''
    previewMode.value = false
    showMetadata.value = true
    autoSaveStatus.value = 'saved'
    emit('update:modelValue', '')
  }
})

// 监听props变化
watch(() => props.modelValue, (newValue) => {
  if (newValue !== content.value) {
    content.value = newValue
    autoSaveStatus.value = 'saved'
    saveToStorage()
  }
})

watch(() => props.type, (newType) => {
  if (newType === '文章' && !hasFrontMatter.value && content.value.trim() === '') {
    nextTick(() => {
      const template = templates.value[1];
      if (template) {
        content.value = template.content;
        showMetadata.value = true;
        handleInput()
      }
    });
  }
})

// 生命周期
onMounted(() => {
  // 加载本地存储的内容
  loadFromStorage()

  if (props.type === '文章' && !hasFrontMatter.value && content.value.trim() === '') {
    const template = templates.value[1]
    if (template) {
      content.value = template.content
      showMetadata.value = true
      handleInput()
    }
  }

  // 页面关闭前保存
  window.addEventListener('beforeunload', () => {
    if (autoSaveStatus.value === 'unsaved') {
      saveToStorage()
    }
  })
})

onUnmounted(() => {
  if (saveTimeout.value) {
    clearTimeout(saveTimeout.value)
  }
})
</script>

<style scoped>
.editor-container {
  width: 100%;
  position: relative;
}

.editor-tools {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(188, 195, 206, 0.3);
  align-items: center;
  flex-wrap: wrap;
  position: relative;
}

.editor-btn {
  padding: 6px 12px;
  height: 100%;
  background-color: #f8f9fa;
  border: 1px solid rgba(188, 195, 206, 0.5);
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
  line-height: unset !important;
  user-select: none;
}

.editor-btn:hover {
  background-color: #e9ecef;
  border-color: rgba(188, 195, 206, 0.8);
}

.template-selector {
  position: relative;
  display: inline-block;
}

.template-select {
  padding: 6px 12px;
  background-color: #f8f9fa;
  border: 1px solid rgba(188, 195, 206, 0.5);
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 120px;
}

.status-indicator {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-left: auto;
}

.mode-indicator,
.save-status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  color: #495057;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-indicator {
  background-color: #fff3cd;
  border-color: #ffeaa7;
  color: #856404;
}

.save-status {
  color: #95a5a6;
  transition: color 0.3s ease;
}

.save-status.saved {
  color: #27ae60;
}

/* 编辑器容器 */
.editor-content {
  position: relative;
}

/* 元数据区域 */
.metadata-section {
  border: 1px solid #e9ecef;
  border-radius: 4px;
  margin-bottom: 10px;
  background: #f8f9fa;
}

.metadata-header {
  padding: 8px 12px;
  background: #e9ecef;
  border-bottom: 1px solid #dee2e6;
  font-size: 14px;
  font-weight: 500;
}

.metadata-title {
  color: #495057;
}

.metadata-tip {
  color: #6c757d;
  font-size: 12px;
  font-weight: normal;
}

.metadata-content {
  padding: 12px;
}

.metadata-code {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.4;
  color: #495057;
  white-space: pre-wrap;
  word-break: break-all;
  box-shadow: none;
  background-color: transparent;
}

/* 编辑器 */
.editor-textarea {
  width: 100%;
  height: 70vh;
  padding: 15px;
  outline: none;
  border: 1px solid rgba(188, 195, 206, 0.5);
  border-radius: 4px;
  font-size: 16px;
  line-height: 1.5;
  resize: vertical;
  font-family: inherit;
  transition: border-color 0.2s ease, background-color 0.2s ease;
}

.editor-textarea.with-metadata {
  height: calc(70vh - 150px);
}

.editor-textarea:focus {
  background-color: rgba(188, 195, 206, 0.05);
}

.preview-area {
  width: 100%;
  height: 70vh;
  background-color: #fff;
  border: 1px solid transparent;
  border-radius: 4px;
  font-size: 16px;
  line-height: 1.5;
  overflow-y: auto;
}

.preview-area::-webkit-scrollbar {
  display: none;
}

/* 上传状态样式 */
.upload-status {
  margin-bottom: 15px;
  border: 1px solid rgba(188, 195, 206, 0.3);
  border-radius: 4px;
  overflow: hidden;
  background-color: #f8f9fa;
}

.upload-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid rgba(188, 195, 206, 0.3);
  font-size: 14px;
  font-weight: 500;
}

.upload-progress-text {
  color: #495057;
}

.current-file-name {
  color: #6c757d;
  font-size: 12px;
  margin-left: 5px;
}

.upload-percentage {
  color: #3498db;
  font-weight: 600;
}

.upload-progress {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
}

.progress-bar {
  flex-grow: 1;
  height: 8px;
  background-color: #ecf0f1;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #3498db;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-fill.upload-error {
  background-color: #e74c3c;
}

.progress-text {
  font-size: 12px;
  min-width: 60px;
  text-align: right;
}

.success-text {
  color: #27ae60;
}

.error-text {
  color: #e74c3c;
}

.preview-placeholder {
  color: #95a5a6;
  font-style: italic;
  text-align: center;
  padding: 40px 20px;
}

.preview-error {
  color: #e74c3c;
  background-color: #fdf2f2;
  padding: 10px;
  border-radius: 4px;
  border-left: 4px solid #e74c3c;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .editor-tools {
    flex-direction: column;
    align-items: stretch;
    display: inline-block;
    width: 100%;
  }

  .editor-btn,
  .template-select {
    /* width: 100%; */
    margin-bottom: 5px;
    margin-right: 10px;
  }

  .status-indicator {
    margin-left: 0;
    justify-content: space-between;
    width: 100%;
  }

  .metadata-header {
    padding: 6px 10px;
    font-size: 13px;
  }

  .metadata-content {
    padding: 8px 10px;
  }

  .metadata-code {
    font-size: 12px;
  }
}
</style>