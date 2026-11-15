"""Test nhanh cho tools/check.py (chạy: python tests/test_check.py hoặc pytest).

XML ở đây dựng tay theo đúng cấu trúc đã quan sát trong file .pkt bản 8.1.1.0022
(DEVICE/ENGINE/NAME/SAVE_REF_ID/RUNNINGCONFIG/VLANS/MODULE/PORT, LINK/CABLE).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import check  # noqa: E402


def engine(name, ref, model="2960-24TT", config=(), vlans=(), ports=()):
    cfg = "".join(f"<LINE>{ln}</LINE>" for ln in config)
    vl = "".join(f'<VLAN rspan="0" name="{n}" number="{i}" />' for i, n in vlans)
    pt = ""
    for ip, mask, v6 in ports:
        a = "".join(f"<IPV6_ADDRESS><ADDRESS>{x}</ADDRESS><PREFIX>{p}</PREFIX></IPV6_ADDRESS>" for x, p in v6)
        pt += f"<PORT><IP>{ip}</IP><SUBNET>{mask}</SUBNET><IPV6_ADDRESSES>{a}</IPV6_ADDRESSES></PORT>"
    return (f'<DEVICE><ENGINE><TYPE model="{model}">x</TYPE><NAME>{name}</NAME>'
            f"<SAVE_REF_ID>{ref}</SAVE_REF_ID><MODULE>{pt}</MODULE>"
            f"<RUNNINGCONFIG>{cfg}</RUNNINGCONFIG><VLANS>{vl}</VLANS></ENGINE></DEVICE>")


def link(a, pa, b, pb):
    return (f"<LINK><CABLE><FROM>{a}</FROM><PORT>{pa}</PORT><TO>{b}</TO><PORT>{pb}</PORT></CABLE></LINK>")


XML = ("<PACKETTRACER5><VERSION>8.1.1.0022</VERSION><NETWORK><DEVICES>"
       + engine("SW-1", "r1", config=[
           "hostname SW-1", "enable secret 5 $1$abc", "!",
           "interface FastEthernet0/1", " switchport access vlan 2", " switchport mode access", "!",
           "interface FastEthernet0/2", "!",
           "interface FastEthernet0/24", " shutdown", "!",
           "interface GigabitEthernet0/1", " switchport trunk allowed vlan 3,4", " switchport mode trunk", "!"],
           vlans=[(1, "default"), (2, "DT"), (3, "KH")])
       + engine("PC-A", "r2", "PC-PT", ports=[("115.200.15.10", "255.255.255.0", [("2001:DB8::1", 64)])])
       + "</DEVICES><LINKS>" + link("r2", "FastEthernet0", "r1", "FastEthernet0/1") + "</LINKS></NETWORK></PACKETTRACER5>")
M = check.build_model(XML.encode())


def run(kind, **kw):
    dev = M["devices"].get(kw.get("device"), {})
    return check.CHECKS[kind](M, dev, kw)[0]


def test_helpers():
    assert check.norm_port("FastEthernet0/1") == "Fa0/1"
    assert check.norm_port("Gig0/1") == "Gi0/1"
    assert check.norm_port("GigabitEthernet0/1") == "Gi0/1"
    assert check.expand_ports("Fa0/6-10") == [f"Fa0/{i}" for i in range(6, 11)]
    assert check.fmt_vlans({2, 3, 4, 7}) == "2-4,7"


def test_switch():
    assert run("hostname", device="SW-1", name="SW-1")
    assert run("enable_secret", device="SW-1")
    assert run("vlan", device="SW-1", id=2, name="DT")
    assert not run("vlan", device="SW-1", id=2, name="XX")      # sai tên
    assert not run("vlan", device="SW-1", id=4, name="TC")      # chưa có
    assert run("no_vlan", device="SW-1", id=4)
    assert run("port_vlan", device="SW-1", ports="Fa0/1", vlan=2)
    assert not run("port_vlan", device="SW-1", ports="Fa0/1-2", vlan=2)   # Fa0/2 còn mặc định
    assert run("port_vlan", device="SW-1", ports="Fa0/2", vlan=1)
    assert run("port_mode", device="SW-1", port="Gi0/1", mode="trunk")
    assert run("trunk_allowed", device="SW-1", port="Gi0/1", vlans=[3, 4])
    assert not run("trunk_allowed", device="SW-1", port="Gi0/1", vlans=[2, 3, 4])
    assert run("port_shutdown", device="SW-1", port="Fa0/24", shutdown=True)
    assert not run("port_default", device="SW-1", port="Fa0/24")
    assert run("port_default", device="SW-1", port="Fa0/2")


def test_pc_and_links():
    assert not run("ip", device="PC-A", ipv4="115.100.15.10")   # nhầm octet 2
    assert run("ip", device="PC-A", ipv4="115.200.15.10")
    assert run("ipv6", device="PC-A", ipv6="2001:db8:0:0:0:0:0:1")  # so sánh sau khi chuẩn hoá
    assert run("ipv6", device="PC-A", ipv6=["2001:DB8::2", "2001:DB8::1"])
    assert not run("ipv6", device="PC-A", ipv6="2001:DB8::123")
    assert run("link", a="PC-A:Fa0", b="SW-1:Fa0/1")
    assert run("link", a="SW-1:Fa0/1", b="PC-A:Fa0")             # đảo chiều vẫn đúng
    assert run("no_link", a="SW-1:Fa0/24", b="SW-2:Fa0/24")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
