# Cheatsheet: Router Cisco 2811 (Chương 3 - Thực hành 01)

Nguồn: slide "Chương 3 - Thực hành 01 - Cấu hình Router cơ bản". Các chế độ EXEC/Config và lệnh `?`, `enable`, `conf t`, `exit`/`end` giống switch (xem `switch-2960.md`).

## Lệnh show
```
show interfaces                 show int fa0/1
show ip                         show ipv6
show protocols
show ip route                   show ip cef            (bảng định tuyến / chuyển mạch IPv4)
show ipv6 route                 show ipv6 cef
show running-config
```
`show ipv6 cef` chỉ dùng được sau khi đã bật định tuyến IPv6 (xem mục 2).

## Tham số chung
```
hostname R-UTC                  (no hostname: về tên mặc định "Router")
enable secret UTC@123
no ip domain-lookup             (không đổi từ gõ sai thành địa chỉ IP)
write memory
```

## Bật IPv6 trên router
```
ipv6 unicast-routing            cho phép chuyển tiếp gói IPv6 giữa các giao diện
ipv6 cef                        (slide có nêu cùng lệnh trên; là CEF cho IPv6, cần để dùng show ipv6 cef)
```
Quên `ipv6 unicast-routing` thì router không chuyển tiếp IPv6 giữa các mạng, dù địa chỉ và tuyến đều đúng.

## Giao diện
```
interface FastEthernet0/0
 speed 100
 duplex full
 ip address <IPv4> <mask>
 ipv6 address <prefix>/<độ dài>
 no shutdown                    (bật cổng; shutdown để tắt)
```
Nếu đặt speed/duplex trên cổng router thì cổng switch nối với nó cũng phải đặt giống vậy.

## Định tuyến tĩnh và mặc định
```
ip route <mạng đích> <mask đích> <next-hop>
ipv6 route <prefix đích>/<độ dài> <next-hop>
ip route 0.0.0.0 0.0.0.0 <next-hop>          (mặc định IPv4)
ipv6 route ::/0 <next-hop>                   (mặc định IPv6)
```
Next-hop là địa chỉ của cổng **router đầu kia** trên đường nối chung.

## Bổ sung (rút ra từ thực hành, chưa có trong slide)
- Cổng serial (WIC-2T) giữa hai router: thường phải đặt `clock rate` ở đầu DCE thì đường nối mới lên (`up/up` trong `show ip interface brief`). Hãy xác nhận khi làm bài.
- Kiểm tra nhanh cả cổng và địa chỉ: `show ip interface brief`.
