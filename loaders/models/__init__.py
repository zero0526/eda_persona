"""Mô hình dữ liệu Pydantic đại diện cho toàn bộ các bảng trong SQLite persona-runner.

Tất cả 31 bảng trong SQLite được định nghĩa trong file `table_models.py` duy nhất,
đồng thời các trường JSON phức tạp được bóc tách thành các Sub-Schema con có kiểu rõ ràng.
"""

from .table_models import *
