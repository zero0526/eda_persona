from data_loader import PersonaDataLoader

loader = PersonaDataLoader()
print("=== DATA SUMMARY ===")
for k, v in loader.summary().items():
    print(f"  • {k}: {v}")

df_fb = loader.to_fb_dataframe(drop_null=True)
print(f"\n=== FB BEHAVIOR PROFILE DATAFRAME (Shape: {df_fb.shape}) ===")
print(df_fb[["persona_id", "directness", "emojiUse", "register", "interactionStyle", "pace", "preferredSurface", "readingDepth", "restStyle", "num_avoid", "num_strong"]])
print("\nSample avoid & strong interests for first persona:")
print("  • Avoid (sample 3):", df_fb.loc[0, "avoid"][:3])
print("  • Strong (sample 3):", df_fb.loc[0, "strong"][:3])

