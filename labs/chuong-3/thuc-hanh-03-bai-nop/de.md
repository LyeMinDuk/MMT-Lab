# Chương 3 - Thực hành 03: Bài nộp cuối chương

Nguồn: file đề "Bài nộp cuối chương" chương 3. Lưu file `Hovaten_MSSV.pkt`.

## Kết nối
- R-HN: Fa0/0 nối NET1, Se0/0/0 nối R-DN.
- R-DN: Fa0/0 nối NET2, Se0/0/0 nối R-HN, Se0/0/1 nối R-HCM.
- R-HCM: Fa0/0 nối NET3, Se0/0/1 nối R-DN.

**Slide ghi lệch:** phần mô tả kết nối viết R-HCM nối với R-HN qua Se0/0/1, nhưng bảng địa chỉ cho Se0/0/1 của R-HCM (192.168.20.1/30) cùng mạng với Se0/0/1 của R-DN (192.168.20.2/30). Nên hiểu R-HCM nối với R-DN, đúng như dòng mô tả R-DN. Bộ chấm làm theo cách hiểu này. Ngoài ra bảng NETWORK ghi NET2 là `127.16.0.0/16`, rõ ràng là gõ nhầm của `172.16.0.0/16`.

## Địa chỉ
| Router | Cổng | IPv4 | IPv6 |
|---|---|---|---|
| R-HN | Fa0/0 | 172.15.0.1/16 | 2001:DB8:ACAD:1::1/64 |
| R-HN | Se0/0/0 | 192.168.10.1/30 | 2001:DB8:ACAD:4::1/64 |
| R-DN | Fa0/0 | 172.16.0.1/16 | 2001:DB8:ACAD:2::1/64 |
| R-DN | Se0/0/0 | 192.168.10.2/30 | 2001:DB8:ACAD:4::2/64 |
| R-DN | Se0/0/1 | 192.168.20.2/30 | 2001:DB8:ACAD:5::2/64 |
| R-HCM | Fa0/0 | 172.17.0.1/16 | 2001:DB8:ACAD:3::1/64 |
| R-HCM | Se0/0/1 | 192.168.20.1/30 | 2001:DB8:ACAD:5::1/64 |

Thiết bị đầu cuối: tự đặt IP trong các mạng NET1, NET2, NET3.

Thêm cổng serial: mở router > tab Physical > tắt nguồn > kéo module `WIC-2T` vào khe > bật nguồn.

## Các bước (khớp `--step`)
1. Dựng topology, đặt địa chỉ IPv4/IPv6 cho mọi cổng router, bật cổng, bật `ipv6 unicast-routing`.
2. Cấu hình định tuyến tĩnh hoặc mặc định trên cả ba router sao cho mọi mạng thấy nhau, cả IPv4 và IPv6. Ping giữa các thiết bị ở các mạng khác nhau (kiểm tra cả v4 và v6).

## Chấm tự động
```
python tools/check.py bai.pkt --lab labs/chuong-3/thuc-hanh-03-bai-nop --step 1
python tools/check.py bai.pkt --lab labs/chuong-3/thuc-hanh-03-bai-nop --step 2
```
Bước 2 kiểm tra đường đi từ từng router tới địa chỉ cổng của các router còn lại (v4 và v6), nên tĩnh hay mặc định đều được. Tên thiết bị phải là `R-HN`, `R-DN`, `R-HCM`.
