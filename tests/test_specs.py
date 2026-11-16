"""Kiểm tra mọi checks.json: loại kiểm tra có tồn tại, khoảng bước hợp lệ, thiếu/trùng khóa."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import check  # noqa: E402

NEED = {"vlan": ["device", "id"], "no_vlan": ["device", "id"], "port_vlan": ["device", "ports", "vlan"],
        "port_mode": ["device", "port", "mode"], "trunk_allowed": ["device", "port", "vlans"],
        "port_shutdown": ["device", "port"], "port_default": ["device", "port"], "enable_secret": ["device"],
        "hostname": ["device", "name"], "ip": ["device", "ipv4"], "ipv6": ["device", "ipv6"],
        "link": ["a", "b"], "no_link": ["a", "b"], "port_ip": ["device", "port"], "port_up": ["device", "port"],
        "ipv6_routing": ["device"], "reach": ["device", "dest"],
        "device": ["device"], "gateway": ["device"], "ip_in": ["device", "network"],
        "dhcp_pool": ["device", "name"], "dhcp_excluded": ["device", "start"], "dhcp6_pool": ["device", "name"],
        "port_line": ["device", "port", "line"], "dhcp_server_pool": ["device", "name"],
        "xml_value": ["device", "path", "equals", "label"], "xml_has": ["device", "contains", "label"]}


def test_specs():
    files = sorted(ROOT.glob("labs/**/checks.json"))
    assert files, "không tìm thấy checks.json"
    for f in files:
        spec = json.loads(f.read_text(encoding="utf-8"))
        for c in spec["checks"]:
            assert c["type"] in check.CHECKS, (f, c)
            for k in NEED[c["type"]]:
                assert k in c, (f, c, k)
            assert c.get("from", 1) <= c.get("to", 99), (f, c)
            assert c.get("from", 1) <= spec.get("steps", 99), (f, c)
            assert "to" not in c or c["to"] <= spec.get("steps", 99), (f, c)


if __name__ == "__main__":
    test_specs()
    print("ok test_specs")
