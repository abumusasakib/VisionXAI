import os
from collections import defaultdict

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}


def is_image_file(filename):
    return os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS


def get_extension(filename):
    return os.path.splitext(filename)[1].lower()


def print_tree(path, prefix="", output_lines=None):
    try:
        items = sorted(os.listdir(path))
    except PermissionError:
        line = prefix + "└── [Permission Denied]"
        output_lines.append(line)
        return

    image_counter = defaultdict(int)
    other_files = []

    for item in items:
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            connector = "└── " if item == items[-1] else "├── "
            line = prefix + connector + item + "/"
            output_lines.append(line)
            new_prefix = prefix + ("    " if item == items[-1] else "│   ")
            print_tree(full_path, new_prefix, output_lines)
        else:
            if is_image_file(item):
                ext = get_extension(item)
                image_counter[ext] += 1
            else:
                connector = "└── " if item == items[-1] else "├── "
                line = prefix + connector + item
                output_lines.append(line)

    if image_counter:
        for ext, count in sorted(image_counter.items()):
            line = prefix + f"[{ext} files: {count}]"
            output_lines.append(line)


def generate_tree_and_save(folder_path, output_filename="directory_tree.md"):
    if not os.path.isdir(folder_path):
        print(f"Invalid folder path: {folder_path}")
        return

    output_lines = []
    output_lines.append(f"# 📁 Directory Tree of `{os.path.basename(folder_path)}`\n")
    output_lines.append(os.path.basename(folder_path) + "/")
    print_tree(folder_path, "", output_lines)

    # Write to .md file
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"\n✅ Directory tree saved to `{output_filename}`")


# Example usage
folder_path = input("Enter the folder path to scan: ").strip()
generate_tree_and_save(folder_path)
