# Chương 6 - Thực hành 02: Bài tập tổng hợp (UTC và UTC2)

Nguồn: slide "Chương 6 - Thực hành 02". Bài nộp: `Chương 6 - Thực hành 02.zip` gồm file `.pkt` và file `.pdf` với 4 bảng (vị trí và chức năng, kết nối, quy hoạch địa chỉ IP, địa chỉ IP). Tự làm trong 6 tiết, nộp trong hai tuần.

> **Lưu ý về dữ liệu.**
> - Đây là bài **thiết kế**: bộ chấm kiểm tra quan hệ (prefix, không chồng lấn, DHCP theo mạng của cổng, định tuyến thông), không so địa chỉ cố định.
> - Slide không đặt tên server và laptop. `checks.json` dùng `UTC-Server-01` (DNS, lúc đầu cả Web và Mail), `UTC-Server-02` (server mới ở bước 6 chạy Web và Mail), `UTC2-Server-01`. Sửa lại nếu bạn đặt tên khác.
> - **Giả định về cổng router**, theo bảng của đề thi thử cùng bộ môn: R-UTC `Fa0/0` là VLAN 11, `Fa0/1` VLAN 10, `Fa1/0` VLAN 12, `Fa1/1` nối R-UTC2; R-UTC2 `Fa0/0` VLAN 21, `Fa0/1` VLAN 20, `Fa1/0` VLAN 22. Riêng `Fa1/0` của R-UTC (VLAN 12, nối `Fa0/3` của Sw-UTC-A2) và `Fa1/0` của R-UTC2 (VLAN 22, nối `Fa0/3` của Sw-UTC2) có trong slide. Các chỗ phụ thuộc giả định được chỉ rõ ở `checks.json` (bước 5 và 6 dùng cổng của R-UTC2).
> - Slide không nói rõ phải cập nhật bản ghi `www`/`mail` trên DNS khi Web, Mail chuyển sang server mới ở bước 6; bộ chấm không kiểm tra điều này, bạn nên tự xem lại.

## Quy hoạch VLAN và mạng
Dải IPv4 `116.154.208.0/23`, IPv6 `24C1:D8E0::/48`.

| Mạng | IPv4 | IPv6 | VLAN |
|---|---|---|---|
| L1 | `/24` | `/64` | 12 (UTC-Cla) |
| L2 | `/25` | `/64` | 22 (UTC2-Cla) |
| L3 | `/26` | `/64` | 10 (UTC-Ser) |
| L4 | `/27` | `/64` | 20 (UTC2-Ser) |
| L5 | `/28` | `/64` | 11 (UTC-Vip) |
| L6 | `/29` | `/64` | 21 (UTC2-Vip) |
| L7 | `/30` | `/64` | nối R-UTC và R-UTC2 |

## Bước 1 - Triển khai tại UTC A1
1 router, 1 switch, 1 server, 5 laptop. Switch `Sw-UTC-A1` và router `R-UTC`, mật khẩu đặc quyền `UTC@123`; VLAN 10 `UTC-Ser` (server), VLAN 11 `UTC-Vip` (laptop ban lãnh đạo); địa chỉ, tốc độ, full duplex cho cổng router. Server: DNS `dns.utc.edu.vn` (miền `utc.edu.vn`); Web `www.utc.edu.vn` với file `utc-index.html` ("UTC - THE WAY TO SUCCESS"); Mail `mail.utc.edu.vn` với `vip1/123`, `vip2/234`, `vip3/345` (địa chỉ `vip1@utc.edu.vn`...). Kiểm tra kết nối, DNS, Web, Mail.

## Bước 2 - Bổ sung các lớp ở tòa A2
Thêm module NM-2FE2W cho R-UTC, switch `Sw-UTC-A2` (mật khẩu `UTC@123`), 10 PC. `Fa1/0` của R-UTC nối `Fa0/3` của Sw-UTC-A2 (VLAN 12 `UTC-Cla`). Trunk giữa hai switch cho VLAN 10, 11, 12. DHCP trên R-UTC cho VLAN 12: pool `UTC-DHCPv4-pool`, loại trừ từ `.+1` đến `.+60` của L1, network L1 (`/24`), default-router `.+1`, dns-server là server DNS (`L3 .+3`). PC dùng DHCP, kiểm tra kết nối và dịch vụ.

## Bước 3 - Phân hiệu UTC2 ở TP.HCM
Thêm switch `Sw-UTC2` (mật khẩu `UTC@123`) và 3 laptop (ban lãnh đạo UTC2, VLAN 21 `UTC2-Vip`), nối với router ở UTC. Kiểm tra kết nối và dịch vụ.

## Bước 4 - IPv6
Dùng `24C1:D8E0::/48`, mỗi VLAN một `/64`. VLAN 12 được cấp IPv6 qua DHCP từ `Fa1/0` của R-UTC: pool `UTC-DHCPv6-pool`, dns-server là IPv6 của server DNS (`L3-v6 ::+3`). Kiểm tra kết nối và dịch vụ v4/v6.

## Bước 5 - Nâng cấp theo chuyển đổi số
Thêm router `R-UTC2` (có NM-2FE2W) và server `UTC2-Server-01`; hai router nối nhau, các giao diện nối switch đặt tốc độ và full duplex. Tuyến mặc định trên R-UTC, tuyến tĩnh trên R-UTC2. DNS: khai miền `utc2.edu.vn` trên DNS của UTC. Web `www.utc2.edu.vn` với `utc2.html` ("Welcome to UTC2, Ho Chi Minh City, Vietnam."); Mail `mail.utc2.edu.vn` với `vip12/123`, `vip22/234`, `vip32/345` (địa chỉ `vip1@utc2.edu.vn`...). Kiểm tra kết nối và dịch vụ hai miền.

## Bước 6 - Rà soát và hoàn thiện
Tại UTC: DNS giữ nguyên trên server ban đầu; Web, Mail chuyển sang server mới `UTC-Server-02`. Tại UTC2: thêm VLAN 22 `UTC2-Cla` trên Sw-UTC2, `Fa0/3` của Sw-UTC2 nối `Fa1/0` của R-UTC2, thêm 10 PC. Kiểm tra toàn bộ.

## Chấm tự động
```
python tools/check.py bai.pkt --lab labs/chuong-6/thuc-hanh-02-tong-hop --step 4
```
Lưu một file `.pkt` sau mỗi bước. Các bước sau chấm lại cả cấu hình của bước trước (trừ chỗ đề yêu cầu thay đổi, như Web, Mail chuyển server ở bước 6).
