# Cloudflare R2 图床功能优化与 Bug 修复

## 概述
本次PR修复了多个关键bug，优化了Cloudflare R2图床的文件管理逻辑，并添加了详细的日志记录以便问题排查。

## 主要修改

### 1. 修复关键Bug 🐛

#### 修复 `AttributeError: 'MemeSender' object has no attribute 'logger'`
- **问题**: 插件启动时崩溃，无法加载
- **原因**: 在 `__init__` 方法中过早使用 `self.logger`，而此时 logger 还未初始化
- **解决方案**: 延迟日志记录，将R2初始化日志推迟到 logger 初始化完成后
- **修改文件**: `main.py`

#### 修复同步进程配置传递错误
- **问题**: 同步失败，报错 `KeyError: 'key'`
- **原因**: `run_sync_process` 函数无法正确识别配置格式
- **解决方案**: 添加配置格式自动检测，支持多种配置结构
- **修改文件**: `image_host/img_sync.py`

#### 添加缺失的 `__init__.py` 文件
- **问题**: 插件加载器无法正确识别插件类
- **解决方案**: 添加缺失的 `__init__.py` 文件
- **修改文件**: `__init__.py` (新建)

### 2. 优化 Cloudflare R2 文件管理 📁

#### 所有文件上传到 `memes/` 文件夹
- **修改前**: 文件直接上传到存储桶根目录
- **修改后**: 所有文件上传到 `memes/` 文件夹，保持分类结构
- **路径格式**: `memes/{category}/{filename}`
- **示例**:
  - `memes/angry/xxx.jpg`
  - `memes/happy/yyy.gif`
- **好处**:
  - 避免污染存储桶根目录
  - 文件管理更加清晰
  - 便于与其他应用共用存储桶
- **修改文件**: `image_host/providers/cloudflare_r2_provider.py`

#### 只检查和同步 `memes/` 文件夹
- **修改**: `get_image_list()` 现在只列出 `memes/` 前缀的文件
- **好处**:
  - 避免误删存储桶中的其他文件
  - 同步速度更快（只扫描必要文件）
  - 提高安全性
- **修改文件**: `image_host/providers/cloudflare_r2_provider.py`

#### 改进 S3 键名解析
- **修改**: `_parse_s3_key()` 正确解析 `memes/` 前缀，准确提取分类信息
- **修改文件**: `image_host/providers/cloudflare_r2_provider.py`

### 3. 改进日志记录 📝

#### 添加详细的同步日志
- 记录同步进程启动信息（任务类型、本地目录）
- 记录上传/下载任务开始和完成
- 记录进程退出码
- 异常时记录详细堆栈信息
- **好处**: 问题排查更加方便
- **修改文件**: `image_host/img_sync.py`

### 4. 文档优化 📖

#### 简化 R2 配置 YAML
- **修改**: README.md 中只保留核心配置项，删除冗余内容
- **好处**: 用户配置更加简单，减少混淆
- **修改文件**: `README.md`

## 版本更新
- **版本号**: v3.18
- **更新内容**: 修复关键bug，优化R2图床功能

## 测试情况 ✅
- 插件可以正常加载
- Cloudflare R2 初始化成功
- 同步到云端功能正常工作
- 文件正确上传到 `memes/` 文件夹
- 只同步 `memes/` 文件夹内的文件
- 详细的日志记录

## 破坏性变更 ⚠️

**重要**: 此PR包含破坏性变更

- 之前上传到存储桶根目录的文件不会被自动管理
- 建议用户在升级前备份数据
- 升级后首次同步会重新上传所有文件到 `memes/` 文件夹

## 使用示例

### 配置示例
```yaml
# Cloudflare Account ID (account_id)
account_id: "your_account_id"
# R2 Access Key ID (access_key_id)
access_key_id: "your_access_key_id"
# R2 Secret Access Key (secret_access_key)
secret_access_key: "your_secret_access_key"
# R2 Bucket 名称 (bucket_name)
bucket_name: "your_bucket_name"
# 自定义CDN域名 (可选) (public_url)
# 例如: https://你的域名.com
public_url: "https://你的域名.com"
```

### 同步命令
```
/表情管理 同步到云端
```

文件将上传到：`https://你的域名.com/memes/{category}/{filename}`

## 相关Issue
- 修复 PR #34 中的同步失败问题
- 优化 Cloudflare R2 图床使用体验

## 提交记录
- a0acf27: feat: 所有文件上传到 R2 的 memes 文件夹，只检查和同步该文件夹
- d22abba: 修复: 延迟 logger 初始化，避免 AttributeError; 更新版本号到 v3.18
- dc1ab18: 添加缺失的 __init__.py 文件
- 30f74f1: 简化 R2 配置 YAML，只保留核心配置项