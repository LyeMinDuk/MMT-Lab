# MMT-Lab

Luyện thực hành môn Mạng máy tính (Cisco Packet Tracer 8.1.1.0022). Đi cùng repo trắc nghiệm MMT-Quiz.

Hiện có:
- **Chương 2**: thực hành 01 (cheatsheet switch), thực hành 02 (kịch bản 10 bước), thực hành 03 (bài nộp).
- **Chương 3**: thực hành 01 (cheatsheet router), thực hành 02 (mạng kết nối, định tuyến tĩnh/mặc định), thực hành 03 (bài nộp).

Các chương khác sẽ bổ sung dần.

## Cấu trúc
```
tools/pkt2xml.py     giải mã .pkt/.pka thành XML + file tóm tắt (để gửi cho Claude xem)
tools/check.py       chấm bài offline: đọc file .pkt và so với checks.json
tests/               test cho check.py và các checks.json (python tests/test_check.py; python tests/test_specs.py)
cheatsheets/         tóm tắt lệnh theo từng bài thực hành
labs/chuong-N/...    đề (de.md) + tiêu chí chấm (checks.json) cho từng bài
```

## Cài đặt
```
pip install -r requirements.txt     # securedypkt
```

## Quy trình luyện một bài
1. Đọc `labs/.../de.md`, làm trong Packet Tracer, **lưu một file `.pkt` sau mỗi bước**.
2. Chấm theo bước: `python tools/check.py bai.pkt --lab labs/chuong-2/thuc-hanh-02-kich-ban --step 4`.
   Kết quả chỉ nêu yêu cầu và thực tế, kèm lệnh `show` để xem lại, không đưa sẵn đáp án.
3. Phần ping và bảng MAC vẫn tự kiểm tra trong Packet Tracer.
4. Muốn xem script đọc được gì từ file: `python tools/check.py bai.pkt --dump`.

## Gửi file cho Claude xem
```
python tools/pkt2xml.py bai.pkt --summary --configs
```
Gửi file `bai.summary.txt` (vài KB). File `.xml` nặng khoảng 1 MB, chỉ cần khi phải soi sâu.

## Thêm bài mới
Tạo `labs/chuong-N/<tên-bài>/` gồm `de.md` và `checks.json`:
```json
{"title": "...", "steps": 3, "checks": [
  {"type": "vlan", "device": "SW-1", "id": 2, "name": "DT", "from": 1},
  {"type": "trunk_allowed", "device": "SW-1", "port": "Gi0/1", "vlans": [3, 4], "from": 2, "to": 2}
]}
```
`from`/`to` là khoảng bước áp dụng (mặc định mọi bước). Tên `device` là **tên hiển thị** trong Packet Tracer.

| type | tham số |
|---|---|
| `vlan` / `no_vlan` | device, id, (name) |
| `port_vlan` | device, ports (`Fa0/6-10`, `Fa0/1,Fa0/3`), vlan |
| `port_mode` | device, port, mode (`access`/`trunk`) |
| `trunk_allowed` | device, port, vlans |
| `port_shutdown` | device, port, (shutdown: true/false) |
| `port_default` | device, port (cổng không còn dòng cấu hình nào) |
| `enable_secret` | device |
| `hostname` | device, name |
| `ip` | device, ipv4, (mask) |
| `ipv6` | device, ipv6 (một giá trị hoặc danh sách), (prefix) |
| `link` / `no_link` | a, b (dạng `SW-1:Fa0/24`, serial: `R-HN:Se0/0/0`) |
| `port_ip` | device, port, ipv4, mask, (ipv6, prefix): địa chỉ đặt trên **cổng router** |
| `port_up` | device, port (cổng không còn `shutdown`) |
| `ipv6_routing` | device (có `ipv6 unicast-routing`) |
| `reach` | device, dest (địa chỉ IPv4 hoặc IPv6): mô phỏng đi theo bảng định tuyến từ router này tới `dest` |

`from`, `to` là khoảng bước nên **không dùng làm tên tham số** của loại kiểm tra (vì vậy `reach` dùng `dest`). `ip`/`ipv6` nhận `mask: null`/`prefix: null` nếu không cần xét độ dài mask.

`reach` đi theo mạng nối trực tiếp (cổng đang bật), tuyến tĩnh và tuyến mặc định, theo next-hop; với IPv6 mỗi router chuyển tiếp phải có `ipv6 unicast-routing`. Nó báo router nào thiếu tuyến, next-hop sai, cổng tắt hoặc vòng lặp. Vì chấm theo kết quả đường đi nên tĩnh hay mặc định đều được.

## Giới hạn đã biết
- Đọc cấu trúc file đã kiểm chứng trên một file `.pkt` thật (thiết bị, IP, IPv4/IPv6, link, running-config). **Chưa kiểm chứng** trên file chương 2 có VLAN tùy chỉnh và cấu hình trunk thật: nếu có loại kiểm tra nào chấm sai, chạy `--dump` để xem script đọc được gì rồi báo lại.
- Chưa thử với file `.pka`.
- Chương 3 mới kiểm thử trên mạng giả lập dựng tay (test), chưa trên file `.pkt` chương 3 thật. Tuyến có next-hop là tên cổng (`ip route ... Serial0/0/0`) chưa được `reach` hỗ trợ.
- Slide chương 3 thực hành 02 là bản chữ không có hình topology nên thiếu địa chỉ máy trạm, mask đường nối hai router và tên cổng; xem `de.md` của bài đó và sửa `checks.json` khi có đủ thông tin.
- Đề chương 3 thực hành 03 ghi lệch hai chỗ (R-HCM nối R-HN, NET2 `127.16.0.0`); xem `labs/chuong-3/loi-hay-gap.md`.
- Không chấm ping, bảng MAC hay trạng thái STP.
- Slide chương 2 thực hành 02 mâu thuẫn ở IPv6 của LAN 2 (`EFA` và `DEFA`); bộ chấm chấp nhận cả hai.

## Đẩy lên GitHub
```
git init && git add . && git commit -m "Khởi tạo MMT-Lab"
git branch -M main
git remote add origin https://github.com/<tên-bạn>/MMT-Lab.git
git push -u origin main
```
`.gitignore` đã loại `*.pkt`, `*.pka`, `*.xml`, `*.pdf` để không đẩy bài nộp và tài liệu của trường. Nên để repo private.
