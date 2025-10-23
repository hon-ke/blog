<template>
    <div class="layout">
        <Header></Header>
        <section id="core" class="container off-canvas off-canvas-sidebar-show">
            <aside id="aside" class="off-canvas-sidebar">
                <div class="probes"></div>
                <section class="sticky">

                    <!-- 文章menu -->
                    <ul class="header_nav reset-ul uni-bg uni-shadow">
                        <li v-for="x in categoryData" @click="setInfo('post', x.name)" class="menu-item"
                            :class="[x.icon, { 'current-menu-item': activeMenu === x.name }]">
                            <a>{{ x.name }}</a>
                        </li>
                    </ul>

                    <!-- 页面menu -->
                    <ul class="header_nav reset-ul uni-bg uni-shadow">
                        <li v-for="x in pagesData" @click="setInfo('page', x)" class="menu-item"
                            :class="[x.icon, { 'current-menu-item': activeMenu === x }]">
                            <a>{{ x.title }}</a>
                        </li>

                        <li @click="setInfo('page', '新建page')" class="menu-item"
                            :class="['czs-chemistry-l', { 'current-menu-item': activeMenu === '新建page' }]">
                            <a>新建</a>
                        </li>
                    </ul>

                    <!-- 设置 -->
                    <ul class="header_nav reset-ul uni-bg uni-shadow">
                        <li>
                            <input type="password" class="api-key_input" placeholder="请输入API_KEY" v-model="apiKey"
                                @input="saveApiKey">
                        </li>
                    </ul>

                    <div class="submit-btn link" @click="submit">发布内容</div>

                </section>
            </aside>
            <a href="#close" class="off-canvas-overlay"></a>
            <main class="admin-main">
                <MarkdownEditor v-model="editorText" :type="type" :api-key="apiKey" @save="handleSave"
                    @update:modelValue="handleContentUpdate" @status-change="handleStatusChange"
                    @upload-progress="handleUploadProgress" @error="handleError" ref="editorRef" />
                
            </main>
        </section>
    </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import Header from '../components/Header.vue'
import MarkdownEditor from '@/components/Editor.vue'
import Empty from '@/components/Empty.vue'

import axios from 'axios'

const editorRef = ref(null)
const editorText = ref('')
const apiKey = ref('')
const symble = ref('create')

// 当前编辑的类别 post,note,page
const type = ref('post')
// 当前active的menu
const activeMenu = ref("笔记")

// 数据
const categoryData = ref([])
const pagesData = ref([])
const submitData = ref({})


// 或者为每个分类分配图标
const assignIconsToCategories = (categories) => {
    categories.push("新建");

    const categoryIconList = [
        "czs-cup-l",
        "czs-code-l",
        "czs-heart-l",
        "czs-chemistry-l",
        "czs-commed2-l",
        "czs-dashboard-l",
        "czs-crown-l",
        "czs-folder-l",
        "czs-fingerprint-l",
        "czs-moments",
    ]
    return categories.map((category, index) => {
        const icon = categoryIconList[index % categoryIconList.length]
        return {
            name: category,
            icon: icon
        }
    })
}

// 使用普通对象而不是 ref，避免 .value 嵌套问题
const PostModel = {
    // 核心内容
    title: "",
    excerpt: "",
    tag: "",
    category: "",
    cover: "",
    is_top: false,
    is_locked: false,
}

const NoteModel = {
    // 核心内容
    category: "笔记",
    is_top: false,
    is_locked: false,
}

// 页面模型对象
const PageModel = {
    // 页面标题
    title: "",
    // 页面描述
    description: "",
    // 页面链接
    link: "",
    // 图标
    icon: "",
    // 是否启用
    is_active: true,
    // 排序权重
    order: 0,
}

// 保存API Key
const saveApiKey = () => {
    localStorage.setItem('api-key', apiKey.value)
}

// 编辑器事件处理
const handleSave = (data) => {
    // console.log('内容已保存:', data)
}

const handleContentUpdate = (content) => {
    // console.log('内容更新:', content)
}

const handleStatusChange = (status) => {
    // console.log('状态变化:', status)
}

const handleUploadProgress = (progress) => {
    // console.log('上传进度:', progress)
}

const setState = () => {
    // page需要重新加载数据更新
    if (type.value == "page") {
        localStorage.setItem("type", null)
        return
    }
    localStorage.setItem("type", type.value)
    localStorage.setItem("activeMenu", activeMenu.value)
}

const loadState = () => {
    const savedType = localStorage.getItem("type")
    const savedActiveMenu = localStorage.getItem("activeMenu")
    if (savedType) {
        type.value = savedType
    }
    if (savedActiveMenu) {
        activeMenu.value = savedActiveMenu
    }
}
// 设置类型
const setInfo = (newType, activeMenuData) => {
    type.value = newType
    activeMenu.value = activeMenuData

    if (activeMenuData == "新建" || activeMenuData == "新建page") {
        // 初始化
        PostModel.category = ""
        Object.assign(PageModel, {
            // 页面标题
            title: " 首页导航中显示的名字",
            // 页面描述
            description: " 关于页面的描述，可选",
            // 页面链接
            link: " 访问页面的链接，以 / 开头",
            // 图标
            icon: " 首页导航中显示的icon,可以访问 /icons 寻找类名",
            // 是否启用
            is_active: true,
            // 排序权重
            order: 0,
        });
        setState()
        editorText.value = ""
        insetMetaData(type.value)
        return
    }

    if (activeMenuData == '笔记') {
        type.value = "note"
    }
    // 更新 PostModel 的 category
    if (newType === 'post') {
        PostModel.category = activeMenuData
    }

    if (newType == "page") {
        axios.get(`/api/pages/${activeMenuData.title}`).then(res => {
            const { content, ...metadata } = res.data;
            const frontMatter = objectToFrontMatter(metadata);
            editorText.value = frontMatter + (content || '');
            Object.assign(PageModel, metadata);
            symble.value = "update"
        }).catch(err => {
            console.log(err);
            symble.value = "create"
            Object.assign(PageModel, activeMenuData);
            const frontMatter = objectToFrontMatter(PageModel);
            editorText.value = frontMatter + '';
        });
        setState();
        return; // 注意这里返回，不执行后面的insetMetaData
    }

    setState()
    insetMetaData(type.value)

}

const insetMetaData = (type) => {
    let meta = {
        post: PostModel,
        note: NoteModel,
        page: PageModel
    }

    const selectedModel = meta[type]
    if (selectedModel) {
        // 删除第一组元数据
        editorText.value = removeFirstFrontMatter(editorText.value)

        const frontMatter = objectToFrontMatter(selectedModel)
        editorText.value = frontMatter + editorText.value
    }
}

// 删除第一组 front matter
const removeFirstFrontMatter = (content) => {
    const frontMatterRegex = /^---\s*\r?\n[\s\S]*?\r?\n---\s*\r?\n?/

    if (content) {

        return content.replace(frontMatterRegex, '')
    } else {
        return content
    }
}

// 改进的 obj2frontMatter 函数 - 值留空白，不显示任何内容
const objectToFrontMatter = (data) => {
    if (!data || typeof data !== 'object') {
        return '---\n---\n\n'
    }

    const lines = ['---']

    Object.entries(data).forEach(([key, value]) => {
        let stringValue

        if (value === null || value === undefined || value === "") {
            // 空值完全留空，不显示任何内容
            stringValue = ""
        } else if (typeof value === 'string') {
            // 对包含特殊字符的字符串使用引号
            if (/[:{}\[\],&*#?|<>=!%@`\n]/.test(value)) {
                stringValue = `"${value.replace(/"/g, '\\"')}"`
            } else {
                stringValue = value
            }
        } else if (Array.isArray(value)) {
            stringValue = value.length > 0 ? `[${value.join(', ')}]` : ""
        } else if (value instanceof Date) {
            stringValue = value.toISOString()
        } else if (typeof value === 'object') {
            // 简单处理嵌套对象，转换为 JSON
            stringValue = JSON.stringify(value)
        } else if (typeof value === 'boolean') {
            stringValue = value.toString()
        } else if (typeof value === 'number') {
            stringValue = value.toString()
        } else {
            stringValue = ""
        }

        // 如果值为空，只保留键和冒号
        lines.push(`${key}:${stringValue ? ' ' + stringValue : ''}`)
    })

    lines.push('---', '')
    return lines.join('\n') + '\n\n'
}

// 构建提交数据
const buildSubmitData = () => {
    const content = editorText.value.trim()

    // 解析 front matter 和内容
    const parsed = parseFrontMatter(content)
    const metadata = parsed.metadata
    const bodyContent = parsed.content

    // 根据类型构建不同的数据
    if (type.value === 'post') {
        return {
            title: metadata.title || "",
            content: bodyContent,
            excerpt: metadata.excerpt || "",
            tag: metadata.tag || "",
            category: metadata.category || activeMenu.value,
            cover: metadata.cover || "",
            is_top: metadata.is_top || false,
            is_locked: metadata.is_locked || false,
        }
    } else if (type.value === 'page') {
        return {
            title: metadata.title || "",
            description: metadata.description || "",
            link: metadata.link || "",
            icon: metadata.icon || "",
            content: bodyContent,
            is_active: metadata.is_active !== false,
            order: metadata.order || 0,
            show_in_nav: metadata.show_in_nav !== false,
        }
    } else {
        // note 类型
        return {
            content: bodyContent,
            category: "笔记",
            is_top: metadata.is_top || false,
            is_locked: metadata.is_locked || false,
        }
    }
}

// 解析 front matter
const parseFrontMatter = (content) => {
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

            // 移除引号
            if ((value.startsWith('"') && value.endsWith('"')) ||
                (value.startsWith("'") && value.endsWith("'"))) {
                value = value.slice(1, -1)
            }

            // 类型转换
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

// 验证输入
const validateInput = () => {
    if (!editorText.value.trim()) {
        alert('内容不能为空')
        return false
    }

    if (!apiKey.value) {
        alert('请先输入 API Key')
        return false
    }

    return true
}



// 发布内容
const submit = async () => {
    try {


        if (!validateInput()) return
        console.log(1213);

        let response = {}
        const data = buildSubmitData()
        submitData.value = data

        let api = {
            post: "/api/admin/posts/",
            note: "/api/admin/posts/",
            page: "/api/admin/pages/",
        }

        if (symble.value == "update") {
            api = {
                post: "/api/admin/posts/",
                note: "/api/admin/posts/",
                page: "/api/admin/pages/",
            }

            response = await axios.put(api[type.value], data, {
                headers: {
                    'accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                params: {
                    api_key: apiKey.value
                },
                timeout: 10000
            })
        } else {
            response = await axios.post(api[type.value], data, {
                headers: {
                    'accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                params: {
                    api_key: apiKey.value
                },
                timeout: 10000
            })
        }


        console.log('发布成功:', response.data)
        handleSuccess(response.data)

    } catch (error) {
        console.error('发布失败:', error)
        handleError(error)
    }
}

// 成功处理
const handleSuccess = (responseData) => {
    editorText.value = ''
    const successMessage = `发布成功！\n类型: ${type.value}\nID: ${responseData.id}`
    alert(successMessage)
    console.log('发布的内容ID:', responseData.id)
}

// 错误处理
const handleError = (error) => {
    let errorMessage = '发布失败，请重试'

    if (error.response) {
        const errorData = error.response.data
        if (errorData.detail) {
            errorMessage = errorData.detail
        } else if (errorData.message) {
            errorMessage = errorData.message
        }

        switch (error.response.status) {
            case 400:
                errorMessage = '请求数据格式错误'
                break
            case 401:
                errorMessage = 'API Key 无效或已过期'
                break
            case 403:
                errorMessage = '没有权限执行此操作'
                break
            case 409:
                if (errorMessage.includes('标题')) {
                    errorMessage = '文章标题已存在，请修改标题后重试'
                }
                break
            case 422:
                errorMessage = '数据验证失败，请检查输入内容'
                break
        }
    } else if (error.request) {
        errorMessage = '网络连接失败，请检查网络连接'
    }

    alert(`发布失败: ${errorMessage}`)

    if (error.response && error.response.status === 401) {
        localStorage.removeItem('api-key')
        apiKey.value = ''
    }
}

onMounted(() => {
    // 从本地存储加载API Key
    const savedApiKey = localStorage.getItem('api-key')
    if (savedApiKey) {
        apiKey.value = savedApiKey
    }

    loadState()
    // 获取分类
    axios.get("/api/posts/categories").then(res => {
        categoryData.value = assignIconsToCategories(res.data)
    }).catch(err => {
        categoryData.value = []
    })

    // 获取分类
    axios.get("/api/pages/").then(res => {
        pagesData.value = res.data
    }).catch(err => {
        pagesData.value = []
    })

    // 默认插入笔记元数据
    if (!editorText.value.trim()) {
        insetMetaData(type.value)
    }
})
</script>

<style scoped>
/* 保持原有的样式 */
@import "@/assets/css/style.css";
@import "@/assets/css/icons.css";
@import url(@/assets/css/hljs.css);

.admin-main {
    background-color: #fff;
    width: 100%;
    border-radius: 0.6rem;
    padding: 15px;
    box-shadow: 0 0 0 0.5px rgba(188, 195, 206, 0.1), 0 2px 10px rgba(48, 55, 66, 0.06);
}

.api-key_input {
    width: 100%;
    border: none;
    outline: none;
    padding: 8px 12px;
    background: transparent;
}

.editor-btn {
    padding: 6px 12px;
    background-color: #f8f9fa;
    border: 1px solid rgba(188, 195, 206, 0.5);
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s ease;
    user-select: none;
}

.editor-btn:hover {
    background-color: #e9ecef;
    border-color: rgba(188, 195, 206, 0.8);
}

.submit-btn {
    background-color: #fff;
    padding: 0.4rem;
    text-align: center;
    transition: background-color .3;
    border-radius: 0.6rem;
}


.submit-btn:hover {
    background-color: #3366ff;
    color: #fff;

}
</style>