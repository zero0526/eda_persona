from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent


def deep_merge(source: dict[str, Any], destination: dict[str, Any]) -> dict[str, Any]:
    """Gộp đệ quy source vào destination (source sẽ ghi đè giá trị nếu trùng key)."""
    for key, value in source.items():
        if isinstance(value, dict) and key in destination and isinstance(destination[key], dict):
            destination[key] = deep_merge(value, destination[key])
        else:
            destination[key] = value
    return destination


@dataclass(frozen=True)
class FbActionLogsConfig:
    persona: Path
    without_persona: Path


@dataclass(frozen=True)
class PersonaConfig:
    fb_pf_persona: Path


@dataclass(frozen=True)
class AppConfig:
    fb_action_logs: FbActionLogsConfig
    persona: PersonaConfig

    @classmethod
    def load(
        cls,
        *config_paths: str | Path | Sequence[str | Path],
    ) -> "AppConfig":
        """
        Nạp một hoặc nhiều file cấu hình YAML.
        Các file truyền vào sau sẽ được ưu tiên merge/ghi đè lên file trước.
        """
        # Làm phẳng danh sách đường dẫn truyền vào
        flat_paths: list[Path] = []
        for p in config_paths:
            if isinstance(p, (list, tuple)):
                flat_paths.extend([PROJECT_ROOT / item for item in p])
            else:
                flat_paths.append(PROJECT_ROOT / p)

        merged_data: dict[str, Any] = {}

        for path in flat_paths:
            resolved_file = path.resolve()
            if not resolved_file.is_file():
                raise FileNotFoundError(f"Không tìm thấy file cấu hình tại: {resolved_file}")

            with open(resolved_file, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f) or {}
                # Gộp nội dung file hiện tại vào dữ liệu tổng
                merged_data = deep_merge(content, merged_data)

        root = merged_data.get("root", {})
        fb_logs = root.get("fb-action-logs", {})
        persona = root.get("persona", {})

        def resolve_p(rel_path: str) -> Path:
            if not rel_path:
                return Path()
            return (PROJECT_ROOT / rel_path).resolve()

        return cls(
            fb_action_logs=FbActionLogsConfig(
                persona=resolve_p(fb_logs.get("persona", "")),
                without_persona=resolve_p(fb_logs.get("without-persona", "")),
            ),
            persona=PersonaConfig(
                fb_pf_persona=resolve_p(persona.get("fb-pf-persona", "")),
            ),
        )


# ==========================================
# CÁCH SỬ DỤNG
# ==========================================

# 1. Nạp một file đơn lẻ:
# cfg = AppConfig.load("./configs/paths.yaml")

# 2. Nạp nhiều file riêng lẻ (file sau ghi đè/bổ sung file trước):
cfg = AppConfig.load(
    "./configs/paths.yaml",
    "./configs/thresholds.yaml"
)

# 3. Hoặc truyền dưới dạng một danh sách list/tuple:
# config_files = ["./configs/paths.yaml", "./configs/persona.yaml"]
# cfg = AppConfig.load(config_files)