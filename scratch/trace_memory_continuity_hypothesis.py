import sys
from pathlib import Path
import pandas as pd
from collections import defaultdict

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from loaders.action_loader import ActionLoader

loader = ActionLoader()
all_personas = loader.load_all_personas()

print("=== KIỂM CHỨNG Ý TƯỞNG CỦA USER: TIẾP NỐI CHỦ ĐỀ CŨ VÀ TIẾP TỤC CHỦ ĐỀ MỚI PHÁT SINH ===\n")

for pid in ['vn_fb_001', 'vn_fb_002', 'vn_fb_003', 'vn_fb_004', 'vn_fb_005', 'vn_fb_006']:
    hist = all_personas[pid]
    print(f"********************************************************************")
    print(f"PERSONA: {pid} ({hist.persona_name})")
    print(f"********************************************************************")
    
    for s in hist.sessions:
        wm = s.working_memory
        pm = s.prior_memory
        
        print(f"\n--- Phiên {s.session_order} (ID: {s.session_id[:8]}...) ---")
        
        # Working memory active threads
        if wm and wm.active_threads:
            print("  [Active Threads]:")
            for th in wm.active_threads:
                print(f"    * key='{th.key}' | topic='{th.topic}' | origin='{th.origin}' | state='{th.state}'")
        else:
            print("  [Active Threads]: None")
            
        # Memory deltas (ghi vào bộ nhớ sau phiên)
        if wm and wm.memory_deltas:
            thread_deltas = [d.record_key for d in wm.memory_deltas if d.record_type == 'thread']
            entity_deltas = [d.record_key for d in wm.memory_deltas if d.record_type == 'entity']
            print(f"  [Memory Deltas - Ghi nhớ cuối phiên]: Threads={thread_deltas} | Entities={entity_deltas}")
        else:
            print("  [Memory Deltas]: None")
            
        # Searched topics
        if wm and wm.searched_topics:
            searches = [(st.query, st.purpose) for st in wm.searched_topics]
            print(f"  [Searches]: {searches}")
            
        # Opened sources
        if wm and wm.opened_sources:
            sources = [(op.target[:40] if op.target else '', op.type) for op in wm.opened_sources]
            print(f"  [Opened Sources]: {sources}")

