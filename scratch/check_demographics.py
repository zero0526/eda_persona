import sys
import os
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')
from loaders.action_loader import ActionLoader
loader = ActionLoader()
profiles, _ = loader.load_persona_profiles_and_contracts()
for pid in sorted(profiles.keys()):
    p = profiles[pid]
    a = p['attributes']
    print(f"{pid}:")
    print(f"  Tuổi: {a.get('Nhóm tuổi')}, Giới tính: {a.get('Giới tính sinh học')}, Tỉnh/TP: {a.get('Tỉnh / Thành phố')}")
    print(f"  Công việc: {a.get('Nhóm vai trò công việc hiện tại.')} - Lĩnh vực: {a.get('Lĩnh vực của công việc chính hiện tại. Phân loại theo nhóm ngành kinh tế.')}")
    print(f"  Gia đình: {a.get('Tình trạng quan hệ tình cảm hoặc hôn nhân hiện tại')}, Con: {a.get('Số con')}")
    print(f"  Tương tác MXH: {a.get('Cách thường tham gia và tương tác trên các nền tảng trực tuyến.')}")
