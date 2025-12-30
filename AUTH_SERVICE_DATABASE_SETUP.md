# 配置 Gateway Service 使用 auth_service 数据库

**日期:** 2025-12-30  
**问题:** Gateway Service 当前使用 `gateway_db` 数据库，但需要改为使用 `auth_service` 数据库存储限流记录

## 问题分析

Gateway Service 默认使用 `gateway_db` 数据库，但您希望将限流记录存储在 `auth_service` 数据库中。

## 解决方案

### 方法 1: 使用 .env 文件（推荐）

创建或编辑 `.env` 文件，设置数据库名称：

```bash
# 在 gateway-service 目录下创建或编辑 .env 文件
MYSQL_DATABASE=auth_service
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password

# 确保 MySQL 存储已启用
RATE_LIMIT_MYSQL_ENABLED=true
RATE_LIMIT_MYSQL_ASYNC=false
```

### 方法 2: 使用环境变量

在启动服务前设置环境变量：

```bash
export MYSQL_DATABASE=auth_service
python run.py
```

### 方法 3: 在启动命令中设置

```bash
MYSQL_DATABASE=auth_service python run.py
```

## 验证步骤

### 1. 检查数据库连接

```bash
python scripts/test_auth_service_db.py
```

这个脚本会：
- 测试连接到 `auth_service` 数据库
- 检查 `rate_limit_records` 表是否存在
- 测试存储一条记录
- 验证记录是否成功存储

### 2. 检查现有记录

```bash
python scripts/check_auth_service_records.py
```

### 3. 重启 Gateway Service

修改配置后，必须重启服务：

```bash
# 停止当前服务（Ctrl+C）
# 然后重新启动
python run.py
```

### 4. 测试限流记录

发送一些请求触发限流，然后检查数据库：

```bash
# 检查记录
python scripts/check_auth_service_records.py

# 或者直接查询 MySQL
mysql -u root -p auth_service -e "SELECT * FROM rate_limit_records ORDER BY updated_at DESC LIMIT 10;"
```

## 配置示例

完整的 `.env` 文件示例：

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8001
DEBUG=false

# MySQL Configuration - 使用 auth_service 数据库
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=auth_service

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_PER_DAY=10000

# MySQL Rate Limit Storage
RATE_LIMIT_MYSQL_ENABLED=true
RATE_LIMIT_MYSQL_ASYNC=false  # 使用同步模式确保记录被存储

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 注意事项

1. **数据库必须存在**: 确保 `auth_service` 数据库已创建
2. **表必须存在**: 确保 `rate_limit_records` 表已创建
3. **权限**: 确保 MySQL 用户有权限访问 `auth_service` 数据库
4. **重启服务**: 修改配置后必须重启服务才能生效

## 创建表（如果需要）

如果 `auth_service` 数据库中没有 `rate_limit_records` 表，可以运行：

```sql
USE auth_service;

CREATE TABLE IF NOT EXISTS rate_limit_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    identifier VARCHAR(255) NOT NULL,
    window_type VARCHAR(20) NOT NULL,
    route_path VARCHAR(500),
    request_count INT NOT NULL DEFAULT 0,
    window_start DATETIME NOT NULL,
    window_end DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_identifier_window_route (identifier, window_type, route_path(255)),
    INDEX idx_identifier (identifier),
    INDEX idx_window_type (window_type),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 故障排查

### 问题: 记录仍然没有出现

1. **检查配置**:
   ```bash
   python -c "from app.settings import get_settings; s = get_settings(); print(f'Database: {s.mysql_database}')"
   ```

2. **检查日志**: 查看应用日志中是否有 MySQL 存储相关的消息

3. **检查连接**: 运行 `python scripts/test_auth_service_db.py` 验证连接

4. **检查表**: 确认表存在于 `auth_service` 数据库中

### 问题: 连接失败

- 检查 MySQL 服务是否运行
- 检查用户名和密码是否正确
- 检查用户是否有访问 `auth_service` 数据库的权限

## 快速检查清单

- [ ] `.env` 文件中设置了 `MYSQL_DATABASE=auth_service`
- [ ] `auth_service` 数据库存在
- [ ] `rate_limit_records` 表存在于 `auth_service` 数据库中
- [ ] `RATE_LIMIT_MYSQL_ENABLED=true`
- [ ] `RATE_LIMIT_MYSQL_ASYNC=false` (推荐使用同步模式)
- [ ] Gateway Service 已重启
- [ ] 运行了测试脚本验证连接

