import sys
import sqlite3
import pandas as pd
import json

sys.stdout.reconfigure(encoding='utf-8')
from loaders.episode_loader import get_sqlite_path

conn = sqlite3.connect(get_sqlite_path())
conn.row_factory = sqlite3.Row

print("=== 1. KIỂM TRA BẢNG BOTS ===")
bots = pd.read_sql_query("SELECT * FROM bots", conn)
print(bots.to_string())

print("\n=== 2. KIỂM TRA TOÀN BỘ CỬA SỔ CỦA vn_fb_001 VÀ vn_fb_002 ===")
windows = pd.read_sql_query("""
    SELECT w.*, b.persona_id, b.status as bot_status
    FROM activity_windows w
    JOIN bots b ON w.bot_id = b.id
    WHERE b.persona_id IN ('vn_fb_001', 'vn_fb_002')
""", conn)
print(windows.to_string())

print("\n=== 3. KIỂM TRA SESSIONS CỦA vn_fb_001 VÀ vn_fb_002 ===")
sessions = pd.read_sql_query("""
    SELECT s.id, s.bot_id, b.persona_id, s.status, s.terminal_reason, s.started_at, s.ended_at, s.total_actions
    FROM agent_sessions s
    JOIN bots b ON s.bot_id = b.id
    WHERE b.persona_id IN ('vn_fb_001', 'vn_fb_002')
""", conn)
print(sessions.to_string())

print("\n=== 4. KIỂM TRA TẤT CẢ SESSIONS TOÀN HỆ THỐNG THEO PERSONA ===")
all_sess = pd.read_sql_query("""
    SELECT b.persona_id, s.status, s.terminal_reason, COUNT(*) as cnt
    FROM agent_sessions s
    JOIN bots b ON s.bot_id = b.id
    GROUP BY b.persona_id, s.status, s.terminal_reason
""", conn)
print(all_sess.to_string())
