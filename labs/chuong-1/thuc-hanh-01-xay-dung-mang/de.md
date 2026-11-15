# Chương 1 - Thực hành 01: Xây dựng mạng, cấu hình IP và ping

Nguồn: slide "Chương 1 - Thực hành" (phần Bài tập).

> **Lưu ý về dữ liệu.** Sơ đồ mạng và "bảng thông số" của bài này là hình, không có trong bản slide dạng chữ. Phần dưới chỉ gồm những gì có chữ. Tên thiết bị `LT0`, `PC0`, `S0`, `R0` lấy từ các bước trong slide; loại thiết bị là giả định hợp lý (laptop, PC, server, router 2811). Sửa `checks.json` nếu bạn đặt tên khác hoặc khi có đủ thông tin từ hình.

## Bước 1 - Xây dựng mô hình
Đưa thiết bị vào workspace (laptop, PC, server, router 2811, switch 2960) và nối cáp theo sơ đồ trong slide. Dùng cáp Straight-Through; Cross-Over chỉ để nối hai router.

## Bước 2 - Cấu hình địa chỉ IP
- **Đầu cuối** (LT0, PC0, S0 và các máy khác): Config > FastEthernet0, chọn Static, điền IPv4/IPv6 theo bảng thông số trong slide. Mọi PC, Laptop, Server cấu hình giống LT0.
- **Router R0**, cổng Fa0/0 (từ slide):
  - IPv4: `132.54.78.1` mask `255.255.255.0`
  - IPv6: `2AB1:1D8C:ABBA::1/64`
  - Cổng Fa0/1 làm tương tự theo bảng thông số (giá trị có trong hình, không có trong bản chữ).
- Nhớ bật cổng (`no shut`).

## Bước 3 - Kiểm tra kết nối
- Trên đầu cuối: Command Prompt, `ping` IPv4 và IPv6 tới các thiết bị khác, xem kết quả.
- Trên R0: CLI, `ping` v4/v6 tới các đầu cuối.

Gợi ý hướng kiểm tra: ping IPv6 giữa hai mạng khác nhau cần router bật `ipv6 unicast-routing`.

## Chấm tự động
```
python tools/check.py bai.pkt --lab labs/chuong-1/thuc-hanh-01-xay-dung-mang --step 2
```
Bộ chấm chỉ kiểm tra thiết bị có mặt (bước 1) và địa chỉ, trạng thái cổng Fa0/0 của R0 (bước 2 trở đi). Các phần còn lại phụ thuộc vào hình slide.
