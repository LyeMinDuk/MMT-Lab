# Chương 1 - Thực hành 02: Bài tập nộp

Nguồn: file đề "Bài tập chương 1" của môn. Lưu file `Hovaten_MSSV.pkt`.

## Bước 1 - Thiết kế mô hình mạng
Dựng các thiết bị và nối cáp:

| Thiết bị | Loại | Cổng | Nối tới |
|---|---|---|---|
| PC0 | PC-PT | Fa0 | Fa0/1 (Switch0) |
| Laptop0 | Laptop-PT | Fa0 | Fa0/2 (Switch0) |
| Server0 | Server-PT | Fa0 | Fa0/3 (Switch0) |
| Switch0 | 2960-24TT | Fa0/4 | Fa0/0 (Router0) |
| Switch1 | 2960-24TT | Fa0/1 | Fa0/1 (Router0) |
| Router0 | 2811 | Fa0/0, Fa0/1 | Fa0/4 (Switch0), Fa0/1 (Switch1) |
| Wireless Router0 | WRT300N | E1 | Fa0/2 (Switch1) |
| Tablet PC0 | TabletPC-PT | không dây | |
| Smartphone0 | Smartphone-PT | không dây | |

Tên thiết bị trong checks.json lấy theo tên mặc định của Packet Tracer (`Tablet PC0`, `Smartphone0`); đề viết `TabletPC0` không có dấu cách, nên nếu bạn đặt tên theo đề thì sửa lại cho khớp.

## Bước 2 - Cấu hình địa chỉ IP các thiết bị
| Thiết bị | IPv4 / mask | Default gateway v4 | IPv6 | Default gateway v6 |
|---|---|---|---|---|
| PC0 | 151.45.78.8 / 255.255.0.0 | 151.45.78.1 | 2001:DB8:3C4D:1::123/64 | 2001:DB8:3C4D:1::1 |
| Laptop0 | 151.45.78.11 / 255.255.0.0 | 151.45.78.1 | | |
| Server0 | 151.45.78.20 / 255.255.0.0 | 151.45.78.1 | 2001:DB8:3C4D:1::321/64 | 2001:DB8:3C4D:1::1 |
| Router0 Fa0/0 | 151.45.78.1 / 255.255.0.0 | | 2001:DB8:3C4D:1::1/64 | |
| Router0 Fa0/1 | 211.13.45.1 / 255.255.255.0 | | | |
| Wireless Router0 | 211.13.45.10 / 255.255.255.0 | | | |

Gợi ý của đề: cấu hình Wireless Router0 (IP phía LAN, DHCP và SSID để máy không dây vào được).

## Bước 3 - Kiểm tra kết nối
Quan sát ping giữa các thiết bị với nhau; yêu cầu ping thành công giữa các thiết bị. Tablet PC0 và Smartphone0 cần kết nối vào router không dây và nhận địa chỉ trong mạng `211.13.45.0/24` thì mới ping được (đây là suy ra từ yêu cầu ping thành công, đề không ghi địa chỉ riêng cho hai máy này).

## Chấm tự động
```
python tools/check.py bai.pkt --lab labs/chuong-1/thuc-hanh-02-bai-nop --step 2
```
Chấm bước 3 sẽ kiểm tra thêm hai máy không dây đã có IP trong `211.13.45.0/24`. Ping thật vẫn phải tự thử trong Packet Tracer.
