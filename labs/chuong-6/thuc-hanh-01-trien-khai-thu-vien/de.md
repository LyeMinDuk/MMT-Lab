# Chương 6 - Thực hành 01: Triển khai hệ thống cho Trung tâm Thông tin - Thư viện

Nguồn: slide "Chương 6 - Thực hành 01". Bài nộp: `Chương 6 - Thực hành 01.zip` gồm file `.pkt` và file `.pdf` với 3 bảng (vị trí và chức năng, kết nối, địa chỉ IP).

> **Lưu ý về dữ liệu.**
> - Đây là bài **thiết kế**: tự chia mạng và tự đặt địa chỉ, nên bộ chấm kiểm tra *quan hệ* (kích thước mạng con, dải địa chỉ, không chồng lấn, dịch vụ) chứ không so địa chỉ cố định.
> - Tên thiết bị trong slide có dấu cách và dấu gạch lạ (`SW- UTC Lib -A7`, `UTC Lib – S2`). `checks.json` dùng `R-UTC Lib`, `SW-UTC Lib-A8`, `SW-UTC Lib-A7`, `SW-UTC Lib-A6`, `UTC Lib - S1`, `UTC Lib - S2`; sửa lại nếu bạn đặt tên khác.
> - Slide đặt tên pool là `UTC Lib-DHCPv4-pool` có dấu cách, nhưng tên pool trong IOS là một từ, nên bộ chấm không bắt buộc tên pool.

## Yêu cầu
- Nối các tòa A6, A7, A8, hỗ trợ IPv4 và IPv6; dịch vụ DNS, Web, Mail, DHCP; domain `lib.utc.edu.vn`.
- Hai khối: giảng viên (GV: 40 người) và nghiên cứu sinh (NCS: 150 người), mỗi người một thiết bị cấp địa chỉ động.
- Ba LAN: máy chủ (tối đa 12 máy), laptop GV, máy tính NCS.
- Được cấp: IPv4 `69.251.30.0/23`, IPv6 `2018:2809::/48`; 1 router 2811 (có NM-2FE2W), 3 switch 2960, 2 server, PC (NCS) và laptop (GV).

## Bước 1 - Lập kế hoạch và dựng thiết bị
Xác định bảng vị trí - chức năng, bảng kết nối, bảng địa chỉ IP và topology; dựng sáu thiết bị: `R-UTC Lib`, `SW-UTC Lib-A8`, `SW-UTC Lib-A7`, `SW-UTC Lib-A6`, `UTC Lib - S1` (DNS, DHCP cho NCS), `UTC Lib - S2` (Web, Mail). Bước chuẩn bị hạ tầng và cài đặt phần cứng không làm được trong lab.

## Bước 2 - Cấu hình thiết bị mạng
- **Chia mạng** (tự tính): chọn prefix nhỏ nhất đủ chỗ cho GV (40), NCS (150), máy chủ (12), cộng cổng router; IPv6 mỗi LAN một `/64` trong `2018:2809::/48`.
- **Switch**: đặt tên, mật khẩu đặc quyền; A8 có ba VLAN (`3 UTC-SER`, `5 UTC-GV`, `7 UTC-NCS`), A7 và A6 có hai VLAN (GV, NCS); nối trunk giữa các switch, access cho thiết bị. Kết nối 1 PC và 1 laptop (tượng trưng) ở mỗi nơi.
- **Router**: đặt tên, mật khẩu; địa chỉ các giao diện (v4 và v6); DHCPv4 và DHCPv6 cho mạng GV (dns-server là IPv4 của `UTC Lib - S1`, DHCPv6 theo mẫu slide).

## Bước 3 - Cấu hình máy chủ và kiểm thử
- **S1**: DNS cho `lib.utc.edu.vn` (SOA: Min TTL 86400, Retry 3600, Refresh 10800, Expiry 1209600; NS `NS.LIB.UTC.EDU.VN`; A và AAAA cho NS, WWW, MAIL); DHCP cho NCS (pool `serverPool`, tối đa 150 người dùng; `serverPool-v6`).
- **S2**: Web `lib-utc.html` ("Welcome to UTC Library") qua HTTP và HTTPS; Mail với bốn tài khoản `gv-a6/pg6`, `gv-a7/pg7`, `ncs-a6/pn6`, `ncs-a7/pn7`.
- Kiểm thử bằng ping, nslookup, trình duyệt và email client; hoàn thiện ba bảng tài liệu.

## Chấm tự động
```
python tools/check.py bai.pkt --lab labs/chuong-6/thuc-hanh-01-trien-khai-thu-vien --step 3
```
Lưu một file `.pkt` sau mỗi bước. Bộ chấm không đọc được client (PC, laptop) vì slide không đặt tên, và DNS/mail chấm theo chuỗi như chương 5.
