# Lỗi hay gặp ở các bài chương 5

1. **Truy cập bằng tên miền khi chưa có bản ghi.** Truy cập `www.utc.edu.vn` thất bại dù truy cập bằng IP được, vì máy trạm chưa phân giải được tên. Khai bản ghi A (v4) và AAAA (v6) cho tên đó, và đảm bảo máy trạm trỏ tới đúng máy chủ DNS.
2. **Quên đặt DNS Server trên máy trạm.** `nslookup` không có trả lời hoặc báo không tìm thấy máy chủ; kiểm tra địa chỉ DNS đã nhập.
3. **Dịch vụ chưa bật.** DNS, HTTP/HTTPS, Email, DHCP đều phải ở trạng thái On trong tab Services thì mới phục vụ.
4. **Nhầm họ địa chỉ giữa hai máy chủ DNS.** Bản ghi A thuộc DNSv4, bản ghi AAAA thuộc DNSv6; khai sai máy thì truy vấn trả về rỗng.
5. **Thiếu `excluded-address` trên DHCP router.** Client có thể được cấp trúng địa chỉ của cổng router; slide loại trừ `.1` đến `.30`.
6. **Start IP trên máy chủ DHCP trùng thiết bị cố định.** Địa chỉ bắt đầu và số người dùng tối đa phải nằm ngoài các địa chỉ đã gán cho router và máy chủ.
7. **Đặt `ip helper-address` sai cổng.** Lệnh đặt ở cổng phía máy trạm (Fa0/0 của R-UTC2) và trỏ tới IP máy chủ DHCP; hai mạng còn cần định tuyến đi và về.
8. **Mong đợi DHCPv6 relay trên router 2811.** Theo slide, router 2811 trong Packet Tracer 8.1.1 không hỗ trợ, nên bài 3 chỉ làm DHCPv4.
9. **Email: sai domain hoặc sai tài khoản.** Địa chỉ phải đúng dạng `aaa@utc.edu.vn`; user và mật khẩu ở client khớp với tài khoản tạo trên máy chủ mail.
