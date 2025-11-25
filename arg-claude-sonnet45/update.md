# 手动更新

1. 修改 main.py 的逻辑，引入 cli main
2. 修改 pyproject.toml
   [build-system]
   requires = ["setuptools>=45", "wheel"]
   build-backend = "setuptools.build_meta"
3. readme.md 编码格式改成 utf-8
4. 添加 cli 的集成测试，并运行调试
