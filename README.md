# Clash 订阅工具

JustMySocks 订阅自动更新 + 本地配置托管方案。

## 文件说明

| 文件 | 说明 |
|------|------|
| `jms2clash.py` | 从 JustMySocks 订阅拉取节点，生成 Clash YAML 配置 |
| `subscription_url.txt` | 存放订阅链接（敏感文件，不纳入 Git） |
| `output/clash_config.txt` | 生成的 Clash 配置文件（敏感文件，不纳入 Git） |
| `serve_clash.bat` | 手动启动 HTTP 服务，仅托管 output 文件夹 |
| `startup_clash.bat` | 一键更新订阅 + 启动 HTTP 服务（静默模式，开机自启） |
| `update_sub.bat` | 手动更新订阅（从 `subscription_url.txt` 读取链接） |

## 使用方法

### 1. 配置订阅链接

将订阅链接写入 `subscription_url.txt`（每行一个，`#` 开头为注释）：

```
https://jmssub.net/members/getsub.php?service=...
```

### 2. 更新订阅

双击 `update_sub.bat`，或手动执行：

```bash
python jms2clash.py --file subscription_url.txt -o clash_config.txt
```

也可以直接传入链接：

```bash
python jms2clash.py "<订阅链接>" -o clash_config.txt
```

### 3. 启动本地配置服务

双击 `serve_clash.bat`，在 Clash Verge 等客户端中添加订阅地址：

```
http://127.0.0.1:18901/clash_config.txt
```

### 4. 开机自启

已通过快捷方式注册到 Windows 启动文件夹，开机会自动执行：

1. 拉取最新 JustMySocks 订阅，更新 `output/clash_config.txt`
2. 启动 HTTP 服务在 `127.0.0.1:18901` 托管配置（仅暴露 output 文件夹）

查看/管理启动项：`Win+R` → 输入 `shell:startup`

## 支持的节点类型

- **Shadowsocks** (ss://) — SIP002 及传统格式
- **VMess** (vmess://) — 支持 tcp / ws / grpc / h2 传输

## 依赖

- Python 3.10+
- PyYAML (`pip install pyyaml`)
