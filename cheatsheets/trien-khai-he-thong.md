# Cheatsheet: Triển khai hệ thống và chia mạng (Chương 6)

Nguồn: slide "Chương 6 - Thực hành 01, 02" và đề thi thử. Mục "Bổ sung" là kiến thức chung về chia mạng.

## 1. Sáu bước triển khai
1. **Lập kế hoạch**: xác định yêu cầu, kế hoạch triển khai.
2. **Chuẩn bị hạ tầng**: tủ rack, nguồn (UPS), làm mát (điều hòa), phụ kiện. *(không làm được trong lab)*
3. **Cài đặt phần cứng**: gắn router, switch, server vào rack; nối cáp, cấp nguồn, bật thiết bị. *(không làm được trong lab)*
4. **Cấu hình thiết bị mạng**: switch, router, thiết bị khác.
5. **Cấu hình máy chủ**: cấu hình mạng, cấu hình dịch vụ.
6. **Kiểm thử và hoàn thiện tài liệu**: kiểm thử, xử lý lỗi (mạng, dịch vụ), hoàn thiện tài liệu.

Bài nộp kèm các bảng: **vị trí và chức năng**, **kết nối**, **địa chỉ IP** (và topology mạng); thực hành 02 nộp thêm bảng **quy hoạch địa chỉ**.

## 2. Chia mạng IPv4 theo VLSM (Bổ sung)
Số máy dùng được trong một mạng `/n` là `2^(32-n) - 2`:

| Prefix | /24 | /25 | /26 | /27 | /28 | /29 | /30 |
|---|---|---|---|---|---|---|---|
| Máy dùng được | 254 | 126 | 62 | 30 | 14 | 6 | 2 |

Cách làm:
1. Đếm số máy mỗi mạng, **cộng thêm cổng router** (và dự phòng nếu đề yêu cầu).
2. Chọn prefix **nhỏ nhất** (mạng con bé nhất) vẫn đủ chỗ.
3. Xếp các mạng theo kích thước **giảm dần**, cấp liên tiếp từ đầu dải, mỗi mạng bắt đầu ở địa chỉ chia hết cho kích thước của nó.
4. Kiểm tra các mạng **không chồng lấn** và nằm trong dải được cấp (ví dụ `/23`).

Địa chỉ mạng + 1 thường dành cho cổng router; máy trạm lấy các địa chỉ kế tiếp (đề thi thử ghi là `.+1`, `.+2`...).

## 3. Chia mạng IPv6 (Bổ sung)
Từ dải `/48`, mỗi VLAN lấy một mạng `/64` bằng cách tăng nhóm thứ tư: `…::/64`, `…:0:1::/64`, `…:0:2::/64`... Đề thi thử ghi rõ: dải bé nhất cho L1, kế tiếp cho L2, L3... Địa chỉ trong mạng IPv6 theo cùng quy ước `::+1`, `::+2`.

## 4. Kiểm tra nhanh khi triển khai
```
show vlan brief                  show interfaces trunk
show ip interface brief          show ip route / show ipv6 route
show running-config              ping, nslookup, trình duyệt, email client
```
Lần lượt: cáp và cổng, VLAN và trunk, địa chỉ, định tuyến, dịch vụ.

## 5. Mẫu bảng tài liệu
- **Vị trí và chức năng**: STT | tên thiết bị | loại | vị trí | chức năng.
- **Kết nối**: STT | tên thiết bị | loại | giao diện | tới giao diện (của thiết bị).
- **Quy hoạch địa chỉ**: mạng LAN | VLAN | prefix IPv4 | prefix IPv6 | ghi chú.
- **Địa chỉ IP**: mạng | địa chỉ IPv4 | địa chỉ IPv6 | ghi chú; có dòng Net ID và Host ID.
