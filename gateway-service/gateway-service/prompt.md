## 一、 统一代码规范（Python3
### 1.  技术栈与版本约束
- 编程语言：Python 3.10
- 核心框架：Django 4.2 / FastAPI 0.104
- 数据库：MySQL 8.0 + asyncmy
- 代码检查工具：flake8 + black（格式化）
- Consul：服务发现、配置中心、健康检查（Python 客户端：python-consul）。
-  etcd：分布式键值存储，用于服务发现和配置管理（Python 客户端：etcd3）。
- Prometheus + Grafana：监控和指标收集（Python 客户端：prometheus-client）。
- Zipkin/Jaeger：分布式追踪（Python 客户端：py_zipkin、jaeger-client）。


任务：开发【auth service】，属于【cloud resource management system】项目
技术栈：Python 3.10 + FastAPI  + MySQL 8.0 + Redis + gRPC
代码规范：严格遵循已提供的Python代码规范（命名/格式/分层架构）[Developer_coding_rules_Principles] 文件规范
功能需求：
1.  核心功能：【 参考gateway-service.md和gateway-service_layers.txt文件 】
2.  输入参数：【自动生成并注释】
3.  输出结果：【自动生成并注释】
4.  边界条件：【如参数为空、数据不存在的处理逻辑】
5.  全英文注饰无中文
6.  【Gateway-service.md]所有功能模块严格按照[gateway-service_layers.txt]结构规范生成
额外要求：
1.  生成完整代码，包括接口层、服务层、数据层
2.  附带对应的pytest单元测试代码
3.  生成模块说明文档，注明依赖的其他模块
4.  每一个类/函数需要注释
5.  输出代码后需要总结每一个功能和逻辑关系
6.  在所有.env中增加环境变量配置信息
