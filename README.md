# python-vistopia

看理想命令行客户端 / 下载器

[![codecov](https://codecov.io/gh/chazeon/python-vistopia/graph/badge.svg?token=UESNMCBB87)](https://codecov.io/gh/chazeon/python-vistopia)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 用法

### 安装

```
pip3 install -r requirements.txt
```

### 运行

需自行通过抓包获取 API 令牌（token）。部分开放节目（如《八分》）无须令牌。

执行以下命令运行：
```
python3 vistopia/main.py --token [token] [subcommand]
```

子命令目前支持：
- `search`: 搜索节目
- `subscriptions`: 列出所有已订阅节目
- `show-content`: 节目章节信息
- `save-show`: 保存节目至本地，并添加封面和 ID3 信息
- `save-transcript`: 保存节目文稿至本地

## 不足

目前不支持 API 签名。

## 源代码开源授权

采用 [MIT 开源授权](./LICENCE)。
