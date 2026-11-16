# Chương 6 - Thực hành 03: Thi thử (60 phút, làm trên Packet Tracer)

Nguồn: "Thuyết minh đề" của đề thi thử (phần A: thông tin cần thiết). Cán bộ coi thi không giải thích thêm.

> **Lưu ý về dữ liệu.**
> - File chỉ có phần A (tên thiết bị, bảng kết nối, quy hoạch địa chỉ). Phần yêu cầu cụ thể của đề (nếu có) không nằm trong file, nên bộ chấm kiểm tra trạng thái cuối: thiết bị, cáp, VLAN, địa chỉ, định tuyến thông.
> - **Đề tự mâu thuẫn ở VLAN 21.** L6 là `/29` (chỉ có 6 địa chỉ máy, `.+1` đến `.+6`), nhưng bảng ghi `VL21-LT1 = .+7` (địa chỉ broadcast) và `VL21-LT2 = .+9` (nằm ngoài mạng). Hai máy này không đặt được IPv4 như bảng; bộ chấm chỉ kiểm tra IPv6 (`::+7`, `::+9`) cho hai máy đó. Nên hỏi người ra đề.
> - Bảng địa chỉ không nêu dải cấp phát, nên bộ chấm không kiểm tra dải mà chỉ kiểm tra prefix, vị trí máy trong mạng và không chồng lấn.

## Thiết bị
Switch 2960: `SW-UTC-01`, `SW-UTC-02`, `SW-UTC2-01`, `SW-UTC2-02`. Router 2811 (+NM-2FE2W): `R-UTC`, `R-UTC2`. PC `VL12-PC1/2`, `VL22-PC1/2`; Server `VL10-SV1/2`, `VL20-SV1/2`; Laptop `VL11-LT1/2`, `VL21-LT1/2`.

## Bước 1 - Dựng thiết bị và kết nối
Nối theo bảng kết nối: ở mỗi tòa, ba cổng `Fa0/0`, `Fa0/1`, `Fa1/0` của router nối `Fa0/1`, `Fa0/2`, `Fa0/3` của switch 01; `Fa0/10`, `Fa0/11`, `Fa0/12` của switch 01 nối server, laptop, PC; `Gi0/1` hai switch nối nhau; switch 02 nối `Fa0/1`, `Fa0/2`, `Fa0/3` với server, laptop, PC; `Fa1/1` hai router nối nhau.

## Bước 2 - VLAN, cổng access và trunk
Tòa UTC: VLAN 10 `UTC-SER`, 11 `UTC-VIP`, 12 `UTC-CLA`. Tòa UTC2: VLAN 20 `UTC2-SER`, 21 `UTC2-VIP`, 22 `UTC2-CLA`. Cổng switch ở VLAN tương ứng với thiết bị nối vào (cổng nối router theo VLAN của giao diện router: Fa0/0 là VLAN 11/21, Fa0/1 là VLAN 10/20, Fa1/0 là VLAN 12/22); `Gi0/1` là trunk.

## Bước 3 - Địa chỉ IPv4 và IPv6
Độ dài prefix: L1 `/24` (VLAN 12), L2 `/25` (VLAN 22), L3 `/26` (VLAN 10), L4 `/27` (VLAN 20), L5 `/28` (VLAN 11), L6 `/29` (VLAN 21), L7 `/30` (nối hai router); IPv6 mỗi mạng `/64`, L1 lấy dải bé nhất rồi lần lượt L2, L3... Vị trí máy trong mạng (`.+n` và `::+n`):

| Giao diện router | Địa chỉ | Máy | Địa chỉ |
|---|---|---|---|
| Fa0/0, Fa0/1, Fa1/0, Fa1/1 của R-UTC và R-UTC2 | `.+1`, `::+1` (riêng Fa1/1 của R-UTC2 là `.+2`, `::+2`) | VL12-PC1/2 | `.+2`, `.+4` |
| | | VL22-PC1/2 | `.+6`, `.+8` |
| | | VL11-LT1/2 | `.+3`, `.+5` |
| | | VL21-LT1/2 | `.+7`, `.+9` (xem lưu ý) |
| | | VL10-SV1/2, VL20-SV1/2 | `.+3`, `.+5` |

## Bước 4 - Định tuyến thông
Hai router thấy nhau: dùng tuyến tĩnh hoặc mặc định (cả v4 và v6, nhớ bật định tuyến IPv6); mọi mạng của UTC và UTC2 ping thông nhau.

## Chấm tự động
```
python tools/check.py bai.pkt --lab labs/chuong-6/thuc-hanh-03-thi-thu --step 4
```
Làm đủ trong 60 phút rồi chấm; chấm theo `--step` để xem phần nào còn sót.
