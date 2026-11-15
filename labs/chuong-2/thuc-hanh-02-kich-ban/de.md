# Chương 2 - Thực hành 02: Cấu hình theo kịch bản (10 bước)

Nguồn: slide "Chương 2 - Thực hành 02 - Cấu hình theo kịch bản". Hai switch 2960: **SW-UTC-A3** (toà A3) và **SW-UTC-A5** (toà A5). Mật khẩu enable cả hai: `UTC@123`.

## Bảng kết nối
| Thiết bị | Cổng | Tới |
|---|---|---|
| L1-PC1, L1-PC2 | Fa0 | Fa0/1, Fa0/2 (SW-UTC-A3) |
| L2-PC1, L2-PC2 | Fa0 | Fa0/3, Fa0/4 (SW-UTC-A3) |
| L2-PC3, L2-PC4 | Fa0 | Fa0/1, Fa0/2 (SW-UTC-A5) |
| L1-PC3, L1-PC4 | Fa0 | Fa0/4, Fa0/5 (SW-UTC-A5) |
| L3-PC1 (sau này L1-PC5) | Fa0 | Fa0/3 (SW-UTC-A5) |
| L3-PC2 (sau này L2-PC5) | Fa0 | Fa0/5 (SW-UTC-A3) |
| SW-UTC-A3 / SW-UTC-A5 | Fa0/24, Gi0/1 | Fa0/24, Gi0/1 (switch kia) |

## Địa chỉ (IPv4 /24, IPv6 /64)
| LAN | IPv4 | IPv6 | Máy (hậu tố host) |
|---|---|---|---|
| LAN 1 (VLAN 1) | 97.81.46.0 | 200E:2C0A:F1C6:1231:: | PC1 .2, PC2 .4, PC3 .6, PC4 .8, PC5 .7 |
| LAN 2 (VLAN 2) | 117.108.45.0 | 2013:B002:1C04:EFA:: | PC1 .11, PC2 .13, PC3 .15, PC4 .17, PC5 .16 |
| LAN 3 (VLAN 3, Research) | 214.8.73.0 | 3ABC:FFFF:6666:5D7F:: | PC1 .23, PC2 .24 |

Với IPv6 lấy hậu tố host cùng số (ví dụ L2-PC1: `2013:B002:1C04:EFA::11`).

**Lưu ý: slide tự mâu thuẫn.** Bảng quy hoạch ghi LAN 2 IPv6 là `2013:B002:1C04:EFA::/64`, nhưng các hình ở bước 3 đến 5 ghi `DEFA`. Bộ chấm chấp nhận cả hai; nên hỏi giảng viên và giữ một giá trị thống nhất.

## 10 bước (khớp `--step`)
1. Dựng A3: L1-PC1, L1-PC2 vào VLAN 1. Đặt tên switch `SW-UTC-A3` và enable secret. Đặt IP, ghi lại MAC. Xem bảng MAC.
2. Ping giữa các PC, xem bảng MAC.
3. Tạo VLAN 2 tên `Guest` trên A3. Nối L2-PC1, L2-PC2 vào Fa0/3, Fa0/4, gán VLAN 2.
4. Dựng A5: tên `SW-UTC-A5`, enable secret, VLAN 2 `Guest`. Gán Fa0/24 (access) cả hai switch vào VLAN 2 rồi nối cáp.
5. Nối L2-PC3, L2-PC4 vào Fa0/1, Fa0/2 của A5, gán VLAN 2. Ping cả VLAN 2.
6. Tạo VLAN 3 `Research` trên cả hai switch. Trunk Gi0/1 (có `description`), chỉ cho VLAN 3.
7. L3-PC1 nối Fa0/3 (A5), L3-PC2 nối Fa0/5 (A3), cùng VLAN 3. Ping giữa hai máy.
8. Cho VLAN 1 qua trunk (trunk cho VLAN 1,3). Thêm L1-PC3, L1-PC4 vào A5 (Fa0/4, Fa0/5, VLAN 1).
9. Đổi tên VLAN 2 từ `Guest` thành `Outs` ở cả hai switch. Cho VLAN 2 qua trunk (1,2,3). Tắt Fa0/24 và bỏ cáp access.
10. Bỏ LAN 3: VLAN 3 không qua trunk (trunk còn 1,2), xóa VLAN 3. L3-PC1 thành L1-PC5 (VLAN 1), L3-PC2 thành L2-PC5 (VLAN 2). Đưa Fa0/24 về mặc định.

## Chấm tự động
```
python tools/check.py bai.pkt --lab labs/chuong-2/thuc-hanh-02-kich-ban --step 6
```
Lưu một file `.pkt` sau mỗi bước để chấm đúng `--step`. Bộ chấm đọc cấu hình; ping và bảng MAC vẫn tự kiểm tra trong Packet Tracer.
