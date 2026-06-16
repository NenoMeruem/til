#!/usr/bin/env python3
"""
gdrive_sync.py
This script syncs project markdown files and image files to Google Drive, 
replaces local image paths with direct Google Drive CDN URLs, and removes 
original local images to optimize repository size.
"""

import os
import sys
import re
import json
import argparse
import urllib.parse
from datetime import datetime, timezone
from dotenv import load_dotenv

# Try to import Google API libraries.
try:
    from google.oauth2 import service_account
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
except ImportError:
    print("Error: Missing required libraries. Please run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

# Regex for wiki links: ![[filename.png]] or ![[filename.png|300]]
WIKI_IMAGE_RE = re.compile(r'!\[\[([^\]|]+)(?:\|([^\]]*))?\]\]')

# Regex for standard markdown links: ![alt](path)
MD_IMAGE_RE = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')


def get_gdrive_service(creds_path_or_json, token_path_or_json=None):
    """
    Authenticate with Google Drive API.
    Supports:
    1. Google Cloud Service Account JSON.
    2. Google OAuth 2.0 Client credentials (if JSON has 'installed' or 'web' section).
    """
    scopes = ['https://www.googleapis.com/auth/drive']
    
    # 1. Parse credentials JSON
    try:
        if os.path.exists(creds_path_or_json):
            with open(creds_path_or_json, 'r') as f:
                creds_data = json.load(f)
        else:
            creds_data = json.loads(creds_path_or_json)
    except Exception as e:
        raise ValueError(f"Failed to parse credentials JSON: {e}")
        
    # Check if it is a Service Account key
    if creds_data.get('type') == 'service_account':
        print("Authenticating using Google Cloud Service Account...")
        if os.path.exists(creds_path_or_json):
            creds = service_account.Credentials.from_service_account_file(
                creds_path_or_json, scopes=scopes)
        else:
            creds = service_account.Credentials.from_service_account_info(
                creds_data, scopes=scopes)
        return build('drive', 'v3', credentials=creds)
        
    # Check if it is an OAuth 2.0 Client secrets
    elif 'installed' in creds_data or 'web' in creds_data:
        print("Authenticating using Google OAuth 2.0 User Credentials...")
        creds = None
        
        # Load token if provided
        if token_path_or_json:
            if os.path.exists(token_path_or_json):
                creds = Credentials.from_authorized_user_file(token_path_or_json, scopes)
            else:
                try:
                    token_data = json.loads(token_path_or_json)
                    creds = Credentials.from_authorized_user_info(token_data, scopes)
                except json.JSONDecodeError:
                    pass
                    
        # If token is invalid/expired, refresh or prompt browser authentication
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
            else:
                from google_auth_oauthlib.flow import InstalledAppFlow
                if os.path.exists(creds_path_or_json):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        creds_path_or_json, scopes)
                else:
                    flow = InstalledAppFlow.from_client_config(
                        creds_data, scopes)
                # Run local server to authenticate
                creds = flow.run_local_server(port=0)
                
                # Save token file to token.json locally
                with open("token.json", "w") as token_file:
                    token_file.write(creds.to_json())
                print("New OAuth token has been saved to token.json. You should add this file's content to your secrets.")
                
        return build('drive', 'v3', credentials=creds)
    else:
        raise ValueError("Unknown credentials JSON format. Must be a Service Account key or OAuth Client Secrets file.")


def get_or_create_gdrive_folder(service, name, parent_id):
    """
    Find a folder by name under the specified parent. Create it if it doesn't exist.
    """
    escaped_name = name.replace("'", "\\'")
    query = f"name = '{escaped_name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
    items = results.get('files', [])
    
    if items:
        return items[0]['id']
        
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')


def is_subpath(path, parent):
    """
    Return True if path is a child or matches the parent directory path.
    """
    abs_path = os.path.abspath(path)
    abs_parent = os.path.abspath(parent)
    return abs_path.startswith(abs_parent + os.sep) or abs_path == abs_parent


def find_file_in_dir(directory, filename):
    """
    Recursively search for a file by name inside a directory.
    """
    for root, dirs, files in os.walk(directory):
        if filename in files:
            return os.path.join(root, filename)
    return None


def find_or_upload_image(service, image_name, local_image_path, backup_folder_id, dry_run=False):
    """
    Check if the image is already in the GDrive backup folder. If not, upload it.
    Returns the Google Drive direct view URL and the GDrive File ID.
    """
    if dry_run:
        print(f"  [Dry-run] Would check and upload image '{image_name}' to backup folder")
        return "https://lh3.googleusercontent.com/d/DRY_RUN_PLACEHOLDER_ID", "DRY_RUN_PLACEHOLDER_ID"
        
    # Search for an existing file with the same name in the backup folder
    escaped_name = image_name.replace("'", "\\'")
    query = f"name = '{escaped_name}' and '{backup_folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
    items = results.get('files', [])
    
    if items:
        file_id = items[0]['id']
        print(f"  [Found on GDrive] Image '{image_name}' already backed up (ID: {file_id})")
        return f"https://lh3.googleusercontent.com/d/{file_id}", file_id
        
    print(f"  [Uploading] Image '{image_name}' to backup folder...")
    file_metadata = {
        'name': image_name,
        'parents': [backup_folder_id]
    }
    media = MediaFileUpload(local_image_path, resumable=True)
    file_obj = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file_obj.get('id')
    
    # Grant anyone read access to enable public hotlinking
    permission = {
        'role': 'reader',
        'type': 'anyone'
    }
    service.permissions().create(fileId=file_id, body=permission).execute()
    print(f"  [Success] Image '{image_name}' uploaded and made public (ID: {file_id})")
    
    return f"https://lh3.googleusercontent.com/d/{file_id}", file_id


def process_markdown_file(service, md_path, docs_dir, images_dir, backup_folder_id, upload_cache, files_to_delete, dry_run=False):
    """
    Scans a markdown file for images, uploads them, and replaces their relative/wiki links with GDrive URLs.
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    modified = False
    
    def process_image(local_img_path):
        local_img_path = os.path.abspath(local_img_path)
        if not is_subpath(local_img_path, images_dir):
            return None
        if not os.path.exists(local_img_path):
            return None
            
        img_name = os.path.basename(local_img_path)
        
        # Check in-memory cache to avoid duplicate processing in the same run
        if local_img_path in upload_cache:
            return upload_cache[local_img_path]
            
        gdrive_url, file_id = find_or_upload_image(service, img_name, local_img_path, backup_folder_id, dry_run)
        
        upload_cache[local_img_path] = gdrive_url
        files_to_delete.add(local_img_path)
        return gdrive_url

    # 1. Wiki Links replacement
    def repl_wiki(match):
        nonlocal modified
        img_name = match.group(1).strip()
        attrs = match.group(2)
        
        resolved_path = find_file_in_dir(images_dir, img_name)
        if resolved_path:
            gdrive_url = process_image(resolved_path)
            if gdrive_url:
                modified = True
                alt_text = img_name
                if attrs:
                    alt_text = f"{img_name}|{attrs.strip()}"
                return f"![{alt_text}]({gdrive_url})"
        return match.group(0)

    # 2. Standard Markdown links replacement
    def repl_md(match):
        nonlocal modified
        alt_text = match.group(1)
        img_path_raw = match.group(2).strip()
        
        if img_path_raw.startswith(('http://', 'https://', 'data:')):
            return match.group(0)
            
        img_path = urllib.parse.unquote(img_path_raw)
        md_dir = os.path.dirname(md_path)
        resolved_path = os.path.abspath(os.path.join(md_dir, img_path))
        
        if os.path.exists(resolved_path) and is_subpath(resolved_path, images_dir):
            gdrive_url = process_image(resolved_path)
            if gdrive_url:
                modified = True
                return f"![{alt_text}]({gdrive_url})"
        else:
            # Fallback to searching the images_dir by filename
            img_filename = os.path.basename(img_path)
            resolved_path_fallback = find_file_in_dir(images_dir, img_filename)
            if resolved_path_fallback:
                gdrive_url = process_image(resolved_path_fallback)
                if gdrive_url:
                    modified = True
                    return f"![{alt_text}]({gdrive_url})"
                    
        return match.group(0)

    # Perform substitutions
    content, count_wiki = WIKI_IMAGE_RE.subn(repl_wiki, content)
    content, count_md = MD_IMAGE_RE.subn(repl_md, content)
    
    if (count_wiki > 0 or count_md > 0) and modified:
        if not dry_run:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(content)
        return True
        
    return False


def verify_uploads(service, upload_cache):
    """
    Verify that all uploaded images actually exist and are accessible on Google Drive.
    """
    print("\n[Verifying] Verifying uploaded images on Google Drive...")
    for local_path, gdrive_url in upload_cache.items():
        if "DRY_RUN_PLACEHOLDER_ID" in gdrive_url:
            continue
        # Extract File ID from GDrive URL
        file_id = gdrive_url.split('/')[-1]
        try:
            # Try to fetch file metadata
            meta = service.files().get(fileId=file_id, fields='id, name, trashed').execute()
            if meta.get('trashed', False):
                raise RuntimeError(f"File {meta.get('name')} (ID: {file_id}) is marked as trashed.")
            print(f"  [Verified] GDrive file ID {file_id} is active and verified.")
        except Exception as e:
            raise RuntimeError(f"Verification failed for {local_path} (ID: {file_id}). GDrive returned: {e}")
    print("[Success] All images verified successfully on Google Drive!")
    return True


def parse_gdrive_time(gdrive_time_str):
    t_str = gdrive_time_str.replace('Z', '+00:00')
    return datetime.fromisoformat(t_str)


def upload_or_update_file(service, local_file_path, filename, parent_folder_id, dry_run=False):
    """
    Mirrors a local document/file to Google Drive. Updates the file on Drive 
    if local modification time is newer or sizes differ.
    """
    if dry_run:
        print(f"  [Dry-run] Would upload/update document: '{filename}'")
        return
        
    local_mtime = datetime.fromtimestamp(os.path.getmtime(local_file_path), tz=timezone.utc)
    local_size = os.path.getsize(local_file_path)
    
    # Query if file exists in the specific GDrive folder
    escaped_name = filename.replace("'", "\\'")
    query = f"name = '{escaped_name}' and '{parent_folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, modifiedTime, size)').execute()
    items = results.get('files', [])
    
    file_metadata = {
        'name': filename,
        'parents': [parent_folder_id]
    }
    
    if items:
        file_id = items[0]['id']
        remote_mtime_str = items[0].get('modifiedTime')
        remote_size = int(items[0].get('size', 0))
        
        should_update = False
        if remote_mtime_str:
            remote_mtime = parse_gdrive_time(remote_mtime_str)
            # Compare with timezone-aware datetime. Check size & modification diff > 2 seconds
            if (local_mtime - remote_mtime).total_seconds() > 2 or local_size != remote_size:
                should_update = True
        else:
            should_update = True
            
        if should_update:
            if dry_run:
                print(f"  [Dry-run] Would update document: '{filename}' (ID: {file_id})")
            else:
                print(f"  [Updating] Document: '{filename}'...")
                media = MediaFileUpload(local_file_path, resumable=True)
                service.files().update(fileId=file_id, media_body=media).execute()
        # else:
        #     print(f"  [Skip] '{filename}' is up to date")
    else:
        if dry_run:
            print(f"  [Dry-run] Would upload new document: '{filename}'")
        else:
            print(f"  [Uploading] New document: '{filename}'...")
            media = MediaFileUpload(local_file_path, resumable=True)
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()


def sync_docs_to_gdrive(service, docs_dir, images_dir, root_gdrive_folder_id, dry_run=False):
    """
    Recursively mirrors all documents and folders from local DOCS_DIR to Google Drive.
    Skips the IMAGES_DIR folder completely.
    """
    print(f"\n[Mirroring] Syncing directories & documents from '{docs_dir}' to Google Drive folder...")
    gdrive_folders = {'.': root_gdrive_folder_id}
    
    for dirpath, dirnames, filenames in os.walk(docs_dir):
        # Exclude hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        
        # Skip if directory is inside IMAGES_DIR
        if is_subpath(dirpath, images_dir):
            continue
            
        relative_dirpath = os.path.relpath(dirpath, docs_dir)
        parent_gdrive_id = gdrive_folders.get(relative_dirpath)
        
        # If folder mapping is not found, construct parents recursively
        if not parent_gdrive_id:
            parts = relative_dirpath.split(os.sep)
            curr_rel = ""
            curr_parent_id = root_gdrive_folder_id
            for part in parts:
                if curr_rel == "":
                    curr_rel = part
                else:
                    curr_rel = os.path.join(curr_rel, part)
                if curr_rel not in gdrive_folders:
                    if dry_run:
                        print(f"  [Dry-run] Would create folder '{part}' under parent ID {curr_parent_id}")
                        gdrive_folders[curr_rel] = f"DRY_RUN_FOLDER_{part}"
                    else:
                        curr_parent_id = get_or_create_gdrive_folder(service, part, curr_parent_id)
                        gdrive_folders[curr_rel] = curr_parent_id
                else:
                    curr_parent_id = gdrive_folders[curr_rel]
            parent_gdrive_id = curr_parent_id

        # Pre-resolve subdirectories, excluding IMAGES_DIR
        for sub_dir in list(dirnames):
            sub_path = os.path.join(dirpath, sub_dir)
            if is_subpath(sub_path, images_dir):
                dirnames.remove(sub_dir)
                continue
            relative_sub = os.path.relpath(sub_path, docs_dir)
            if relative_sub not in gdrive_folders:
                if dry_run:
                    gdrive_folders[relative_sub] = f"DRY_RUN_FOLDER_{sub_dir}"
                else:
                    gdrive_folders[relative_sub] = get_or_create_gdrive_folder(service, sub_dir, parent_gdrive_id)

        # Upload files
        for filename in filenames:
            if filename.startswith('.'):
                continue
            file_path = os.path.join(dirpath, filename)
            
            # Skip images directory
            if is_subpath(file_path, images_dir):
                continue
                
            # Skip python venv, git, credentials.json, token.json
            if any(part in file_path.split(os.sep) for part in ['.venv', '.git', '__pycache__']) or filename in ['.env', 'credentials.json', 'token.json']:
                continue
                
            upload_or_update_file(service, file_path, filename, parent_gdrive_id, dry_run)


def main():
    parser = argparse.ArgumentParser(
        description="Sync Obsidian Vault Documents and Images to Google Drive, update image links, and release local attachments."
    )
    parser.add_argument("--credentials", help="Google Service Account or OAuth secrets JSON string or file path.")
    parser.add_argument("--token", help="Google OAuth authorized user token JSON string or file path (required for OAuth user mode).")
    parser.add_argument("--folder-id", help="Google Drive Root Folder ID.")
    parser.add_argument("--docs-dir", help="Path to local documents directory to scan and mirror.")
    parser.add_argument("--images-dir", help="Path to local images directory containing files to backup and remove.")
    parser.add_argument("--dry-run", action="store_true", help="Perform scanning and link replacement in memory, showing dry-run logs without modifying any files.")
    
    args = parser.parse_args()
    
    # Load env file if available
    load_dotenv()
    
    creds_json = args.credentials or os.getenv("GDRIVE_SERVICE_ACCOUNT_KEY")
    token_json = args.token or os.getenv("GDRIVE_TOKEN_JSON") or os.getenv("GDRIVE_TOKEN_PATH") or "token.json"
    gdrive_folder_id = args.folder_id or os.getenv("GDRIVE_FOLDER_ID")
    docs_dir = args.docs_dir or os.getenv("DOCS_DIR")
    images_dir = args.images_dir or os.getenv("IMAGES_DIR")
    
    # Validations
    if not creds_json:
        print("Error: Missing credentials. Provide --credentials or set GDRIVE_SERVICE_ACCOUNT_KEY.")
        sys.exit(1)
    if not gdrive_folder_id:
        print("Error: Missing target folder ID. Provide --folder-id or set GDRIVE_FOLDER_ID.")
        sys.exit(1)
    if not docs_dir:
        print("Error: Missing documents scan directory. Provide --docs-dir or set DOCS_DIR.")
        sys.exit(1)
    if not images_dir:
        print("Error: Missing images attachment directory. Provide --images-dir or set IMAGES_DIR.")
        sys.exit(1)
        
    docs_dir = os.path.abspath(docs_dir)
    images_dir = os.path.abspath(images_dir)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, ".."))
    
    if not os.path.exists(docs_dir):
        print(f"Error: Documents directory '{docs_dir}' does not exist.")
        sys.exit(1)
    if not os.path.exists(images_dir):
        print(f"Error: Images directory '{images_dir}' does not exist.")
        sys.exit(1)

    print("==========================================================")
    print("                Google Drive Sync Script                  ")
    print(f"  Repo Root:     {repo_root}")
    print(f"  Docs Scan Dir: {docs_dir}")
    print(f"  Images Dir:    {images_dir}")
    print(f"  GDrive Root:   {gdrive_folder_id}")
    print(f"  Dry-run Mode:  {args.dry_run}")
    print("==========================================================")

    # Initialize client
    try:
        service = get_gdrive_service(creds_json, token_json)
    except Exception as e:
        print(f"Authentication Error: Failed to initialize Google Drive client: {e}")
        sys.exit(1)

    # Create backup folder under root GDrive folder
    if args.dry_run:
        print("[Dry-run] Would verify or create 'backup' folder in Google Drive")
        backup_folder_id = "DRY_RUN_BACKUP_FOLDER_ID"
    else:
        try:
            backup_folder_id = get_or_create_gdrive_folder(service, "backup", gdrive_folder_id)
            print(f"Images will be backed up to GDrive folder 'backup' (ID: {backup_folder_id})")
        except Exception as e:
            print(f"Error: Failed to create or access Google Drive 'backup' folder: {e}")
            sys.exit(1)

    upload_cache = {} # Maps local_img_path -> GDrive direct URL
    files_to_delete = set() # Set of local image absolute paths successfully sync'd
    md_files_updated = 0

    # 1. Scan and replace image links in markdown files
    print("\n[Scanning] Finding and updating image references in documents...")
    for root, dirs, files in os.walk(docs_dir):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        if is_subpath(root, images_dir):
            continue
            
        for file in files:
            if file.endswith('.md'):
                md_path = os.path.join(root, file)
                try:
                    updated = process_markdown_file(
                        service, md_path, docs_dir, images_dir, 
                        backup_folder_id, upload_cache, files_to_delete, args.dry_run
                    )
                    if updated:
                        md_files_updated += 1
                        print(f"  Updated image links in: {os.path.relpath(md_path, docs_dir)}")
                except Exception as e:
                    print(f"  Error processing {file}: {e}")
                    sys.exit(1)

    print(f"\nScan completed. Updated links in {md_files_updated} markdown files.")
    print(f"Total local images queued for sync: {len(files_to_delete)}")

    if not files_to_delete:
        print("No new local images found in docs. Proceeding to document mirror...")
    else:
        # 2. Verification Step
        if not args.dry_run:
            try:
                verify_uploads(service, upload_cache)
            except Exception as e:
                print(f"\nVerification Failed: {e}")
                print("Skipping cleanup phase to prevent data loss. Please check connection.")
                sys.exit(1)

        # 3. Cleanup Step (Only runs if verification succeeded or in dry-run)
        print(f"\n[Cleanup] Removing local image files from '{images_dir}'...")
        total_saved_bytes = 0
        for local_file in files_to_delete:
            if os.path.exists(local_file):
                file_size = os.path.getsize(local_file)
                total_saved_bytes += file_size
                if args.dry_run:
                    print(f"  [Dry-run] Would delete local image: {os.path.relpath(local_file, images_dir)}")
                else:
                    try:
                        os.remove(local_file)
                        print(f"  [Deleted] Local image: {os.path.relpath(local_file, images_dir)}")
                    except Exception as e:
                        print(f"  [Warning] Failed to delete {local_file}: {e}")
                        
        saved_kb = total_saved_bytes / 1024
        print(f"Cleanup finished. Saved {saved_kb:.2f} KB of local space.")

    # 4. Sync documents tree (Mirror documents to Google Drive)
    try:
        sync_docs_to_gdrive(service, repo_root, images_dir, gdrive_folder_id, args.dry_run)
    except Exception as e:
        print(f"\nMirroring Failed: Failed to mirror documents to Google Drive: {e}")
        sys.exit(1)

    print("\n==========================================================")
    print("                  Sync Process Completed!                 ")
    print("==========================================================")


if __name__ == "__main__":
    main()
