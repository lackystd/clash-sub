#!/usr/bin/env python3
"""
JustMySocks subscription to Clash config converter.

Usage:
    python jms2clash.py <subscription_url> [output.yaml]
    python jms2clash.py --url <subscription_url> -o output.yaml
"""

import argparse
import base64
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import yaml


def b64_decode(s: str) -> str:
    """Base64 decode with proper padding."""
    s = s.strip()
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    return base64.b64decode(s).decode("utf-8")


def fetch_subscription(url: str) -> str:
    """Fetch and decode subscription content."""
    req = urllib.request.Request(url, headers={"User-Agent": "ClashForAndroid/2.5.12"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    # Subscription content is base64 encoded
    # Try decoding; if it fails, treat as plain text
    try:
        decoded = base64.b64decode(raw).decode("utf-8")
    except Exception:
        decoded = raw.decode("utf-8")
    return decoded.strip()


def parse_ss_uri(uri: str) -> dict | None:
    """Parse a single ss:// URI into a node dict."""
    uri = uri.strip()
    if not uri.startswith("ss://"):
        return None

    # Remove the ss:// prefix
    rest = uri[5:]

    # SIP002 format: ss://base64(method:password)@host:port#name
    # Legacy format: ss://base64(method:password@host:port)#name

    # Extract fragment (node name)
    name = ""
    if "#" in rest:
        main_part, name = rest.split("#", 1)
        name = urllib.parse.unquote(name)
    else:
        main_part = rest

    # Try SIP002 format first: base64@host:port
    if "@" in main_part:
        userinfo_b64, hostport = main_part.rsplit("@", 1)
        try:
            userinfo = b64_decode(userinfo_b64)
        except Exception:
            userinfo = userinfo_b64

        if ":" not in userinfo:
            return None
        method, password = userinfo.split(":", 1)

        host, port = hostport.rsplit(":", 1)
        port = int(port)
    else:
        # Legacy format: base64(method:password@host:port)
        try:
            decoded = b64_decode(main_part)
        except Exception:
            return None

        # method:password@host:port
        match = re.match(r"^(.+?):(.+?)@(.+?):(\d+)$", decoded)
        if not match:
            return None
        method, password, host, port = (
            match.group(1),
            match.group(2),
            match.group(3),
            int(match.group(4)),
        )

    return {
        "name": name or f"{host}:{port}",
        "type": "ss",
        "server": host,
        "port": port,
        "cipher": method,
        "password": password,
    }


def parse_vmess_uri(uri: str) -> dict | None:
    """Parse a single vmess:// URI into a node dict."""
    uri = uri.strip()
    if not uri.startswith("vmess://"):
        return None

    b64_content = uri[8:]
    try:
        json_str = b64_decode(b64_content)
        info = json.loads(json_str)
    except Exception:
        return None

    name = info.get("ps", f"{info.get('add')}:{info.get('port')}")
    node = {
        "name": name,
        "type": "vmess",
        "server": info.get("add", ""),
        "port": int(info.get("port", 0)),
        "uuid": info.get("id", ""),
        "alterId": int(info.get("aid", 0)),
        "cipher": info.get("scy", "auto"),
        "network": info.get("net", "tcp"),
        "tls": info.get("tls", "") == "tls",
    }

    # Handle transport options
    net = node["network"]
    if net == "ws":
        path = info.get("path", "/")
        host = info.get("host", "")
        node["ws-opts"] = {}
        if path:
            node["ws-opts"]["path"] = path
        if host:
            node["ws-opts"]["headers"] = {"Host": host}
    elif net == "grpc":
        node["grpc-opts"] = {
            "grpc-service-name": info.get("path", ""),
        }
    elif net == "h2":
        node["h2-opts"] = {
            "path": info.get("path", "/"),
            "host": [info.get("host", "")],
        }

    return node


def parse_subscription(content: str) -> list[dict]:
    """Parse all nodes from decoded subscription content."""
    nodes = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("ss://"):
            node = parse_ss_uri(line)
        elif line.startswith("vmess://"):
            node = parse_vmess_uri(line)
        else:
            node = None
        if node:
            nodes.append(node)
    return nodes


def build_clash_config(nodes: list[dict]) -> dict:
    """Build a Clash config dict from parsed nodes."""
    proxies = []
    proxy_names = []

    for node in nodes:
        if node["type"] == "ss":
            proxy = {
                "name": node["name"],
                "type": "ss",
                "server": node["server"],
                "port": node["port"],
                "cipher": node["cipher"],
                "password": node["password"],
            }
        elif node["type"] == "vmess":
            proxy = {
                "name": node["name"],
                "type": "vmess",
                "server": node["server"],
                "port": node["port"],
                "uuid": node["uuid"],
                "alterId": node["alterId"],
                "cipher": node["cipher"],
                "network": node["network"],
                "tls": node["tls"],
            }
            if "ws-opts" in node:
                proxy["ws-opts"] = node["ws-opts"]
            if "grpc-opts" in node:
                proxy["grpc-opts"] = node["grpc-opts"]
            if "h2-opts" in node:
                proxy["h2-opts"] = node["h2-opts"]
        else:
            continue
        proxies.append(proxy)
        proxy_names.append(node["name"])

    config = {
        "mixed-port": 7890,
        "allow-lan": False,
        "mode": "rule",
        "log-level": "info",
        "dns": {
            "enable": True,
            "enhanced-mode": "fake-ip",
            "nameserver": [
                "223.5.5.5",
                "119.29.29.29",
            ],
            "fallback": [
                "8.8.8.8",
                "1.1.1.1",
            ],
        },
        "proxies": proxies,
    }

    if proxy_names:
        config["proxy-groups"] = [
            {
                "name": "Proxy",
                "type": "select",
                "proxies": ["auto"] + proxy_names,
            },
            {
                "name": "auto",
                "type": "url-test",
                "proxies": proxy_names,
                "url": "http://www.gstatic.com/generate_204",
                "interval": 300,
            },
        ]
        config["rules"] = [
            "DOMAIN-SUFFIX,google.com,Proxy",
            "DOMAIN-SUFFIX,github.com,Proxy",
            "DOMAIN-KEYWORD,google,Proxy",
            "GEOIP,CN,DIRECT",
            "MATCH,Proxy",
        ]

    return config


def read_url_from_file(path: str) -> str | None:
    """Read subscription URL from a text file (first non-empty line)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    return line
    except FileNotFoundError:
        return None
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Convert JustMySocks subscription to Clash config"
    )
    parser.add_argument("url", nargs="?", help="Subscription URL")
    parser.add_argument("--url", dest="url_flag", help="Subscription URL")
    parser.add_argument("-f", "--file", dest="url_file", default=None,
                        help="File containing subscription URL (first non-empty line)")
    parser.add_argument("-o", "--output", default=None, help="Output file path (default: output/clash_config.txt)")
    args = parser.parse_args()

    url = args.url or args.url_flag
    if not url and args.url_file:
        url = read_url_from_file(args.url_file)
    if not url:
        parser.error("Subscription URL is required (positional, --url, or --file)")

    print(f"Fetching subscription...")
    content = fetch_subscription(url)
    nodes = parse_subscription(content)

    if not nodes:
        print("No nodes found in subscription.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(nodes)} node(s)")

    config = build_clash_config(nodes)
    output = yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False)

    out_path = args.output
    if not out_path:
        os.makedirs("output", exist_ok=True)
        out_path = os.path.join("output", "clash_config.txt")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"Clash config written to {out_path}")


if __name__ == "__main__":
    main()
