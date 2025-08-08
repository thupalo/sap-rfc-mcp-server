"""Security Management Tool for AgentSAP SAP Credentials."""

import sys
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sap_rfc_mcp_server.secure_config import SAPConfigManager, SecurityError, SECURITY_RECOMMENDATIONS


def main():
    """Main security management interface."""
    parser = argparse.ArgumentParser(
        description="AgentSAP Security Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=SECURITY_RECOMMENDATIONS
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Interactive credential setup')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test credential configuration')
    test_parser.add_argument('--method', choices=['auto', 'env', 'dotenv', 'keyring', 'encrypted_file'],
                           default='auto', help='Configuration method to test')
    test_parser.add_argument('--file', type=Path, help='Path to encrypted file (for encrypted_file method)')
    test_parser.add_argument('--password', help='Password for encrypted file')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show security information')
    
    # Migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Migrate credentials between storage methods')
    migrate_parser.add_argument('--from', dest='from_method', required=True,
                              choices=['env', 'dotenv', 'keyring', 'encrypted_file'],
                              help='Source credential method')
    migrate_parser.add_argument('--to', dest='to_method', required=True,
                              choices=['keyring', 'encrypted_file', 'dotenv'],
                              help='Target credential method')
    migrate_parser.add_argument('--from-file', type=Path, help='Source encrypted file path')
    migrate_parser.add_argument('--from-password', help='Source file password')
    migrate_parser.add_argument('--to-file', type=Path, help='Target encrypted file path')
    migrate_parser.add_argument('--to-password', help='Target file password')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'setup':
            config = SAPConfigManager.setup_credentials_interactive()
            print(f"\n✅ Configuration completed: {config}")
            
        elif args.command == 'test':
            print(f"🔍 Testing credential configuration (method: {args.method})")
            
            kwargs = {}
            if args.method == 'encrypted_file':
                if not args.file or not args.password:
                    print("❌ --file and --password required for encrypted_file method")
                    return
                kwargs = {'file_path': args.file, 'password': args.password}
            
            config = SAPConfigManager.get_config(args.method, **kwargs)
            security_info = config.get_security_info()
            
            print("✅ Credentials loaded successfully!")
            print(f"📊 Security Info:")
            print(f"   Source: {security_info['source']}")
            print(f"   Encrypted: {security_info['encrypted']}")
            print(f"   Connection: {security_info['connection_string']}")
            
            # Test actual SAP connection
            print("\n🔗 Testing SAP connection...")
            from sap_rfc_mcp_server.sap_client import SAPRFCManager
            
            sap_manager = SAPRFCManager(config)
            system_info = sap_manager.get_system_info()
            
            if "RFCSI_EXPORT" in system_info:
                rfcsi = system_info["RFCSI_EXPORT"]
                print(f"✅ SAP Connection successful!")
                print(f"   System: {rfcsi.get('RFCSYSID', 'Unknown')}")
                print(f"   Host: {rfcsi.get('RFCHOST', 'Unknown')}")
                print(f"   Release: {rfcsi.get('RFCSAPRL', 'Unknown')}")
            else:
                print("⚠️ SAP connection established but system info unavailable")
                
        elif args.command == 'info':
            print("🔐 AgentSAP Security Information")
            print("=" * 40)
            
            # Check available security methods
            from sap_rfc_mcp_server.secure_config import DOTENV_AVAILABLE, KEYRING_AVAILABLE
            
            print(f"📦 Available Security Methods:")
            print(f"   Environment Variables: ✅ Always available")
            print(f"   .env Files: {'✅' if DOTENV_AVAILABLE else '❌'} (python-dotenv)")
            print(f"   System Keyring: {'✅' if KEYRING_AVAILABLE else '❌'} (keyring)")
            print(f"   Encrypted Files: ✅ Always available (cryptography)")
            
            # Try to detect current configuration
            print(f"\n🔍 Current Configuration:")
            try:
                config = SAPConfigManager.get_config('auto')
                security_info = config.get_security_info()
                print(f"   Source: {security_info['source']}")
                print(f"   Encrypted: {security_info['encrypted']}")
                print(f"   Status: ✅ Credentials available")
            except SecurityError as e:
                print(f"   Status: ❌ {e}")
            
            print(SECURITY_RECOMMENDATIONS)
            
        elif args.command == 'migrate':
            print(f"🔄 Migrating credentials from {args.from_method} to {args.to_method}")
            
            # Load from source
            from_kwargs = {}
            if args.from_method == 'encrypted_file':
                if not args.from_file or not args.from_password:
                    print("❌ --from-file and --from-password required")
                    return
                from_kwargs = {'file_path': args.from_file, 'password': args.from_password}
            
            config = SAPConfigManager.get_config(args.from_method, **from_kwargs)
            print(f"✅ Loaded credentials from {args.from_method}")
            
            # Save to target
            if args.to_method == 'keyring':
                config.save_to_keyring()
            elif args.to_method == 'encrypted_file':
                if not args.to_file or not args.to_password:
                    print("❌ --to-file and --to-password required")
                    return
                config.save_to_encrypted_file(args.to_file, args.to_password)
            elif args.to_method == 'dotenv':
                env_file = Path(".env")
                with open(env_file, 'w') as f:
                    f.write(f"SAP_USER={config.user}\n")
                    f.write(f"SAP_PASSWORD={config.passwd}\n")
                    f.write(f"SAP_ASHOST={config.ashost}\n")
                    f.write(f"SAP_SYSNR={config.sysnr}\n")
                    f.write(f"SAP_CLIENT={config.client}\n")
                    f.write(f"SAP_LANG={config.lang}\n")
                env_file.chmod(0o600)
                print(f"✅ Credentials saved to {env_file}")
            
            print(f"✅ Migration completed successfully!")
            
    except SecurityError as e:
        print(f"❌ Security Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
