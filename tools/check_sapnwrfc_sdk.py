#!/usr/bin/env python3
"""
SAP NetWeaver RFC SDK System Check
Validates SAP NetWeaver RFC SDK installation and configuration
"""

import os
import platform
import sys
from datetime import datetime
from pathlib import Path


def check_sapnwrfc_sdk():
    """Comprehensive SAP NetWeaver RFC SDK system check."""
    print("[CHECK] SAP NetWeaver RFC SDK System Validation")
    print("=" * 50)
    print(f"[INFO] Platform: {platform.system()} {platform.architecture()[0]}")
    print(f"[INFO] Python: {sys.version.split()[0]}")
    print(f"[TIME] Check started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    issues_found = []
    checks_passed = 0
    total_checks = 0

    # Check 1: SAPNWRFC_HOME environment variable
    print("[1] Checking SAPNWRFC_HOME environment variable...")
    total_checks += 1

    sapnwrfc_home = os.environ.get("SAPNWRFC_HOME")
    if sapnwrfc_home:
        print(f"[OK] SAPNWRFC_HOME found: {sapnwrfc_home}")
        checks_passed += 1

        # Verify the path exists
        if Path(sapnwrfc_home).exists():
            print(f"[OK] Directory exists: {sapnwrfc_home}")
        else:
            print(f"[ERROR] Directory does not exist: {sapnwrfc_home}")
            issues_found.append("SAPNWRFC_HOME points to non-existent directory")
    else:
        print("[ERROR] SAPNWRFC_HOME environment variable not set")
        issues_found.append("SAPNWRFC_HOME environment variable missing")
        return check_summary(checks_passed, total_checks, issues_found)

    # Check 2: Required folder structure
    print(f"\n[2] Checking required folder structure...")
    total_checks += 1

    expected_folders = {
        "bin": "Executable binaries (rfcexec.exe, startrfc.exe)",
        "demo": "Demo applications and samples",
        "doc": "Documentation files",
        "include": "Header files for development",
        "lib": "Library files (sapnwrfc.dll, ICU libraries)",
    }

    sapnwrfc_path = Path(sapnwrfc_home)
    missing_folders = []

    for folder, description in expected_folders.items():
        folder_path = sapnwrfc_path / folder
        if folder_path.exists() and folder_path.is_dir():
            print(f"[OK] {folder:8} - {description}")
        else:
            print(f"[ERROR] {folder:8} - Missing: {description}")
            missing_folders.append(folder)

    if not missing_folders:
        checks_passed += 1
    else:
        issues_found.append(f"Missing folders: {', '.join(missing_folders)}")

    # Check 3: Critical library files
    print(f"\n[3] Checking critical library files...")
    total_checks += 1

    critical_files = {
        "lib/sapnwrfc.dll": "Main SAP NetWeaver RFC library",
        "lib/sapnwrfc.lib": "Import library for linking",
        "lib/icudt50.dll": "ICU data library",
        "lib/icuin50.dll": "ICU internationalization library",
        "lib/icuuc50.dll": "ICU common library",
        "lib/libsapucum.dll": "SAP Unicode library",
    }

    missing_files = []

    for file_path, description in critical_files.items():
        full_path = sapnwrfc_path / file_path
        if full_path.exists() and full_path.is_file():
            size_mb = full_path.stat().st_size / (1024 * 1024)
            print(f"[OK] {file_path:20} - {description} ({size_mb:.1f} MB)")
        else:
            print(f"[ERROR] {file_path:20} - Missing: {description}")
            missing_files.append(file_path)

    if not missing_files:
        checks_passed += 1
    else:
        issues_found.append(f"Missing critical files: {', '.join(missing_files)}")

    # Check 4: Executable files
    print(f"\n[4] Checking executable files...")
    total_checks += 1

    executable_files = {
        "bin/rfcexec.exe": "RFC execution utility",
        "bin/startrfc.exe": "RFC startup utility",
    }

    missing_executables = []

    for exe_path, description in executable_files.items():
        full_path = sapnwrfc_path / exe_path
        if full_path.exists() and full_path.is_file():
            size_kb = full_path.stat().st_size / 1024
            print(f"[OK] {exe_path:18} - {description} ({size_kb:.0f} KB)")
        else:
            print(f"[ERROR] {exe_path:18} - Missing: {description}")
            missing_executables.append(exe_path)

    if not missing_executables:
        checks_passed += 1
    else:
        issues_found.append(f"Missing executables: {', '.join(missing_executables)}")

    # Check 5: PATH environment variable
    print(f"\n[5] Checking PATH environment variable...")
    total_checks += 1

    path_env = os.environ.get("PATH", "")
    lib_path = str(sapnwrfc_path / "lib")

    if lib_path.lower() in path_env.lower():
        print(f"[OK] SAP NetWeaver RFC lib directory found in PATH")
        checks_passed += 1
    else:
        print(f"[WARNING] SAP NetWeaver RFC lib directory not in PATH")
        print(f"[INFO] Consider adding to PATH: {lib_path}")
        issues_found.append("SAP NetWeaver RFC lib directory not in PATH")

    # Check 6: Try to import pyrfc
    print(f"\n[6] Checking Python pyrfc module...")
    total_checks += 1

    try:
        import pyrfc

        print(f"[OK] pyrfc module imported successfully")
        print(f"[INFO] pyrfc version: {pyrfc.__version__}")
        checks_passed += 1

        # Try to get connection info
        try:
            print(f"[INFO] pyrfc binding version: {pyrfc.Connection.get_version()}")
        except Exception as e:
            print(f"[WARNING] Could not get pyrfc binding version: {e}")

    except ImportError as e:
        print(f"[ERROR] pyrfc module not available: {e}")
        issues_found.append("pyrfc Python module not installed or not working")
    except Exception as e:
        print(f"[ERROR] Error testing pyrfc: {e}")
        issues_found.append(f"pyrfc module error: {e}")

    # Check 7: Verify library dependencies (Windows specific)
    if platform.system() == "Windows":
        print(f"\n[7] Checking Windows library dependencies...")
        total_checks += 1

        try:
            import ctypes

            sapnwrfc_dll = sapnwrfc_path / "lib" / "sapnwrfc.dll"

            if sapnwrfc_dll.exists():
                try:
                    # Try to load the library
                    lib = ctypes.CDLL(str(sapnwrfc_dll))
                    print(f"[OK] sapnwrfc.dll loaded successfully")
                    checks_passed += 1
                except Exception as e:
                    print(f"[ERROR] Failed to load sapnwrfc.dll: {e}")
                    issues_found.append(f"sapnwrfc.dll load error: {e}")
            else:
                print(f"[ERROR] sapnwrfc.dll not found")
                issues_found.append("sapnwrfc.dll not found")
        except Exception as e:
            print(f"[WARNING] Could not test library dependencies: {e}")

    # Check 8: Version information
    print(f"\n[8] Extracting version information...")
    total_checks += 1

    try:
        # Try to extract version from path name
        home_name = Path(sapnwrfc_home).name
        if "SAPNWRFC" in home_name.upper():
            version_part = home_name.replace("SAPNWRFC", "").replace("_", "").strip()
            if version_part:
                print(f"[INFO] Detected SDK version from path: {version_part}")
            else:
                print(f"[INFO] SDK version could not be determined from path")

        # Check library file dates
        sapnwrfc_dll = sapnwrfc_path / "lib" / "sapnwrfc.dll"
        if sapnwrfc_dll.exists():
            mtime = datetime.fromtimestamp(sapnwrfc_dll.stat().st_mtime)
            print(f"[INFO] sapnwrfc.dll last modified: {mtime.strftime('%Y-%m-%d')}")

        checks_passed += 1

    except Exception as e:
        print(f"[WARNING] Could not extract version information: {e}")

    return check_summary(checks_passed, total_checks, issues_found)


def check_summary(checks_passed, total_checks, issues_found):
    """Print summary of checks."""
    print(f"\n[SUMMARY] SAP NetWeaver RFC SDK Check Results")
    print("=" * 45)
    print(f"[INFO] Checks passed: {checks_passed}/{total_checks}")

    if checks_passed == total_checks:
        print(
            f"[SUCCESS] All checks passed! SAP NetWeaver RFC SDK is properly installed."
        )
        status = True
    else:
        print(f"[WARNING] {total_checks - checks_passed} check(s) failed.")
        status = False

    if issues_found:
        print(f"\n[ISSUES] Issues found:")
        for i, issue in enumerate(issues_found, 1):
            print(f"  {i}. {issue}")

        print(f"\n[TIP] Troubleshooting suggestions:")
        print(f"• Ensure SAP NetWeaver RFC SDK is properly installed")
        print(
            f"• Verify SAPNWRFC_HOME environment variable points to correct directory"
        )
        print(f"• Add SAP NetWeaver RFC lib directory to PATH environment variable")
        print(f"• Install pyrfc: pip install pyrfc")
        print(f"• Restart command prompt/IDE after environment variable changes")
        print(f"• Download SAP NetWeaver RFC SDK from SAP Support Portal")

    return status


def main():
    """Main function."""
    print(f"[INFO] SAP NetWeaver RFC SDK System Checker")
    print(f"[INFO] Validates SAP NetWeaver RFC SDK installation")
    print()

    try:
        success = check_sapnwrfc_sdk()

        if success:
            print(f"\n[SUCCESS] SAP NetWeaver RFC SDK check completed successfully!")
            return True
        else:
            print(f"\n[ERROR] SAP NetWeaver RFC SDK check completed with issues!")
            return False

    except KeyboardInterrupt:
        print(f"\n[INFO] Check interrupted by user")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during check: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
