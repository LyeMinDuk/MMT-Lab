# Lỗi hay gặp ở các bài chương 6

1. **Chia mạng theo thứ tự tùy ý.** Cấp mạng nhỏ trước làm mạng lớn không còn chỗ căn hàng (địa chỉ mạng phải chia hết cho kích thước của nó). Xếp các mạng theo kích thước giảm dần rồi cấp liên tiếp.
2. **Chọn prefix lớn hơn cần thiết hoặc quên cổng router.** Đếm cả cổng router khi tính số máy, rồi chọn prefix nhỏ nhất đủ chỗ.
3. **Hai mạng chồng lấn nhau.** Router vẫn nhận địa chỉ nhưng một trong hai mạng sẽ không hoạt động đúng; lập lại bảng chia mạng rồi so từng dải.
4. **Đề tự mâu thuẫn ở VLAN 21 (thi thử).** Mạng `/29` chỉ có 6 địa chỉ máy nhưng bảng ghi `.+7` và `.+9`. Hỏi người ra đề thay vì cố đặt cho khớp.
5. **Quên trunk cho đủ VLAN.** Trunk giữa hai switch phải cho phép mọi VLAN dùng ở hai đầu (10, 11, 12 hoặc 20, 21, 22). Thiếu một VLAN thì máy ở tòa kia không ra được router.
6. **Gán sai VLAN cho cổng nối router.** Cổng switch nối giao diện router phải ở đúng VLAN của giao diện đó; nhầm hai cổng thì địa chỉ và gateway của hai VLAN bị đảo.
7. **DHCP: `dns-server` sai hoặc thiếu `excluded-address`.** DNS phải là địa chỉ máy chủ DNS thật; loại trừ dải địa chỉ đã gán tĩnh để client không nhận trùng.
8. **Quên bật `ipv6 unicast-routing` hoặc thiếu tuyến IPv6.** v4 thông nhưng v6 không: kiểm tra riêng `show ipv6 route`.
9. **Chuyển Web, Mail sang server mới mà không đổi bản ghi DNS.** Truy cập bằng tên vẫn trỏ về server cũ.
10. **Tên pool DHCP có dấu cách.** Slide ghi `UTC Lib-DHCPv4-pool`; tên pool IOS là một từ, hãy dùng dấu gạch nối.
