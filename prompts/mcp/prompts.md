# constitution

制定以代码质量、测试标准、用户体验一致性及性能要求为核心的原则

# create feature mcp server specify

构建一个简单的标准化的 mcp server，使用 fastapi-mcp 作为整体框架, 实现 开通邮箱账号权限 和 开通 git 账号权限 功能

# 核心功能

开通邮箱账号权限：接收姓名，身份证号, 验证身份证号合法， 返回 姓名的英文全拼@email.com 和 一个随机的密码
开通 git 账号权限：接收姓名，身份证号，验证身份证号合法， 返回 姓名的英文全拼@git.com 和 一个随机的密码

# 技术栈

- **Runtime**: Python 3.12+ (uv)
- **Framework**: fastapi-mcp

# 定义配置 .env

```env
PORT=9102
```

## main.py

python main.py : 启动 mcp server

# create plans for rag backend feature

实现所有需求
生成.env 配置文件
添加集成测试
运行集成测试，根据测试结果修复问题
