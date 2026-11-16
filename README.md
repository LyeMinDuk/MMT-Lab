# MMT-Lab

Luyện thực hành môn Mạng máy tính (Cisco Packet Tracer 8.1.1.0022). Đi cùng repo trắc nghiệm MMT-Quiz.

Hiện có:
- **Chương 1**: thực hành 01 (xây dựng mạng, cấu hình IP, ping), thực hành 02 (bài tập nộp có router không dây) và cheatsheet Packet Tracer cơ bản.
- **Chương 2**: thực hành 01 (cheatsheet switch), thực hành 02 (kịch bản 10 bước), thực hành 03 (bài nộp).
- **Chương 3**: thực hành 01 (cheatsheet router), thực hành 02 (mạng kết nối, định tuyến tĩnh/mặc định), thực hành 03 (bài nộp).
- **Chương 5**: thực hành 01 (DNS, WEB, MAIL), thực hành 02 (DHCP trên router, trên máy chủ, qua relay) và cheatsheet dịch vụ.
- **Chương 6**: thực hành 01 (triển khai hệ thống thư viện), thực hành 02 (tổng hợp UTC và UTC2, 6 bước), thực hành 03 (thi thử 60 phút) và cheatsheet triển khai, chia mạng.

Các chương khác sẽ bổ sung dần.

## Cấu trúc
```
index.html          trang web theo dõi bài, checklist từng bước, tra lệnh (một file, không thư viện)
tools/build_web.py   nhúng dữ liệu từ labs/ và cheatsheets/ vào index.html
tools/pkt2xml.py     giải mã .pkt/.pka thành XML + file tóm tắt (để gửi cho Claude xem)
tools/check.py       chấm bài offline: đọc file .pkt và so với checks.json
tests/               test cho check.py, checks.json và trang web (python tests/test_check.py; test_specs.py; test_web.py)
cheatsheets/         tóm tắt lệnh theo từng bài thực hành
labs/chuong-N/...    đề (de.md) + tiêu chí chấm (checks.json) cho từng bài
```

## Cài đặt
```
pip install -r requirements.txt     # securedypkt
```

## Trang web
Mở `index.html` bằng trình duyệt (hoặc deploy GitHub Pages/Vercel, đều là file tĩnh).
- **Bài lab**: danh sách theo chương, mỗi bài có checklist từng bước. Tick lưu trong `localStorage` của trình duyệt; menu *Dữ liệu* để xuất/nhập sang máy khác.
- Mỗi bước kèm sẵn lệnh `check.py ... --step N` để chép. Ô *Tên file .pkt* nhận `{n}` (vd `bai-b{n}.pkt`).
- **Tra lệnh**: tìm trong `cheatsheets/*.md` và các `loi-hay-gap.md`, gõ không dấu cũng được, phím `/` nhảy vào ô tìm.
- Trang **không chấm được `.pkt`** (cần Python và `securedypkt`), chỉ gắn lệnh để chạy ở máy bạn.

Dữ liệu được nhúng vào `index.html` (hosting tĩnh không liệt kê được thư mục, mở bằng `file://` thì `fetch` bị chặn). Sau khi thêm hoặc sửa `de.md`, `checks.json`, cheatsheet, lỗi hay gặp:
```
python tools/build_web.py           # ghi lại khối dữ liệu trong index.html
python tools/build_web.py --check   # chỉ kiểm tra có khớp không
```
Tiêu đề từng bước lấy từ `de.md`, nhận ba kiểu: `## Bước N - tiêu đề`, `**Bước N.** nội dung`, hoặc danh sách `1. nội dung` dưới mục có chữ "bước". `tests/test_web.py` báo nếu một bước không tách được.

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
`from`/`to` là khoảng bước áp dụng (mặc định mọi bước). Tên `device` là **tên hiển thị** trong Packet Tracer. Xong chạy `python tools/build_web.py` để bài mới hiện trên web.

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
| `device` | device, (model: `PC-PT`, `Laptop-PT`, `Server-PT`, `2960-24TT`, `2811`, `Linksys-WRT300N`...) |
| `gateway` | device, (ipv4), (ipv6): default gateway của thiết bị đầu cuối |
| `ip_in` | device, network (ví dụ `211.13.45.0/24`): thiết bị có IPv4 thuộc mạng đó (hợp với địa chỉ cấp qua DHCP) |
| `dhcp_pool` | device, (name), (network, mask, default_router, dns_server) hoặc (ref, dns_device): DHCPv4 pool trên **router**; bỏ `name` thì pool nào thỏa cũng được; `ref` (`R-UTC:Fa1/0`) lấy mạng và gateway từ cổng; `dns_device` yêu cầu dns-server là IPv4 của thiết bị đó |
| `dhcp_excluded` | device, start, (end), hoặc ref, from_offset, to_offset: `ip dhcp excluded-address`, kiểu thứ hai tính từ địa chỉ mạng của cổng `ref` |
| `dhcp6_pool` | device, (name), (dns_server), (dns_device): `ipv6 dhcp pool` trên router |
| `port_line` | device, port, line: cổng có đúng dòng cấu hình đó (vd `ip helper-address 55.14.92.5`) |
| `dhcp_server_pool` | device, name, (gateway, dns, start, mask, max_users): pool DHCPv4 trên **máy chủ** |
| `xml_value` | device, path, equals, label: giá trị một thẻ trong cấu hình thiết bị (vd `DNS_SERVER/ENABLED` = 1) |
| `xml_has` | device, (path), contains, label: dữ liệu dịch vụ có chứa các chuỗi (không phân biệt hoa thường) |
| `port_net` | device, (port), (v4_prefix, v4_in, v4_offset, v6_prefix, v6_in, v6_offset): cổng (hoặc một cổng bất kỳ nếu bỏ `port`) có prefix, nằm trong dải, và là địa chỉ thứ `+n` của mạng |
| `host_offset` | device, ref (`R-UTC:Fa1/0`), offset, (v4: false), (v6: false): địa chỉ máy = địa chỉ mạng của cổng `ref` + `offset` (kiểu `.+3; ::+3` của đề) |
| `no_overlap` | label, và ports (danh sách `thiết bị:cổng`) hoặc device/devices, (shared: các cặp cổng được dùng chung một mạng): các mạng không chồng lấn |
| `trunk_has` | device, vlans: có ít nhất một cổng trunk cho phép các VLAN đó |
| `reach` | device, dest hoặc (dest_ref, ver 4/6; `dest_ref` là địa chỉ của cổng `thiết bị:cổng`): mô phỏng đi theo bảng định tuyến từ router này tới `dest` |

`from`, `to` là khoảng bước nên **không dùng làm tên tham số** của loại kiểm tra (vì vậy `reach` dùng `dest`). `ip`/`ipv6` nhận `mask: null`/`prefix: null` nếu không cần xét độ dài mask.

`reach` đi theo mạng nối trực tiếp (cổng đang bật), tuyến tĩnh và tuyến mặc định, theo next-hop; với IPv6 mỗi router chuyển tiếp phải có `ipv6 unicast-routing`. Nó báo router nào thiếu tuyến, next-hop sai, cổng tắt hoặc vòng lặp. Vì chấm theo kết quả đường đi nên tĩnh hay mặc định đều được.

## Giới hạn đã biết
- **Chương 6 là bài thiết kế**, nên bộ chấm kiểm tra quan hệ (prefix, dải, vị trí máy, không chồng lấn, định tuyến thông) chứ không so địa chỉ cố định. Tên thiết bị server/laptop của thực hành 02 và cổng router ở bước 5 và 6 là giả định theo bảng của đề thi thử (ghi ở đầu `de.md`). Đã mô phỏng một mạng đúng cho thi thử (113/113) và các lỗi điển hình, nhưng chưa thử trên file `.pkt` chương 6 thật.
- **Dịch vụ máy chủ (chương 5).** Đã đối chiếu tên thẻ với một file `.pkt` thật (cờ bật/tắt DNS, HTTP, HTTPS, SMTP, POP3, DNS client, email client, pool DHCP mặc định). **Chưa thấy** file có bản ghi DNS, tài khoản mail hay DHCPv6 pool thật, nên các mục đó chấm theo *chuỗi* (`xml_has`): biết có tên và địa chỉ nhưng không phân biệt A/AAAA/NS hay đúng tài khoản nào. Có file bài làm chương 5 thì chạy `--dump` rồi báo lại để chấm chính xác hơn.
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

`index.html` chứa nguyên văn các `de.md` (viết lại từ slide của trường). Nếu deploy công khai thì xem lại phần này; GitHub Pages cho repo private cần gói trả phí, còn Vercel (như MMT-Quiz) deploy được repo private ở gói miễn phí.
