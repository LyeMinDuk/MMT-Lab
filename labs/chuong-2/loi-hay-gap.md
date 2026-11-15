# Lỗi hay gặp ở các bài chương 2

Rút ra từ lúc làm bài thực tế.

1. **Cùng VLAN mà ping không được.** Kiểm tra IP và mask trước, VLAN sau. Từng gặp: gõ nhầm octet thứ hai (`115.200.15.10` thay vì `115.100.15.10`), hai máy rơi vào hai mạng khác nhau nên không ping được dù cùng VLAN 4. Bộ chấm bắt lỗi này bằng loại kiểm tra `ip`.
2. **Cổng Fa0/24 màu cam, bấm speed không hết.** Đây là STP, không phải tốc độ. Khi trunk Gi0/1 cho cả VLAN 2 đi qua trong lúc Fa0/24 cũng đang nối VLAN 2 thì tạo vòng lặp và STP chặn một cổng (`show spanning-tree vlan 2` hiện `Altn BLK`). Ở bước chỉ cho VLAN 3, 4 qua trunk thì danh sách trunk phải đúng như thế.
3. **IPv6 trùng địa chỉ gateway.** Từng gặp ở bài chương 1: PC có IPv6 `::1`, trùng với cổng router, trong khi đề yêu cầu `::123`. Bộ chấm loại `ipv6` bắt được.
4. **`switchport trunk allowed vlan` ghi đè danh sách.** Muốn thêm VLAN mà giữ nguyên danh sách cũ thì dùng `add`.
5. **`default interface` xóa sạch cấu hình cổng.** Sau lệnh này cổng về VLAN 1 và bật lại; kiểm tra bằng `show vlan brief`.
6. **Quên xóa cáp** khi bước yêu cầu bỏ kết nối: xóa cáp trong Packet Tracer bằng công cụ Delete, không chỉ shutdown cổng.
