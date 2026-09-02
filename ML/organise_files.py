import shutil
from pathlib import Path
 
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
 
# directories that should live under data/
DATA_SUBDIRS = ["archive_cleaned", "converted_operators"]
 
# file prefixes that should live under data/ (matched with glob)
DATA_FILE_PATTERNS = ["combined_dataset_*.npy"]
 
# file prefixes that should live under models/ (matched with glob)
MODEL_FILE_PATTERNS = ["trained_model_*.npy"]
 
 
def ensure_dir(path: Path):
    if not path.exists():
        path.mkdir(parents=True)
        print(f"created folder: {path.relative_to(PROJECT_ROOT)}")
 
 
def move_item(source: Path, destination_dir: Path):
    destination = destination_dir / source.name
    if destination.exists():
        print(f"skipped (already moved): {source.name}")
        return
    shutil.move(str(source), str(destination))
    print(f"moved: {source.name} -> {destination_dir.relative_to(PROJECT_ROOT)}/")
 
 
def main():
    ensure_dir(DATA_DIR)
    ensure_dir(MODELS_DIR)
 
    # move data subdirectories
    for subdir_name in DATA_SUBDIRS:
        source = PROJECT_ROOT / subdir_name
        if source.exists() and source.is_dir():
            move_item(source, DATA_DIR)
        else:
            print(f"not found, skipping: {subdir_name}")
 
    # move data files
    for pattern in DATA_FILE_PATTERNS:
        for file in PROJECT_ROOT.glob(pattern):
            move_item(file, DATA_DIR)
 
    # move model files
    for pattern in MODEL_FILE_PATTERNS:
        for file in PROJECT_ROOT.glob(pattern):
            move_item(file, MODELS_DIR)
 
    print("\ndone.")
 
 
if __name__ == "__main__":
    main()
