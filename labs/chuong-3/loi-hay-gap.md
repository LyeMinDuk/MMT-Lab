# Lỗi hay gặp ở các bài chương 3

1. **Quên `ipv6 unicast-routing`.** Địa chỉ và tuyến IPv6 đúng mà vẫn không ping được giữa các mạng. Bộ chấm báo rõ router nào chưa bật.
2. **Cổng router còn `shutdown`.** Mặc định cổng router tắt; mạng của cổng đó không xuất hiện trong bảng định tuyến. Kiểm tra bằng `show ip interface brief`.
3. **Next-hop sai.** Next-hop phải là địa chỉ cổng của router đầu kia trên đường nối chung, không phải địa chỉ cổng của chính mình, cũng không phải địa chỉ ở mạng khác.
4. **Chỉ có tuyến đi, thiếu tuyến về.** Ping cần cả hai chiều: R-DN phải biết đường về NET1 và NET3 chứ không chỉ R-HN biết đường tới NET3. Bộ chấm kiểm tra theo từng router xuất phát.
5. **Nhầm mask khi đặt tuyến tĩnh.** Ví dụ NET2 ở bài 02 là `255.255.255.128`, không phải `255.255.255.0`.
6. **Cổng serial không lên.** Thường do thiếu `clock rate` ở đầu DCE hoặc dùng sai loại cáp (serial DCE/DTE, không dùng cáp copper). Cáp cross-over chỉ dùng khi nối hai router bằng cổng FastEthernet.
7. **Đề ghi lệch.** Hai chỗ trong đề chương 3 thực hành 03: R-HCM "nối với R-HN" (đúng ra R-DN) và NET2 `127.16.0.0` (đúng ra `172.16.0.0`).
