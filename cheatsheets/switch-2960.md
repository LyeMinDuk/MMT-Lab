# Cheatsheet: Switch Cisco 2960 (Chương 2 - Thực hành 01)

Nguồn: slide "Chương 2 - Thực hành 01 - Cấu hình Switch cơ bản". Mục "Bổ sung" là ghi chú rút ra khi làm bài.

## 1. Các chế độ
| Chế độ | Dấu nhắc | Vào bằng | Thoát bằng |
|---|---|---|---|
| User EXEC | `Switch>` | (mặc định) | |
| Privileged EXEC | `Switch#` | `enable` | `disable`, `exit`, `logout` |
| Global Config | `Switch(config)#` | `conf t` | `end`, `exit`, `Ctrl+Z` |

`?` xem trợ giúp ở mọi nơi. `no <lệnh>` hủy lệnh hoặc đưa về mặc định.

## 2. Lệnh show
```
show arp
show mac address-table          (cũng gõ được show mac-address-table)
show interfaces fa0/1           show int fa0/3 status
show vlan                       show vlan brief        show vlan id 1
show running-config
```
Bổ sung (dùng khi gỡ lỗi): `show interfaces trunk`, `show spanning-tree vlan 2`.

## 3. Tham số chung
```
hostname SW-1                   (no hostname: về tên mặc định)
enable secret <mật khẩu>
write memory                    (viết tắt: wr, wri mem)
```

## 4. VLAN
```
vlan 2                          name VLAN-Test        (tạo / đổi tên)
no vlan 2                                              (xóa)
```

## 5. Cổng access
```
interface fa0/20
 switchport mode access
 switchport access vlan 20
interface range fa0/11,fa0/13,fa0/15      (danh sách cổng)
interface range fa0/6-9                   (dải cổng)
```
Đưa cổng về VLAN mặc định: `default interface fa0/11` (ở chế độ config) hoặc `no switchport access vlan` (trong interface).

## 6. Cổng trunk
```
interface gi0/1
 description To-SW1-Gi0/1
 switchport mode trunk
 switchport trunk allowed vlan 1,3,5
 switchport trunk native vlan 5
```
Đóng gói mặc định trên 2960 là dot1q. Mặc định cho phép mọi VLAN, native VLAN là 1.

Bổ sung: `switchport trunk allowed vlan add 2` thêm VLAN mà không ghi đè danh sách cũ.

## 7. Bổ sung: cổng màu cam trong Packet Tracer
Cổng cam là STP chưa cho chuyển tiếp, không liên quan tới speed. Hai nguyên nhân hay gặp:
- Mới cắm cáp: đợi 30-50 giây hoặc bấm Fast Forward Time.
- Có vòng lặp (hai đường nối giữa hai switch cùng cho một VLAN đi qua): `show spanning-tree vlan N` sẽ thấy một cổng ở `BLK`. Xem lại danh sách VLAN được phép trên trunk.

## 8. Bổ sung: kiểm tra khi cùng VLAN mà ping không được
1. IP và mask của hai máy (từng octet), 2. Cổng đã đúng VLAN chưa (`show vlan brief`), 3. Cáp và đèn cổng, 4. Bảng MAC (`show mac address-table`).
