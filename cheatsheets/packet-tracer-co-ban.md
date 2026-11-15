# Cheatsheet: Packet Tracer và cấu hình IP cơ bản (Chương 1 - Thực hành)

Nguồn: slide "Chương 1 - Thực hành". Mục "Bổ sung" là ghi chú rút ra khi làm bài thực tế.

## 1. Packet Tracer là gì
Phần mềm dạy và học công nghệ mạng của Cisco Networking Academy, dùng để minh họa cách mạng máy tính hoạt động (mô phỏng, trực quan hóa, cộng tác). Chuyển giữa Logical/Physical ở thanh điều hướng, giữa Realtime/Simulation ở thanh dưới; thiết bị và cáp nằm ở hộp Device-Type Selection, kéo thả vào Workspace.

## 2. Thiết bị và cáp dùng trong lab
```
Server-PT        PC-PT        Laptop-PT
Router 2811 (+ module NM-2FE2W)        Switch 2960-24TT
Cáp: Copper Straight-Through, Copper Cross-Over
```
Slide dặn: chỉ dùng **Copper Cross-Over** khi nối hai router với nhau. Muốn thêm cổng cho router (ví dụ module NM-2FE2W): tắt nguồn, kéo thả module vào khe, bật lại nguồn.

## 3. Cấu hình IP trên thiết bị đầu cuối (PC, Laptop, Server)
Mở thiết bị > tab **Config** > **FastEthernet0**: chọn **Static**, điền IPv4, Subnet Mask, và IPv6 kèm độ dài prefix (ví dụ `/64`). PC, Laptop, Server cấu hình giống nhau.

Bổ sung: default gateway (v4 và v6) nằm ở **GLOBAL > Settings**, không nằm trong mục FastEthernet0.

## 4. Cấu hình IP trên giao diện router
```
Router#conf t
Router(config)#interface fa0/0
Router(config-if)#ip address 132.54.78.1 255.255.255.0
Router(config-if)#ipv6 address 2AB1:1D8C:ABBA::1/64
Router(config-if)#no shut
```
Cổng router mặc định đang tắt: thiếu `no shut` thì mạng của cổng đó không hoạt động. Làm tương tự cho Fa0/1.

Bổ sung: muốn ping IPv6 qua lại **giữa các mạng** thì router cần `ipv6 unicast-routing` (xem `router-2811.md`).

## 5. Kiểm tra kết nối bằng ping
- Đầu cuối: **Desktop > Command Prompt**, gõ `ping <IPv4>` hoặc `ping <IPv6>` tới các thiết bị khác.
- Router: mở tab **CLI**, `ping` v4/v6 tới các thiết bị đầu cuối.
- Xem kết quả trả lời hay `Request timed out`, rồi lần lại theo thứ tự: IP và mask, gateway, cáp, cổng đã bật chưa.

## 6. Bổ sung: router không dây WRT300N
- Các cổng **Ethernet 1-4** là phía **LAN** của router không dây, cổng **Internet** là phía WAN. IP nằm ở phía LAN (ví dụ `211.13.45.10/24`) đặt trong giao diện **GUI** của router (mục Setup > Network Setup), cùng chỗ bật DHCP cho máy không dây.
- Máy không dây (Tablet, Smartphone): tab **Config > Wireless0**, chọn đúng SSID. Nếu máy hiện địa chỉ dạng `169.254.x.x` nghĩa là chưa nhận được IP từ DHCP.
- Tên các mục trong GUI có thể lệch chút giữa các phiên bản; hãy đối chiếu với màn hình của bạn.
