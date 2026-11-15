# Chương 3 - Thực hành 02: Mạng kết nối, định tuyến tĩnh và mặc định

Nguồn: slide "Chương 3 - Thực hành 02" (Router 2811).

> **Lưu ý về dữ liệu.** Bản slide dạng chữ không chứa hình topology, nên các thông tin chỉ có trong hình (địa chỉ máy trạm, mask của đường nối giữa hai router, cổng nào nối đâu) **chưa có ở đây**. Phần nào suy ra được từ chỗ khác của slide thì có ghi nguồn. Tên router trong bài tập 01 slide không nêu, `checks.json` giả định là `R-UTC`; sửa lại nếu bạn đặt tên khác.

## Bước 1 - Bài tập 01: Mạng kết nối
Một router, hai LAN:

| LAN | IPv4 | IPv6 | Cổng router |
|---|---|---|---|
| LAN 1 | 99.100.31.0/24 | A1B3:4E1C::/64 | Fa0/0: 99.100.31.1 / `A1B3:4E1C::1` |
| LAN 2 | 32.154.23.128/25 | 2DCF:A001::/64 | Fa0/1: 32.154.23.129 / `2DCF:A001::1` |

Việc cần làm: đặt IP cho PC và Server (như hình slide), đặt IP cho hai cổng router, bật cổng, rồi xem `show ip route`, `show ipv6 route`, `show ip cef`, `show ipv6 cef`, `show protocols`. Ping giữa hai LAN.

Gợi ý hướng kiểm tra: `show ipv6 cef` chỉ chạy khi đã bật định tuyến IPv6; hai LAN chỉ ping được nhau khi có `ipv6 unicast-routing` cho IPv6.

## Bước 2 - Bài tập 02: Hai router R-UTC và R-UTC2
Từ các lệnh trong slide suy ra:

| Mạng | IPv4 | IPv6 | Phía |
|---|---|---|---|
| NET1 | 55.14.92.0/24 | 24BB:7A1::/64 | sau R-UTC |
| NET2 | 74.54.33.128/25 | 2DCF:4A6::/64 | sau R-UTC2 |
| Đường nối hai router | R-UTC 212.96.8.253, R-UTC2 212.96.8.254 (mask: xem hình) | R-UTC `2FF2:B52::1`, R-UTC2 `2FF2:B52::2` | |

Các suy luận từ slide khác (chương 5 thực hành 02, bài DHCP qua relay dùng lại topology này): R-UTC2 Fa0/0 là `74.54.33.129/25` (gateway của NET2); server N1 ở NET1 là `55.14.92.5/24`, `24BB:7A1::5/64`.

Làm theo ba cách (slide yêu cầu tự làm cách 1 và 2, còn cách 3 có sẵn lệnh):
1. Chỉ định tuyến tĩnh trên cả hai router.
2. Chỉ định tuyến mặc định trên cả hai router.
3. Tĩnh trên R-UTC, mặc định trên R-UTC2.

Mỗi tuyến cần cả IPv4 và IPv6, trỏ next-hop về cổng router đầu kia. Rồi chạy `show protocols` trên cả hai router và ping từ máy ở NET1 tới `74.54.33.131` và `2DCF:4A6::3` (các máy ở NET2).

## Chấm tự động
```
python tools/check.py bai.pkt --lab labs/chuong-3/thuc-hanh-02-dinh-tuyen --step 1
python tools/check.py bai.pkt --lab labs/chuong-3/thuc-hanh-02-dinh-tuyen --step 2
```
- Bước 1 chấm bài tập 01, bước 2 chấm bài tập 02.
- Bước 2 mô phỏng đường đi theo bảng định tuyến (kết nối, tĩnh, mặc định), nên **cả ba cách đều được chấp nhận**; nó báo router nào thiếu tuyến, next-hop sai hay chưa bật IPv6 routing.
- Bộ chấm chỉ xét cấu hình router, không xét PC và không thay cho ping thật.
