# Cheatsheet: DNS, WEB, MAIL, DHCP (Chương 5 - Thực hành)

Nguồn: slide "Chương 5 - Thực hành 01" (DNS, WEB, MAIL) và "Thực hành 02" (DHCP). Mục "Bổ sung" là kiến thức chung hoặc cách thao tác trong Packet Tracer, tên mục trong giao diện có thể lệch chút giữa các bản.

## 1. DNS trên máy chủ
Máy chủ > tab **Services > DNS**: bật dịch vụ (On), rồi khai bản ghi. Slide dùng hai máy chủ riêng, một cho IPv4 và một cho IPv6, cùng miền `UTC.EDU.VN`:

| Máy chủ | Địa chỉ | Tên máy chủ | Bản ghi A / AAAA |
|---|---|---|---|
| DNSv4 | 113.20.118.6/24 | NS-V4.UTC.EDU.VN | A: NS-V4.UTC.EDU.VN → 113.20.118.6 |
| DNSv6 | 2ABC:A4A9::7/64 | NS-V6.UTC.EDU.VN | AAAA: NS-V6.UTC.EDU.VN → 2ABC:A4A9::7 |

Mỗi máy chủ khai thêm bản ghi **SOA** và **NS** cho miền. Máy trạm phải được đặt tham số **DNS Server** (tab Config hoặc IP Configuration) trỏ tới máy chủ DNS tương ứng.

Kiểm tra: **Desktop > Command Prompt**, `nslookup <tên>` rồi đọc trả lời của máy chủ DNS.

## 2. WEB
Máy chủ > **Services > HTTP**: bật **HTTP** và **HTTPS**, tạo một trang HTML đơn giản (slide dùng `utc.html`). Truy cập thử bằng địa chỉ IP, ví dụ:
```
http://113.20.118.5/utc.html          https://113.20.118.5/utc.html
http://[IPv6]/utc.html                (IPv6 của máy chủ web)
```
Truy cập bằng tên (`www.utc.edu.vn`) chỉ chạy khi DNS đã có bản ghi: khai **A** (WWW.UTC.EDU.VN → 113.20.118.5) trên DNSv4 và **AAAA** (WWW.UTC.EDU.VN → 2ABC:A4A9::5) trên DNSv6. Slide cố ý hỏi "tại sao" khi truy cập bằng tên mà chưa có bản ghi.

## 3. MAIL
Máy chủ mail > **Services > EMAIL**: bật SMTP và POP3, đặt domain `utc.edu.vn`, tạo tài khoản (slide: `aaa/123`, `bbb/234`, `ccc/345`, địa chỉ dạng `aaa@utc.edu.vn`). DNS cho mail: A `MAIL.UTC.EDU.VN → 113.20.118.8`, AAAA `MAIL.UTC.EDU.VN → 2ABC:A4A9::8`.

Máy trạm: **Desktop > Email**, nhập tên, địa chỉ email, máy chủ nhận/gửi (dùng tên `mail.utc.edu.vn` được vì đã có bản ghi), user và mật khẩu của tài khoản. Gửi thư, rồi người nhận kiểm tra hộp thư và trả lời.

## 4. DHCP trên router (v4)
```
ip dhcp excluded-address 19.16.20.1 19.16.20.30
ip dhcp pool UTC-DHCPv4-pool
 network 19.16.20.0 255.255.255.0
 default-router 19.16.20.1
 dns-server 194.0.1.18
```
Máy trạm chọn **DHCP** trong cấu hình IP là nhận được địa chỉ.

## 5. DHCP trên router (v6)
```
ipv6 dhcp pool UTC-DHCPv6-pool
 dns-server 2001:678:4::12
interface FastEthernet0/1
 ipv6 nd other-config-flag
 ipv6 dhcp server UTC-DHCPv6-pool
```
Bổ sung: với `other-config-flag`, DHCPv6 chỉ phát thông tin phụ như DNS; địa chỉ IPv6 vẫn do router quảng bá prefix cho máy trạm tự tạo.

## 6. DHCP trên máy chủ
Máy chủ > **Services > DHCP**, bật dịch vụ, rồi điền pool:
- DHCPv4: Pool Name (`serverPool`), Default Gateway, DNS Server, **Start IP Address**, Subnet Mask, **Maximum Number of Users**.
- DHCPv6: tạo pool (`serverPool-v6`), điền DNS Server, rồi khai **IPv6 Address Prefix**.

Địa chỉ bắt đầu nên nằm ngoài các địa chỉ đã gán tĩnh (cổng router, chính máy chủ).

## 7. DHCP Relay
Khi máy chủ DHCP nằm ở mạng khác, trên router đặt ở **cổng phía máy trạm**:
```
interface Fa0/0
 ip helper-address 55.14.92.5      (địa chỉ máy chủ DHCP)
```
Slide lưu ý: Router 2811 trong Packet Tracer 8.1.1 **không hỗ trợ DHCPv6 relay**. Hai mạng phải có định tuyến đi và về giữa router với nhau (xem `router-2811.md`).
