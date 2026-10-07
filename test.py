from loaders.action_loader import ActionLoader
from dotenv import load_dotenv

import os
load_dotenv()

loader= ActionLoader(os.getenv('SQLITE_PATH'))

import json

session = loader.load_session('3bd87615-0c11-4ade-897a-8aac32829ef0')



with open('memories.json', 'w', encoding='utf-8') as f:
    json.dump(session.model_dump(), f, indent=2, ensure_ascii=False)

print("Saved memories to memories.json successfully!")