#!/usr/bin/env python3
"""
Validate all packages registered in cockpit-registry.

Checks performed per package:
  1. package-index.yaml integrity (total_packages, required fields, path exists)
  2. cockpit-package.yml presence and YAML validity
  3. Required manifest fields: name, version, description, author, license,
     requirements.cockpit
  4. Manifest name/version alignment with the index
  5. Feature paths existence (no absolute paths)
  6. CLI modules contract: if features.modules is declared, bin/configure and
     bin/validate must exist and be executable
  7. Orphan packages (directory with manifest not in the index)
"""

import os
import stat
import sys
import yaml


# Manifest top-level fields that must be present and non-empty.
REQUIRED_MANIFEST_FIELDS = ["name", "version", "description", "author", "license"]


def print_err(msg):
    print(f"\033[91mERROR: {msg}\033[0m", file=sys.stderr)

def print_ok(msg):
    print(f"\033[92mOK: {msg}\033[0m")

def print_info(msg):
    print(f"\033[94mINFO: {msg}\033[0m")


def _is_executable(path: str) -> bool:
    """Return True if *path* exists and has at least one executable bit set."""
    try:
        mode = os.stat(path).st_mode
        return bool(mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
    except OSError:
        return False


def validate_manifest_fields(name: str, manifest: dict) -> int:
    """Validate required top-level fields and requirements.cockpit. Returns error count."""
    errors = 0
    for field in REQUIRED_MANIFEST_FIELDS:
        if not manifest.get(field):
            print_err(f"Package '{name}': manifest missing required field '{field}'")
            errors += 1

    reqs = manifest.get("requirements")
    if not isinstance(reqs, dict) or not reqs.get("cockpit"):
        print_err(
            f"Package '{name}': manifest missing 'requirements.cockpit' "
            f"(minimum cockpit version constraint)"
        )
        errors += 1

    return errors


def validate_modules_contract(name: str, pkg_dir: str, manifest: dict) -> int:
    """
    If the manifest declares features.modules, enforce the CLI contract:
      - bin/configure must exist and be executable
      - bin/validate  must exist and be executable
    Returns error count.
    """
    features = manifest.get("features", {})
    if not isinstance(features, dict):
        return 0

    modules = features.get("modules")
    if not modules:
        return 0  # No modules declared — contract does not apply.

    errors = 0
    for script in ("configure", "validate"):
        script_path = os.path.join(pkg_dir, "bin", script)
        if not os.path.isfile(script_path):
            print_err(
                f"Package '{name}' declares features.modules but is missing "
                f"required script: bin/{script}"
            )
            errors += 1
        elif not _is_executable(script_path):
            print_err(
                f"Package '{name}': bin/{script} exists but is not executable "
                f"(run: chmod +x bin/{script})"
            )
            errors += 1
        else:
            print_ok(f"  bin/{script} — present and executable")

    return errors

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

        # Validate required manifest fields
        errors += validate_manifest_fields(name, manifest)

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

        # Validate CLI modules contract (bin/configure + bin/validate)
        errors += validate_modules_contract(name, pkg_dir, manifest)

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
