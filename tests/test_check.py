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


# ---------- định tuyến: 3 router nối chuỗi HN - DN - HCM ----------
def iface(name, v4=None, v6=None, down=False):
    out = [f"interface {name}"]
    if v4:
        out.append(f" ip address {v4[0]} {v4[1]}")
    if v6:
        out.append(f" ipv6 address {v6}")
    if down:
        out.append(" shutdown")
    return out + ["!"]


def routers(hn_routes=None, dn_routes=None, hcm_routes=None, v6_routing=True, hcm_down=False):
    m16, m30 = "255.255.0.0", "255.255.255.252"
    base = ["ipv6 unicast-routing"] if v6_routing else []
    hn = (base + (hn_routes or [])
          + iface("FastEthernet0/0", ("172.15.0.1", m16), "2001:DB8:ACAD:1::1/64")
          + iface("Serial0/0/0", ("192.168.10.1", m30), "2001:DB8:ACAD:4::1/64"))
    dn = (base + (dn_routes or [])
          + iface("FastEthernet0/0", ("172.16.0.1", m16), "2001:DB8:ACAD:2::1/64")
          + iface("Serial0/0/0", ("192.168.10.2", m30), "2001:DB8:ACAD:4::2/64")
          + iface("Serial0/0/1", ("192.168.20.2", m30), "2001:DB8:ACAD:5::2/64"))
    hcm = (base + (hcm_routes or [])
           + iface("FastEthernet0/0", ("172.17.0.1", m16), "2001:DB8:ACAD:3::1/64", down=hcm_down)
           + iface("Serial0/0/1", ("192.168.20.1", m30), "2001:DB8:ACAD:5::1/64"))
    xml = ("<PACKETTRACER5><VERSION>8.1.1.0022</VERSION><NETWORK><DEVICES>"
           + engine("R-HN", "a", "2811", hn) + engine("R-DN", "b", "2811", dn)
           + engine("R-HCM", "c", "2811", hcm) + "</DEVICES><LINKS></LINKS></NETWORK></PACKETTRACER5>")
    return check.build_model(xml.encode())


def reach(model, dev, to):
    return check.trace(model, dev, to)[0]


GOOD = dict(
    hn_routes=["ip route 0.0.0.0 0.0.0.0 192.168.10.2", "ipv6 route ::/0 2001:DB8:ACAD:4::2"],
    hcm_routes=["ip route 0.0.0.0 0.0.0.0 192.168.20.2", "ipv6 route ::/0 2001:DB8:ACAD:5::2"],
    dn_routes=["ip route 172.15.0.0 255.255.0.0 192.168.10.1", "ip route 172.17.0.0 255.255.0.0 192.168.20.1",
               "ipv6 route 2001:DB8:ACAD:1::/64 2001:DB8:ACAD:4::1", "ipv6 route 2001:DB8:ACAD:3::/64 2001:DB8:ACAD:5::1"])


def test_routing_ok():
    n = routers(**GOOD)
    for src, dst in (("R-HN", "172.17.0.1"), ("R-HCM", "172.15.0.1"), ("R-DN", "172.15.0.1"),
                     ("R-HN", "2001:DB8:ACAD:3::1"), ("R-HCM", "2001:DB8:ACAD:1::1")):
        assert reach(n, src, dst), (src, dst, check.trace(n, src, dst))


def test_routing_faults():
    no_route = dict(GOOD, dn_routes=GOOD["dn_routes"][:1] + GOOD["dn_routes"][2:])  # DN thiếu tuyến tới NET3 (v4)
    n = routers(**no_route)
    assert not reach(n, "R-HN", "172.17.0.1") and "R-DN" in check.trace(n, "R-HN", "172.17.0.1")[1]
    assert reach(n, "R-HN", "2001:DB8:ACAD:3::1")                       # v6 vẫn ổn
    assert not reach(routers(v6_routing=False, **GOOD), "R-HN", "2001:DB8:ACAD:3::1")
    assert reach(routers(v6_routing=False, **GOOD), "R-HN", "172.17.0.1")  # v4 không cần
    assert not reach(routers(hcm_down=True, **GOOD), "R-HN", "172.17.0.1")
    wrong = dict(GOOD, hn_routes=["ip route 0.0.0.0 0.0.0.0 192.168.10.9"])
    assert not reach(routers(**wrong), "R-HN", "172.17.0.1")             # next-hop sai
    loop = dict(GOOD, dn_routes=["ip route 172.17.0.0 255.255.0.0 192.168.10.1"])
    assert not reach(routers(**loop), "R-HN", "172.17.0.1")              # DN trả ngược về HN


def test_port_checks():
    n = routers(**GOOD)
    d = n["devices"]["R-HN"]
    assert check.CHECKS["port_ip"](n, d, dict(device="R-HN", port="Fa0/0", ipv4="172.15.0.1", mask="255.255.0.0", ipv6="2001:db8:acad:1::1"))[0]
    assert not check.CHECKS["port_ip"](n, d, dict(device="R-HN", port="Se0/0/0", ipv4="192.168.10.2", mask="255.255.255.252"))[0]
    assert check.CHECKS["ipv6_routing"](n, d, {"device": "R-HN"})[0]
    assert check.CHECKS["port_up"](n, d, dict(device="R-HN", port="Se0/0/0"))[0]
    assert not check.CHECKS["port_up"](routers(hcm_down=True, **GOOD), routers(hcm_down=True, **GOOD)["devices"]["R-HCM"], dict(device="R-HCM", port="Fa0/0"))[0]


# ---------- router không dây, gateway, device, ip_in ----------
WIRELESS = (
    "<PACKETTRACER5><VERSION>8.1.1.0022</VERSION><NETWORK><DEVICES>"
    '<DEVICE><ENGINE><TYPE model="Linksys-WRT300N">WirelessRouter</TYPE><NAME>WR0</NAME><SAVE_REF_ID>w</SAVE_REF_ID>'
    "<MODULE><PORT><IP></IP><SUBNET></SUBNET></PORT></MODULE>"
    "<LAN_IP_ADDRESS>211.13.45.10</LAN_IP_ADDRESS><LAN_SUBNET_MASK>255.255.255.0</LAN_SUBNET_MASK>"
    "<INTERNET_IP_ADDRESS>0.0.0.0</INTERNET_IP_ADDRESS></ENGINE></DEVICE>"
    '<DEVICE><ENGINE><TYPE model="PC-PT">Pc</TYPE><NAME>PC1</NAME><SAVE_REF_ID>p</SAVE_REF_ID>'
    "<GATEWAY>151.45.78.1</GATEWAY><MODULE><PORT><IP>151.45.78.8</IP><SUBNET>255.255.0.0</SUBNET>"
    "<IPV6_PORT_GATEWAY>2001:DB8:3C4D:1::1</IPV6_PORT_GATEWAY></PORT></MODULE></ENGINE></DEVICE>"
    '<DEVICE><ENGINE><TYPE model="TabletPC-PT">TabletPC</TYPE><NAME>Tab</NAME><SAVE_REF_ID>t</SAVE_REF_ID>'
    "<GATEWAY>192.168.0.1</GATEWAY><MODULE><PORT><IP>169.254.190.141</IP><SUBNET>255.255.0.0</SUBNET></PORT></MODULE></ENGINE></DEVICE>"
    "</DEVICES><LINKS></LINKS></NETWORK></PACKETTRACER5>")
W = check.build_model(WIRELESS.encode())


def runw(kind, **kw):
    return check.CHECKS[kind](W, W["devices"][kw["device"]], kw)[0]


def test_wireless_and_endpoints():
    assert runw("ip", device="WR0", ipv4="211.13.45.10", mask="255.255.255.0")   # IP LAN ở thẻ riêng
    assert runw("device", device="WR0", model="Linksys-WRT300N")
    assert not runw("device", device="PC1", model="Laptop-PT")
    assert runw("gateway", device="PC1", ipv4="151.45.78.1", ipv6="2001:db8:3c4d:1:0:0:0:1")
    assert not runw("gateway", device="PC1", ipv4="151.45.78.254")
    assert not runw("gateway", device="PC1", ipv6="2001:DB8:3C4D:1::2")
    assert runw("ip_in", device="WR0", network="211.13.45.0/24")
    assert not runw("ip_in", device="Tab", network="211.13.45.0/24")             # APIPA 169.254.x.x


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
