# Chương 5 - Thực hành 02: Cấu hình DHCP

Nguồn: slide "Chương 5 - Thực hành 02". Ba bài là ba mạng riêng, nên mỗi bài lưu một file `.pkt` riêng và `--step N` chỉ chấm đúng bài đó.

> **Lưu ý về dữ liệu.** Sơ đồ là hình, không có trong slide chữ. Bài 2 slide cho IPv6 của UTC-Server-01 chỉ trong hình, nên `checks.json` không kiểm tra IPv6 của máy chủ này. Tên `N2-PC1` lấy từ lệnh ping trong bài 3.

## Bước 1 - Bài tập 01: Router cung cấp DHCP
Mạng LAN 1: `19.16.20.0/24`, `2001:DB8:1234:42::/64`. R-UTC Fa0/1 là `19.16.20.1/24`, `2001:DB8:1234:42::1/64`.
- DHCPv4 pool `UTC-DHCPv4-pool`: loại trừ `19.16.20.1 - 19.16.20.30`, network `19.16.20.0/24`, default-router `19.16.20.1`, dns-server `194.0.1.18`.
- DHCPv6 pool `UTC-DHCPv6-pool`: dns-server `2001:678:4::12`; trên Fa0/1 đặt `ipv6 nd other-config-flag` và `ipv6 dhcp server UTC-DHCPv6-pool`.
- L1-PC1, L1-PC2 nhận IPv4/IPv6 từ DHCP; ping v4/v6 giữa hai máy và tới gateway.

## Bước 2 - Bài tập 02: Máy chủ cung cấp DHCP
Mạng LAN 1: `101.12.31.0/24`, `20AB:6D:1:E2::/64`. R-UTC Fa0/1 là `101.12.31.1/24`, `20AB:6D:1:E2::1/64`; UTC-Server-01 là `101.12.31.3/24`.
- DHCPv4 pool `serverPool` trên UTC-Server-01: gateway `101.12.31.1`, DNS `203.119.73.105`, start `101.12.31.40`, mask `255.255.255.0`, tối đa 20 người dùng.
- DHCPv6 pool `serverPool-v6`: DNS `2001:DC8:1:2::105`, prefix `20AB:6D:1:E2::/64`.
- L1-PC1, L1-PC2 nhận địa chỉ từ máy chủ; ping từ hai máy tới gateway và DHCP server.

## Bước 3 - Bài tập 03: DHCP qua Router Relay
Topology tham khảo chương 3 thực hành 02 (bài tập 02). Mạng N1 `55.14.92.0/24` phía R-UTC, mạng N2 `74.54.33.128/25` phía R-UTC2.
- N1-SerUTC-1: `55.14.92.5/24`, `24BB:7A1::5/64`; DHCPv4 pool `serverPool`: gateway `74.54.33.129`, DNS `202.47.142.105`, start `74.54.33.149`, mask `255.255.255.128`, tối đa 30 người dùng.
- R-UTC2: `ip helper-address 55.14.92.5` trên Fa0/0 (cổng phía N2, `74.54.33.129`).
- Các PC của N2 nhận IPv4 từ máy chủ; ping từ N2-PC1 tới mọi host của N1. Slide lưu ý: Router 2811 (PT 8.1.1) không hỗ trợ DHCPv6 relay.

## Chấm tự động
```
python tools/check.py bai1.pkt --lab labs/chuong-5/thuc-hanh-02-dhcp --step 1
python tools/check.py bai3.pkt --lab labs/chuong-5/thuc-hanh-02-dhcp --step 3
```
Bài 1 chấm cấu hình router đọc từ running-config. Bài 2 và 3 đọc cấu hình DHCP pool của máy chủ; riêng DHCPv6 trên máy chủ chỉ chấm theo chuỗi.
