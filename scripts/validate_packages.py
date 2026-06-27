#!/usr/bin/env python3
import os
import sys
import yaml

def print_err(msg):
    print(f"\033[91mERROR: {msg}\033[0m", file=sys.stderr)

def print_ok(msg):
    print(f"\033[92mOK: {msg}\033[0m")

def print_info(msg):
    print(f"\033[94mINFO: {msg}\033[0m")

def validate_registry():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index_path = os.path.join(repo_root, "package-index.yaml")
    
    if not os.path.exists(index_path):
        print_err(f"package-index.yaml not found at {index_path}")
        return False

    print_info(f"Loading package-index.yaml from {index_path}...")
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            index = yaml.safe_load(f)
    except Exception as e:
        print_err(f"Failed to parse package-index.yaml: {e}")
        return False

    if not isinstance(index, dict):
        print_err("package-index.yaml must be a YAML mapping/dictionary")
        return False

    # Check index metadata
    metadata = index.get("metadata", {})
    total_packages_declared = metadata.get("total_packages")
    packages = index.get("packages", [])
    
    if not isinstance(packages, list):
        print_err("'packages' in package-index.yaml must be a list")
        return False

    print_info(f"Registry declared packages: {len(packages)} (metadata total: {total_packages_declared})")
    
    if len(packages) != total_packages_declared:
        print_err(f"Metadata total_packages ({total_packages_declared}) does not match actual packages list length ({len(packages)})")
        return False

    registered_paths = set()
    errors = 0

    for pkg in packages:
        name = pkg.get("name")
        version = pkg.get("version")
        path = pkg.get("path")
        
        if not name or not version or not path:
            print_err(f"Package definition missing required fields (name, version, path): {pkg}")
            errors += 1
            continue

        registered_paths.add(path)
        pkg_dir = os.path.join(repo_root, path)
        
        if not os.path.isdir(pkg_dir):
            print_err(f"Package directory not found: {path} (resolved: {pkg_dir})")
            errors += 1
            continue

        manifest_path = os.path.join(pkg_dir, "cockpit-package.yml")
        if not os.path.exists(manifest_path):
            print_err(f"cockpit-package.yml not found for package {name} at {manifest_path}")
            errors += 1
            continue

        print_info(f"Validating manifest for '{name}'...")
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = yaml.safe_load(f)
        except Exception as e:
            print_err(f"Failed to parse cockpit-package.yml for {name}: {e}")
            errors += 1
            continue

        if not isinstance(manifest, dict):
            print_err(f"Manifest for {name} must be a YAML mapping")
            errors += 1
            continue

        # Verify alignment with index
        manifest_name = manifest.get("name")
        manifest_version = str(manifest.get("version")) # Ensure string comparison
        
        if manifest_name != name:
            print_err(f"Package name mismatch: index has '{name}', manifest has '{manifest_name}'")
            errors += 1
        
        if manifest_version != str(version):
            print_err(f"Package version mismatch for '{name}': index has '{version}', manifest has '{manifest_version}'")
            errors += 1

        # Validate feature paths
        features = manifest.get("features", {})
        if isinstance(features, dict):
            for feature_type, feature_list in features.items():
                if not isinstance(feature_list, list):
                    continue
                for item in feature_list:
                    if isinstance(item, dict) and "path" in item:
                        fpath = item["path"]
                        if os.path.isabs(fpath):
                            print_err(f"Package '{name}' declares feature '{feature_type}' with absolute path '{fpath}' which is not allowed")
                            errors += 1
                        else:
                            full_fpath = os.path.normpath(os.path.join(pkg_dir, fpath))
                            if not os.path.exists(full_fpath):
                                print_err(f"Package '{name}' declares feature '{feature_type}' with path '{fpath}', but it does not exist at '{full_fpath}'")
                                errors += 1
                            else:
                                print_ok(f"  Feature '{feature_type}' path verified: {fpath}")

    # Check for unregistered package directories in the packages/ directory
    packages_root = os.path.join(repo_root, "packages")
    if os.path.isdir(packages_root):
        for entry in os.listdir(packages_root):
            entry_path = os.path.join(packages_root, entry)
            if not os.path.isdir(entry_path):
                continue
            if entry.startswith("."):
                continue
            manifest_path = os.path.join(entry_path, "cockpit-package.yml")
            if os.path.exists(manifest_path):
                registered_path = f"packages/{entry}"
                if registered_path not in registered_paths:
                    print_err(f"Orphan package directory found: 'packages/{entry}' contains cockpit-package.yml but is not registered in package-index.yaml")
                    errors += 1

    if errors > 0:
        print_err(f"Validation failed with {errors} errors.")
        return False

    print_ok("All packages and index validated successfully!")
    return True

if __name__ == "__main__":
    success = validate_registry()
    sys.exit(0 if success else 1)
