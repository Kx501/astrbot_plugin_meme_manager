# 更新日志

## v3.16 - 2025-11-11

### 新增功能
- **Cloudflare R2 图床支持**
  - 新增 Cloudflare R2 作为可选图床后端
  - 在配置中可以选择使用 Stardots 或 Cloudflare R2
  - 支持完整的 R2 图床功能：上传、删除、同步、状态检查

### 技术改进
- 重构图床提供者架构，支持多后端
- 添加图床提供者接口规范 (`image_host/interfaces/image_host.py`)
- 实现 Cloudflare R2 提供者 (`image_host/providers/cloudflare_r2_provider.py`)
- 更新配置架构 (`_conf_schema.json`) 支持 R2 配置项

### 配置说明
在插件配置中添加以下选项：
```yaml
image_host: "cloudflare_r2"  # 选择图床类型
image_host_config:
  cloudflare_r2:
    account_id: "your_account_id"           # Cloudflare Account ID
    access_key_id: "your_access_key_id"     # R2 API Access Key ID
    secret_access_key: "your_secret_access_key"  # R2 API Secret Access Key
    bucket_name: "your_bucket_name"         # R2 Bucket 名称
    public_url: "https://your-domain.com"   # 可选: CDN 域名
```

## v3.15 - 2025-11-11

### 功能
- 表情包管理器初始版本
- 支持 AI 自动发送表情包
- WebUI 管理界面
- Stardots 图床支持