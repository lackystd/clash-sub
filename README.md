# Clash 订阅工具

JustMySocks 订阅自动更新 + 本地配置托管方案。

## 文件说明

| 文件 | 说明 |
|------|------|
| `jms2clash.py` | 从 JustMySocks 订阅拉取节点，生成 Clash YAML 配置 |
| `clash_config.txt` | 生成的 Clash 配置文件 |
| `serve_clash.bat` | 手动启动 HTTP 服务托管配置（交互模式） |
| `startup_clash.bat` | 一键更新订阅 + 启动 HTTP 服务（静默模式） |

## 使用方法

### 1. 手动更新订阅

```bash
python jms2clash.py "<订阅链接>" -o clash_config.txt
```

### 2. 启动本地配置服务

双击 `serve_clash.bat`，在 Clash Verge 等客户端中添加订阅地址：

```
http://127.0.0.1:18901/clash_config.txt
```

### 3. 开机自启

已通过快捷方式注册到 Windows 启动文件夹，开机会自动执行：

1. 拉取最新 JustMySocks 订阅，更新 `clash_config.txt`
2. 启动 HTTP 服务在 `127.0.0.1:18901` 托管配置

查看/管理启动项：`Win+R` → 输入 `shell:startup`

## 支持的节点类型

- **Shadowsocks** (ss://) — SIP002 及传统格式
- **VMess** (vmess://) — 支持 tcp / ws / grpc / h2 传输

## 依赖

- Python 3.10+
- PyYAML (`pip install pyyaml`)
