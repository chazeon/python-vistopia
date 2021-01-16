# 理想国客户端

## 用法

### 安装

```
pip3 install -r requirements.txt
```

### 运行

需自行通过抓包获取 API 令牌（token）。

执行以下命令运行：
```
python3 vistopian/main.py --token [token] [subcommand]
```

子命令目前支持：
- `subscriptions`: 列出所有已订阅节目
- `show-content`: 节目章节信息
- `save-show`: 保存节目至本地，并添加封面和 ID3 信息

## 不足

目前不支持 API 签名。

## 源代码开源授权

采用 [MIT 开源授权](./LICENCE)。