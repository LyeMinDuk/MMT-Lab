# Lỗi hay gặp ở các bài chương 1

1. **IPv6 của máy trùng gateway.** Từng gặp: PC có IPv6 `2001:DB8:3C4D:1::1`, trùng với cổng Fa0/0 của router, trong khi đề yêu cầu `::123`. Hai thiết bị cùng địa chỉ thì ping không ổn định; so lại từng nhóm số với đề.
2. **Cổng router còn tắt.** Cổng router mặc định `shutdown`; thiếu `no shut` thì không ping qua router được.
3. **Quên default gateway.** Cùng LAN thì ping được, nhưng sang mạng khác thì không. Gateway đặt ở GLOBAL > Settings, không ở mục FastEthernet0.
4. **Cắm nhầm cổng router không dây.** Các cổng Ethernet 1-4 là phía LAN; IP `211.13.45.10` của đề là IP phía LAN, đặt trong GUI của router (Setup), không đặt ở cổng Internet.
5. **Tablet/Smartphone ở `169.254.x.x`.** Máy chưa nhận được IP từ DHCP của router không dây: kiểm tra SSID ở tab Config > Wireless0 có khớp với router không, và router đã bật DHCP chưa.
6. **Dùng Cross-Over bừa.** Chỉ dùng Cross-Over khi nối hai router; các kết nối còn lại trong bài này dùng Straight-Through.
7. **Lệnh `configt` trong slide.** Slide gõ dính thành `configt`; lệnh đúng là `conf t` (hoặc `configure terminal`).
