"""Data loader cho Facebook Persona.

Cung cấp class PersonaDataLoader để đọc và bóc tách dữ liệu từ file JSON gốc:
- persona_ids: Danh sách mã định danh của các Persona (e.g. vn_000019, vn_000041,...).
- origin_personas: Danh sách thuộc tính gốc (persona attributes).
- fb_personas: Danh sách hồ sơ hành vi Facebook (facebook_behavior_profile: communication, facebookBehavior, interests,...).
- Chuyển đổi linh hoạt sang pandas DataFrame phục vụ phân tích EDA và thống kê.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Dict, Iterator, List, Optional, Union
import pandas as pd

# Đảm bảo in Unicode tiếng Việt mượt mà trên console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


class PersonaDataLoader:
    """Class quản lý việc nạp và xử lý dữ liệu Persona từ file JSON gốc."""

    def __init__(
        self,
        file_path: Optional[Union[str, Path]] = None,
        auto_load: bool = True,
    ) -> None:
        """Khởi tạo DataLoader.

        Parameters
        ----------
        file_path : Optional[Union[str, Path]], optional
            Đường dẫn đến file JSON persona. Nếu để trống (None), tự động tìm
            'data/original_facebook_persona.json'.
        auto_load : bool, default=True
            Nếu True, tự động gọi self.load() để nạp dữ liệu ngay khi khởi tạo instance.
        """
        if file_path is None:
            candidates = [
                Path(__file__).resolve().parent / "data" / "original_facebook_persona.json",
                Path.cwd() / "data" / "original_facebook_persona.json",
            ]
            self.file_path = next((p for p in candidates if p.is_file()), candidates[0])
        else:
            self.file_path = Path(file_path)

        self.raw_data: List[Dict[str, Any]] = []
        self.persona_ids: List[str] = []
        self.origin_personas: List[Dict[str, Any]] = []
        self.fb_personas: List[Optional[Dict[str, Any]]] = []
        self.fb_behavior_profiles: List[Optional[Dict[str, Any]]] = []
        self._id_index_map: Dict[str, int] = {}

        if auto_load:
            self.load()

    def load(self, file_path: Optional[Union[str, Path]] = None) -> PersonaDataLoader:
        """Đọc và bóc tách dữ liệu từ file JSON.

        Parameters
        ----------
        file_path : Optional[Union[str, Path]], optional
            Đường dẫn mới nếu muốn nạp file khác với file_path khi khởi tạo.

        Returns
        -------
        PersonaDataLoader
            Trả về chính instance hiện tại để hỗ trợ method chaining.
        """
        target_path = Path(file_path) if file_path is not None else self.file_path
        if not target_path.is_file():
            raise FileNotFoundError(f"Không tìm thấy file persona tại: {target_path.resolve()}")

        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError(f"Dữ liệu JSON phải là một danh sách các records (List[dict]), nhận được: {type(data)}")

        self.raw_data = data
        self.persona_ids = []
        self.origin_personas = []
        self.fb_personas = []
        self.fb_behavior_profiles = []
        self._id_index_map = {}

        for idx, d in enumerate(data):
            if not isinstance(d, dict):
                continue

            p_id = str(d.get("persona_id", f"unknown_{idx}"))
            persona_obj = d.get("persona") or {}
            origin_attrs = persona_obj.get("attributes") or {}
            fb_profile = d.get("facebook_behavior_profile")

            self.persona_ids.append(p_id)
            self.origin_personas.append(origin_attrs)
            self.fb_personas.append(fb_profile)
            self.fb_behavior_profiles.append(fb_profile)
            self._id_index_map[p_id] = idx

        self.file_path = target_path
        return self

    def get_by_id(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """Lấy toàn bộ record thô theo persona_id."""
        idx = self._id_index_map.get(persona_id)
        if idx is not None and 0 <= idx < len(self.raw_data):
            return self.raw_data[idx]
        return None

    def get_origin_attributes(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """Lấy từ điển thuộc tính gốc (attributes) theo persona_id."""
        idx = self._id_index_map.get(persona_id)
        if idx is not None and 0 <= idx < len(self.origin_personas):
            return self.origin_personas[idx]
        return None

    def get_fb_persona(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """Lấy hồ sơ hành vi Facebook (facebook_behavior_profile) theo persona_id."""
        idx = self._id_index_map.get(persona_id)
        if idx is not None and 0 <= idx < len(self.fb_personas):
            return self.fb_personas[idx]
        return None

    def get_fb_contract(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """Alias cho get_fb_persona."""
        return self.get_fb_persona(persona_id)

    def to_origin_dataframe(self, include_id: bool = True) -> pd.DataFrame:
        """Chuyển đổi danh sách thuộc tính gốc (origin_personas) thành pandas DataFrame.

        Parameters
        ----------
        include_id : bool, default=True
            Nếu True, cột 'persona_id' sẽ được thêm vào đầu DataFrame.

        Returns
        -------
        pd.DataFrame
            DataFrame gồm N hàng (mỗi persona 1 hàng) và các cột là các thuộc tính Persona.
        """
        df = pd.DataFrame(self.origin_personas)
        if include_id:
            df.insert(0, "persona_id", self.persona_ids)
        return df

    def to_dataframe(self, include_id: bool = True) -> pd.DataFrame:
        """Alias cho to_origin_dataframe."""
        return self.to_origin_dataframe(include_id=include_id)

    def to_fb_dataframe(
        self, include_id: bool = True, drop_null: bool = False
    ) -> pd.DataFrame:
        """Chuyển đổi danh sách hồ sơ hành vi Facebook (facebook_behavior_profile) thành DataFrame phẳng.

        Làm phẳng các trường:
        - communication: directness, emojiUse, language, register, tone
        - facebookBehavior: interactionStyle, pace, preferredSurface, readingDepth, restStyle
        - interests: avoid, strong (kèm num_avoid, num_strong)

        Parameters
        ----------
        include_id : bool, default=True
            Nếu True, thêm cột 'persona_id'.
        drop_null : bool, default=False
            Nếu True, loại bỏ các persona không có profile (None).

        Returns
        -------
        pd.DataFrame
            DataFrame gồm các biến hành vi Facebook đã làm phẳng.
        """
        rows = []
        for pid, profile in zip(self.persona_ids, self.fb_personas):
            if profile is None:
                if not drop_null:
                    row = {"persona_id": pid} if include_id else {}
                    rows.append(row)
                continue

            row = {"persona_id": pid} if include_id else {}

            # 1. communication (làm phẳng toàn bộ các trường)
            comm = profile.get("communication") or {}
            row["directness"] = comm.get("directness")
            row["emojiUse"] = comm.get("emojiUse")
            row["language"] = comm.get("language")
            row["register"] = comm.get("register")
            row["tone"] = comm.get("tone")

            # 2. facebookBehavior (các trường hành vi chỉ định)
            fb_b = profile.get("facebookBehavior") or {}
            row["discoveryStyle"] = fb_b.get("discoveryStyle")
            row["interactionStyle"] = fb_b.get("interactionStyle")
            row["pace"] = fb_b.get("pace")
            row["preferredSurface"] = fb_b.get("preferredSurface")
            row["readingDepth"] = fb_b.get("readingDepth")
            row["restStyle"] = fb_b.get("restStyle")

            # 3. usage (thói quen truy cập và năng lượng)
            usage = profile.get("usage") or {}
            row["attention"] = usage.get("attention")
            row["energy"] = usage.get("energy")
            row["engagementStyle"] = usage.get("engagementStyle")
            row["facebookFrequency"] = usage.get("facebookFrequency")

            # 4. interests (lấy avoid và strong)
            interests = profile.get("interests") or {}
            avoid_list = interests.get("avoid") or []
            strong_list = interests.get("strong") or []
            row["avoid"] = avoid_list
            row["strong"] = strong_list
            row["num_avoid"] = len(avoid_list)
            row["num_strong"] = len(strong_list)

            rows.append(row)

        return pd.DataFrame(rows)

    def summary(self) -> Dict[str, Any]:
        """Tổng kết nhanh thông tin tập dữ liệu đã nạp."""
        n_profile = sum(1 for p in self.fb_personas if p is not None)
        df_origin = pd.DataFrame(self.origin_personas)

        return {
            "file_path": str(self.file_path),
            "total_records": len(self.persona_ids),
            "total_unique_ids": len(set(self.persona_ids)),
            "total_origin_attributes": df_origin.shape[1] if not df_origin.empty else 0,
            "records_with_facebook_behavior_profile": n_profile,
            "sample_ids": self.persona_ids[:5],
        }

    def __len__(self) -> int:
        return len(self.persona_ids)

    def __getitem__(self, item: Union[int, str]) -> Dict[str, Any]:
        if isinstance(item, int):
            return self.raw_data[item]
        if isinstance(item, str):
            record = self.get_by_id(item)
            if record is None:
                raise KeyError(f"Không tìm thấy persona_id: {item}")
            return record
        raise TypeError(f"Key phải là int hoặc str, nhận được: {type(item)}")

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        return iter(self.raw_data)

    def __repr__(self) -> str:
        return (
            f"PersonaDataLoader(records={len(self.persona_ids)}, "
            f"file='{self.file_path.name}')"
        )


if __name__ == "__main__":
    # Test khởi tạo và nạp dữ liệu
    loader = PersonaDataLoader()
    print("DataLoader:", loader)
    print("Summary:")
    for k, v in loader.summary().items():
        print(f"  • {k}: {v}")

    # Chuyển đổi sang DataFrame
    df = loader.to_origin_dataframe()
    print(f"\nDataFrame shape: {df.shape}")
    print(f"Sample columns (first 10): {list(df.columns[:10])}")
    print("\nSample rows:")
    print(df[["persona_id", "age_bracket", "gender_identity", "province", "monthly_personal_income_band"]])