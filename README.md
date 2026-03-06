# 墨榜 v1

自媒体运营工具，当前包含：

- 热点查询（抖音真实热搜 / 小红书探索页）
- 对标分析（示例返回）
- AI 选题生成（结构化输出）
- 静态首页展示

## 项目结构

```text
.
├── app/
│   └── routes/
├── static/
├── main.py
├── requirements.txt
└── SPEC.md
```

## 运行方式

```bash
pip install -r requirements.txt
python main.py
```

默认监听：`http://0.0.0.0:8081`

## 当前说明

这个版本已经可以：
- 打开首页
- 调用趋势、分析、选题、健康检查接口
- 热点模块接入真实数据（抖音热搜 + 小红书探索页）
- AI 选题输出更结构化，可直接用于内容策划
