# Chương 5 - Thực hành 01: Dịch vụ DNS, WEB, MAIL

Nguồn: slide "Chương 5 - Thực hành 01".

> **Lưu ý về dữ liệu.** Sơ đồ mạng của bài là hình, không có trong bản slide chữ. Tên máy chủ DNS (`L2 - DNSv4`, `L2 - DNSv6`) là giả định của mình; `L2 - UTC WEB`, `L2 - UTC MAIL` và `L1-PC0`, `L1-PC1`, `L1-PC2` lấy từ slide. Nếu bạn đặt tên khác, sửa `checks.json`. Bộ chấm kiểm tra **cấu hình dịch vụ** bằng cách tìm chuỗi trong dữ liệu của máy chủ (chưa phân biệt loại bản ghi), nên ping, nslookup, mở web và gửi thư vẫn phải tự thử.

## Bước 1 - Bài tập 01: Dịch vụ DNS
- Dựng topology, cấu hình R-UTC.
- **DNSv4**: `113.20.118.6/24`, miền `UTC.EDU.VN`, máy chủ `NS-V4.UTC.EDU.VN`, bản ghi SOA, NS và A (`NS-V4.UTC.EDU.VN → 113.20.118.6`).
- **DNSv6**: `2ABC:A4A9::7/64`, cùng miền, máy chủ `NS-V6.UTC.EDU.VN`, bản ghi SOA, NS và AAAA (`NS-V6.UTC.EDU.VN → 2ABC:A4A9::7`).
- Đặt tham số DNS Server trên các PC; `nslookup` từ L1-PC0, PC1 tới DNSv4 và từ L1-PC1, PC2 tới DNSv6.

## Bước 2 - Bài tập 02: Dịch vụ WEB
- Máy chủ web **L2 - UTC WEB**: `113.20.118.5/24`, `2ABC:A4A9::5/64`; bật HTTP và HTTPS, tạo trang `utc.html`.
- Từ PC LAN1 truy cập bằng IP (v4, v6, http và https), rồi thử `http://www.utc.edu.vn/utc.html` và giải thích kết quả.
- Khai DNS: A `WWW.UTC.EDU.VN → 113.20.118.5` trên DNSv4, AAAA `WWW.UTC.EDU.VN → 2ABC:A4A9::5` trên DNSv6; truy cập lại bằng tên.

## Bước 3 - Bài tập 03: Dịch vụ MAIL
- DNS cho mail: A `MAIL.UTC.EDU.VN → 113.20.118.8`, AAAA `MAIL.UTC.EDU.VN → 2ABC:A4A9::8`.
- Máy chủ **L2 - UTC MAIL**: `113.20.118.8/24`, `2ABC:A4A9::8/64`, domain `utc.edu.vn`, tạo tài khoản `aaa/123`, `bbb/234`, `ccc/345`.
- Cấu hình email client: aaa trên L1-PC0, bbb trên L1-PC1, ccc trên L1-PC2.
- bbb gửi thư cho aaa và ccc; aaa và ccc kiểm tra hộp thư, trả lời; bbb xem phản hồi.

## Chấm tự động
```
python tools/check.py bai.pkt --lab labs/chuong-5/thuc-hanh-01-dns-web-mail --step 2
```
Lưu một file `.pkt` sau mỗi bước. Bước sau chấm lại cả cấu hình của các bước trước.
