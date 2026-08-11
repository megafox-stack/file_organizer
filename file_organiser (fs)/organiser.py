
import os
import shutil 

# File type definitions for categorization
CODE_FILES = {
    "Python": [".py"],
    "JavaScript": [".js"],
    "Java": [".java"],
    "Cpp": [".cpp", ".h", ".hpp", ".c"],
    "Web": {
        "HTML": [".html", ".htm"],
        "CSS": [".css"]
    }
}

REGULAR_FILES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Videos": [".mp4", ".mkv", ".avi"],
    "Documents": [".pdf", ".txt", ".docx"],
    "Archives": [".zip", ".rar"]
}


def get_file_category(file_path):
    """
    Determine the category of a file.
    
    Returns:
        tuple: (category_type, category_name, sub_category)
               category_type: "code", "regular", or None
               category_name: folder name (e.g., "Python", "Images")
               sub_category: subfolder name for code web files (e.g., "HTML", "CSS"), or None
    """
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()
    
    # Check if it's a code file (priority check to avoid Documents mislabeling)
    for lang, exts in CODE_FILES.items():
        if isinstance(exts, list):
            if extension in exts:
                return ("code", lang, None)
        elif isinstance(exts, dict):  # Nested dict for Web subfolders
            for sub_lang, sub_exts in exts.items():
                if extension in sub_exts:
                    return ("code", "Web", sub_lang)
    
    # Check if it's a regular file
    for category, exts in REGULAR_FILES.items():
        if extension in exts:
            return ("regular", category, None)
    
    # Unknown file type
    return (None, "Others", None)


def organize_code_file(file_path, folder_path, language, sub_category=None, dry_run=False):
    """
    Organize a code file into Code/Language/ or Code/Language/SubLanguage/
    
    Args:
        file_path: Full path to the file
        folder_path: Root folder where Code/ will be created
        language: Language subfolder name (Python, JavaScript, etc.)
        sub_category: Optional sub-category (HTML, CSS, etc.)
        dry_run: If True, don't actually move the file (default: False)
    
    Returns:
        tuple: (success, message, src_path, dest_path)
               success: Boolean indicating if file was moved
               message: Status message
               src_path: Original file path (None if skipped/failed)
               dest_path: Destination file path (None if skipped/failed)
    """
    filename = os.path.basename(file_path)
    
    # Build target path
    if sub_category:
        target_folder = os.path.join(folder_path, "Code", language, sub_category)
    else:
        target_folder = os.path.join(folder_path, "Code", language)
    
    if not dry_run:
        os.makedirs(target_folder, exist_ok=True)
    
    destination = os.path.join(target_folder, filename)
    
    # Check for existing file
    if os.path.exists(destination):
        return False, f"SKIPPED (already exists): {filename}", None, None
    
    # Move the file (only if not in dry run mode)
    if not dry_run:
        shutil.move(file_path, destination)
    
    # Build display path
    if sub_category:
        display_path = f"Code/{language}/{sub_category}/"
    else:
        display_path = f"Code/{language}/"
    
    return True, f"MOVED: {filename} → {display_path}", file_path, destination


def organize_regular_file(file_path, folder_path, category, detect_duplicates=True, auto_rename=False, dry_run=False):
    """
    Organize a regular file (images, videos, documents, etc.)
    
    Args:
        file_path: Full path to the file
        folder_path: Root folder where category folder will be created
        category: Category name (Images, Videos, etc.)
        detect_duplicates: Whether to move duplicates to Duplicates/ folder
        auto_rename: Whether to auto-rename files (future feature)
        dry_run: If True, don't actually move the file
    
    Returns:
        tuple: (success, message, src_path, dest_path)
               success: Boolean indicating if file was moved
               message: Status message
               src_path: Original file path (None if skipped/failed)
               dest_path: Destination file path (None if skipped/failed)
    """
    filename = os.path.basename(file_path)
    target_folder = os.path.join(folder_path, category)
    
    if not dry_run:
        os.makedirs(target_folder, exist_ok=True)
    
    destination = os.path.join(target_folder, filename)
    
    # Check for existing file
    if os.path.exists(destination):
        if detect_duplicates and not dry_run:
            # Move to Duplicates folder
            dup_folder = os.path.join(folder_path, "Duplicates")
            os.makedirs(dup_folder, exist_ok=True)
            dup_destination = os.path.join(dup_folder, filename)
            
            # Handle duplicates in duplicates folder
            if os.path.exists(dup_destination):
                base, ext = os.path.splitext(filename)
                counter = 1
                dup_destination = os.path.join(dup_folder, f"{base}_{counter}{ext}")
                while os.path.exists(dup_destination):
                    counter += 1
                    dup_destination = os.path.join(dup_folder, f"{base}_{counter}{ext}")
            
            shutil.move(file_path, dup_destination)
            return True, f"DUPLICATE: {filename} → Duplicates/", file_path, dup_destination
        else:
            return False, f"SKIPPED (already exists): {filename}", None, None
    
    # Move the file
    if not dry_run:
        shutil.move(file_path, destination)
    
    return True, f"MOVED: {filename} → {category}/", file_path, destination


def organise_files(folder_path, detect_duplicates=True, auto_rename=False, dry_run=False):
    """
    Organize all files in a folder by type (code and regular files).
    Uses intelligent categorization to separate code files from regular files.
    
    Args:
        folder_path: Path to the folder to organize
        detect_duplicates: Enable duplicate detection (default: True)
        auto_rename: Enable auto-rename feature (default: False)
        dry_run: Preview changes without moving files (default: False)
    
    Returns:
        tuple: (stats, move_history)
               stats: Dictionary with statistics about the organization process
               move_history: List of tuples (src_path, dest_path) for each successful move
    """
    
    if not os.path.exists(folder_path):
        print("ERROR: Folder path does not exist")
        exit()
    
    files = os.listdir(folder_path)
    
    # Statistics tracking
    stats = {
        'total': 0,
        'code_files': 0,
        'regular_files': 0,
        'duplicates': 0,
        'skipped': 0,
        'moved': 0
    }
    
    # Track all moves for undo functionality
    move_history = []
    
    for file in files:
        file_path = os.path.join(folder_path, file)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue
        
        stats['total'] += 1
        
        # Determine file category
        category_type, category_name, sub_category = get_file_category(file_path)
        
        # Handle code files
        if category_type == "code":
            success, message, src, dest = organize_code_file(file_path, folder_path, category_name, sub_category, dry_run)
            stats['code_files'] += 1
            if success:
                stats['moved'] += 1
                if src and dest and not dry_run:
                    move_history.append((src, dest))
            else:
                stats['skipped'] += 1
            print(message)
        
        # Handle regular files
        elif category_type == "regular":
            success, message, src, dest = organize_regular_file(
                file_path, folder_path, category_name, 
                detect_duplicates, auto_rename, dry_run
            )
            stats['regular_files'] += 1
            if success:
                stats['moved'] += 1
                if src and dest and not dry_run:
                    move_history.append((src, dest))
                if "DUPLICATE" in message:
                    stats['duplicates'] += 1
            else:
                stats['skipped'] += 1
            print(message)
        
        # Handle unknown file types
        else:
            print(f"NO CATEGORY: {file}")
            stats['skipped'] += 1
    
    return stats, move_history


def undo_organization(move_history):
    """
    Undo the last organization by reversing all file moves.
    
    Args:
        move_history: List of tuples (src_path, dest_path) from organize_files()
    
    Returns:
        dict: Statistics about the undo operation
    """
    if not move_history:
        return {'undone': 0, 'errors': 0, 'message': "No moves to undo"}
    
    stats = {'undone': 0, 'errors': 0}
    
    # Reverse the moves in reverse order (last move first)
    for src_path, dest_path in reversed(move_history):
        try:
            # Check if destination file still exists
            if os.path.exists(dest_path):
                # Create source directory if it doesn't exist
                src_dir = os.path.dirname(src_path)
                os.makedirs(src_dir, exist_ok=True)
                
                # Move file back to original location
                shutil.move(dest_path, src_path)
                stats['undone'] += 1
                print(f"UNDONE: {os.path.basename(dest_path)} ← {os.path.basename(src_path)}")
            else:
                print(f"SKIPPED: {dest_path} - file not found")
                stats['errors'] += 1
        except Exception as e:
            print(f"ERROR: Failed to undo {dest_path}: {str(e)}")
            stats['errors'] += 1
    
    return stats


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        folder_path = input("Enter the folder path: ").strip().strip('"')

    stats, move_history = organise_files(folder_path)
    print("\n" + "=" * 50)
    print("✅ FILE ORGANIZATION COMPLETED!")
    print("=" * 50)
    print(f"Total files processed: {stats['total']}")
    print(f"Code files organized: {stats['code_files']}")
    print(f"Regular files organized: {stats['regular_files']}")
    print(f"Duplicates found: {stats['duplicates']}")
    print(f"Files skipped: {stats['skipped']}")
    print(f"Files moved: {stats['moved']}")

