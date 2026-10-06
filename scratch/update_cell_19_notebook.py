import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

nb_path = 'notebooks/eda_action_v2.ipynb'
nb = json.load(open(nb_path, 'r', encoding='utf-8'))

cell_19_text = '''### Kết luận Giả thuyết 2 ($H_2$): **ỦNG HỘ MẠNH MẼ (STRONGLY SUPPORTED)**

Các kết quả phân tích định lượng và đối chiếu hồ sơ cho thấy:
1. **Tuân thủ Tuyệt đối Nhịp độ Vật lý (Pacing Fidelity)**: 100% các bước của bot có `scrollCadence = "quick"` (`vn_fb_001`, `002`, `005`) đều thực thi dưới nhãn `gesture_pace = fast`. Ngược lại, 100% các bước của bot có `scrollCadence = "balanced"` (`vn_fb_003`, `004`, `006`) đều thực thi dưới nhãn `careful`. Độ dài thời gian cử chỉ của nhóm `careful` lớn hơn nhóm `fast` có ý nghĩa thống kê cực kỳ cao ($p < 10^{-5}$).
2. **Khắc họa Chính xác Bản sắc Tương tác Xã hội Qua Thang 3 Nấc**:
   - Thang đo 3 nấc (0: Thấp/Không, 1: Vừa, 2: Cao) đồng biến vượt trội với hành vi thực tế: **Share ($r_s = +1.000, p < 0.001$)**, **React ($r_s = +0.926, p = 0.008$)**, và **Comment ($r_s = +0.583$)**.
   - Kiểm định Chi-Square ($\chi^2 = 26.77, df = 8, p = 7.76 \\times 10^{-4} < 0.001$) khẳng định cơ cấu tương tác phụ thuộc chặt chẽ và có ý nghĩa thống kê vào nhóm Social Archetype.
   - Nhóm "Tàu ngầm" (`vn_fb_004`, `vn_fb_006`) dành 87.5% tương tác cho Like, 0 share, đúng tính cách "chỉ xem và like".
   - Nhóm "Chiến thần bình luận dạo" (`vn_fb_003`) thực hiện 7/9 lượt bình luận toàn hệ thống (tỷ lệ 100% trên bài quan sát).
   - Nhóm "Người thích chia sẻ" (`vn_fb_005`) là bot duy nhất thực hiện hành động `share` trên nền tảng.
   - **Phát hiện mâu thuẫn hệ thống:** Tầng `BehavioralContract` gán nhầm nghịch đảo `reactionRate` (Tàu ngầm 0.167, Chiến thần cmt 0.800). Tuy nhiên, LLM ưu tiên bám sát Chân dung định tính (Semantic Persona Archetype) thay vì tham số kỹ thuật thô.
3. **Căn cứ Ngữ cảnh & Tìm kiếm Khớp 100% với Hồ sơ**: Từ khóa tìm kiếm mang tính định danh cao theo địa bàn sinh sống thực tế của nhân vật (Cần Thơ, Đà Nẵng) và thị hiếu chuyên biệt (Bất động sản, Đồ ăn đường phố).
4. **Quy tắc Emoji Tuyệt đối Nghiêm ngặt**: Các bot có `emojiRate = 0` (`vn_fb_005`, `vn_fb_006`) hoàn toàn không chứa bất kỳ emoji nào trong văn bản bình luận.
5. **Cảnh báo Kỹ thuật (Repetition Loop)**: Phát hiện hiện tượng agent phát sinh vòng lặp lặp lại nội dung bình luận giống hệt nhau (lên tới 4-7 lần) khi gặp lỗi tương tác CDP/UI nhưng không nhận thức được trạng thái đã gửi thành công.
'''

nb['cells'][19]['source'] = [line + '\n' for line in cell_19_text.split('\n')][:-1]

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Đã cập nhật thành công Cell 19 trong notebooks/eda_action_v2.ipynb!")
