import os
import shutil
import zipfile
import hashlib
import xml.etree.ElementTree as ET

# Configuration
ADDONS_SOURCES = [
    r"C:\Users\conta\AppData\Roaming\Kodi\addons\script.dejavu",
    r"C:\Users\conta\AppData\Roaming\Kodi\addons\repository.dejavu"
]
REPO_DIR = r"C:\Users\conta\AppData\Roaming\Kodi\addons\repository.dejavu"


def create_zip(source_dir, output_zip):
    """Zips the contents of source_dir into output_zip, with a top-level folder of the same name."""
    addon_id = os.path.basename(source_dir)
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                # Skip .git, __pycache__, and our own generation script/zips
                if any(x in root for x in [".git", "__pycache__", ".ipynb_checkpoints"]):
                    continue
                if file in ["generate_repo.py", "addons.xml", "addons.xml.md5"] or file.endswith(".zip"):
                    continue

                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, os.path.join(source_dir, ".."))
                zipf.write(abs_path, rel_path)


def generate_repo():
    print("--- DejaVu Repository Generator ---")
    
    addons_xml_content = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n'
    
    for source in ADDONS_SOURCES:
        if not os.path.exists(source):
            print(f"Warning: Source not found: {source}")
            continue
            
        addon_xml_path = os.path.join(source, "addon.xml")
        if not os.path.exists(addon_xml_path):
            print(f"Warning: No addon.xml in {source}")
            continue
            
        # Parse addon.xml
        tree = ET.parse(addon_xml_path)
        root = tree.getroot()
        addon_id = root.attrib['id']
        version = root.attrib['version']
        
        print(f"Processing {addon_id} v{version}...")
        
        # Create destination folder in repo
        dest_dir = os.path.join(REPO_DIR, addon_id)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            
        # Copy addon.xml to dest
        shutil.copy2(addon_xml_path, os.path.join(dest_dir, "addon.xml"))
        
        # Copy icon/fanart if they exist
        for asset in ["icon.png", "fanart.jpg"]:
            asset_path = os.path.join(source, asset)
            if os.path.exists(asset_path):
                shutil.copy2(asset_path, os.path.join(dest_dir, asset))
        
        # Create ZIP
        zip_name = f"{addon_id}-{version}.zip"
        zip_path = os.path.join(dest_dir, zip_name)
        create_zip(source, zip_path)
        print(f"  Created {zip_name}")
        
        # Add to cumulative addons.xml
        with open(addon_xml_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Skip the XML declaration if present
            if lines[0].startswith('<?xml'):
                lines = lines[1:]
            addons_xml_content += "".join(lines).strip() + "\n\n"

    addons_xml_content += "</addons>\n"
    
    # Write addons.xml
    addons_xml_path = os.path.join(REPO_DIR, "addons.xml")
    with open(addons_xml_path, 'w', encoding='utf-8') as f:
        f.write(addons_xml_content)
    print("Generated addons.xml")
    
    # Generate MD5
    with open(addons_xml_path, 'rb') as f:
        md5_hash = hashlib.md5(f.read()).hexdigest()
        
    with open(addons_xml_path + ".md5", 'w') as f:
        f.write(md5_hash)
    print("Generated addons.xml.md5")
    
    print("--- Done ---")

if __name__ == "__main__":
    generate_repo()
