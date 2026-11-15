# Chương 2 - Thực hành 03: Bài nộp cuối chương

Nguồn: file đề "Bài nộp cuối chương" của môn. Lưu file `Hovaten_MSSV.pkt`.

## Kết nối
- Phòng đào tạo (DT) cắm Fa0/1-5, phòng kế hoạch (KH) cắm Fa0/6-10, phòng tài chính (TC) cắm Fa0/11-15 trên SW-1.
- Phòng quản lý (QL) cắm Fa0/21, Fa0/22, Fa0/23 trên SW-2.
- SW-1 và SW-2 nối nhau qua Fa0/24 (mỗi switch) và Gi0/1 (mỗi switch).

| Thiết bị | Cổng | Tới (thiết bị) |
|---|---|---|
| DT-PC01 / DT-PC02 | Fa0 | Fa0/1, Fa0/2 (SW-1) |
| KH-PC01 / KH-PC02 | Fa0 | Fa0/6, Fa0/7 (SW-1) |
| TC-PC01 / TC-PC02 | Fa0 | Fa0/11, Fa0/12 (SW-1) |
| QL-DT01 / QL-KH01 / QL-TC01 | Fa0 | Fa0/21, Fa0/22, Fa0/23 (SW-2) |

## Địa chỉ (mask /24 cho IPv4, /64 cho IPv6)
| Máy | IPv4 | IPv6 |
|---|---|---|
| DT-PC01 | 192.167.5.10 | 2AB1:1D8C:ABBA::2 |
| DT-PC02 | 192.167.5.11 | 2AB1:1D8C:ABBA::4 |
| QL-DT01 | 192.167.5.12 | 2AB1:1D8C:ABBA::6 |
| KH-PC01 | 200.10.75.10 | 200E:2C0A:F1C6:1231::6 |
| KH-PC02 | 200.10.75.11 | 200E:2C0A:F1C6:1231::8 |
| QL-KH01 | 200.10.75.12 | 200E:2C0A:F1C6:1231::10 |
| TC-PC01 | 115.100.15.10 | 3ABC:FFFF:6666:5D7F::5 |
| TC-PC02 | 115.100.15.11 | 3ABC:FFFF:6666:5D7F::7 |
| QL-TC01 | 115.100.15.12 | 3ABC:FFFF:6666:5D7F::9 |

## Các bước (khớp với `--step` của check.py)
**Bước 1.** Đặt mật khẩu enable cho SW-1, SW-2. Trên SW-1 tạo VLAN 2, 3, 4 tên DT, KH, TC và gán mỗi VLAN một dải 5 cổng. Trên SW-2 tạo VLAN 2, 3, 4 tên QLDT, QLKH, QLTC, mỗi VLAN một cổng (Fa0/21, Fa0/22, Fa0/23). Thêm Fa0/24 vào VLAN DT (SW-1) và QLDT (SW-2), chế độ access. Ping trong VLAN 2, xem bảng MAC hai switch.

**Bước 2.** Tạo trunk Gi0/1 giữa hai switch, cho phép VLAN KH, TC, QLKH, QLTC (tức VLAN 3, 4). Ping trong VLAN 3 và 4, xem bảng MAC.

**Bước 3.** Tắt Fa0/24, xóa cáp giữa hai switch, đưa Fa0/24 về mặc định. Cho phép thêm VLAN DT và QLDT qua trunk. Ping lần lượt trong VLAN 2, 3, 4, xem bảng MAC.

## Yêu cầu
Ping thành công giữa các thiết bị cùng VLAN; hai switch hiển thị đầy đủ bảng MAC.

## Chấm tự động
```
python tools/check.py bai.pkt --lab labs/chuong-2/thuc-hanh-03-bai-nop --step 1
```
Lưu một file `.pkt` sau mỗi bước rồi chấm với `--step` tương ứng. Không có `--step` thì chấm bước cuối (bước 3).
