"""Enhanced SAP Connection Configuration with Security Best Practices."""

import os
import json
import base64
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False


class SecurityError(Exception):
    """Security-related configuration error."""
    pass


@dataclass
class SAPConfig:
    """SAP connection configuration with enhanced security."""
    
    user: str
    passwd: str = field(repr=False)  # Hide password in string representation
    ashost: str
    sysnr: str
    client: str
    lang: str = "EN"
    trace: str = "0"
    
    # Security metadata
    _credential_source: str = field(default="unknown", init=False, repr=False)
    _encrypted: bool = field(default=False, init=False, repr=False)
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_credentials()
    
    def _validate_credentials(self):
        """Validate that all required credentials are present."""
        required_fields = ["user", "passwd", "ashost", "sysnr", "client"]
        missing_fields = [field for field in required_fields if not getattr(self, field)]
        
        if missing_fields:
            raise SecurityError(f"Missing required SAP credentials: {', '.join(missing_fields)}")
    
    @classmethod
    def from_env(cls, prefix: str = "SAP_") -> "SAPConfig":
        """Create config from environment variables (legacy method)."""
        config = cls(
            user=os.getenv(f"{prefix}USER", ""),
            passwd=os.getenv(f"{prefix}PASSWORD", ""),
            ashost=os.getenv(f"{prefix}ASHOST", ""),
            sysnr=os.getenv(f"{prefix}SYSNR", ""),
            client=os.getenv(f"{prefix}CLIENT", ""),
            lang=os.getenv(f"{prefix}LANG", "EN"),
            trace=os.getenv(f"{prefix}TRACE", "0"),
        )
        config._credential_source = "environment"
        return config
    
    @classmethod
    def from_dotenv(cls, env_file: Optional[Path] = None, prefix: str = "SAP_") -> "SAPConfig":
        """Create config from .env file (recommended for development)."""
        if not DOTENV_AVAILABLE:
            raise SecurityError("python-dotenv package is required for .env file support. Install with: pip install python-dotenv")
        
        if env_file is None:
            env_file = Path.cwd() / ".env"
        
        if not env_file.exists():
            raise SecurityError(f"Environment file not found: {env_file}")
        
        # Load .env file
        load_dotenv(env_file)
        
        config = cls.from_env(prefix)
        config._credential_source = f"dotenv:{env_file}"
        return config
    
    @classmethod
    def from_keyring(cls, service_name: str = "AgentSAP", username: str = "sap_connection") -> "SAPConfig":
        """Create config from system keyring (recommended for production)."""
        if not KEYRING_AVAILABLE:
            raise SecurityError("keyring package is required for keyring support. Install with: pip install keyring")
        
        try:
            # Retrieve encrypted credentials from keyring
            encrypted_data = keyring.get_password(service_name, username)
            if not encrypted_data:
                raise SecurityError(f"No credentials found in keyring for service '{service_name}', user '{username}'")
            
            # Decode and parse credentials
            credentials = json.loads(encrypted_data)
            
            config = cls(
                user=credentials["user"],
                passwd=credentials["passwd"],
                ashost=credentials["ashost"],
                sysnr=credentials["sysnr"],
                client=credentials["client"],
                lang=credentials.get("lang", "EN"),
                trace=credentials.get("trace", "0"),
            )
            config._credential_source = f"keyring:{service_name}"
            return config
            
        except (json.JSONDecodeError, KeyError) as e:
            raise SecurityError(f"Invalid credential format in keyring: {e}")
    
    @classmethod
    def from_encrypted_file(cls, file_path: Path, password: str) -> "SAPConfig":
        """Create config from encrypted file (enterprise-grade security)."""
        if not file_path.exists():
            raise SecurityError(f"Encrypted credential file not found: {file_path}")
        
        try:
            # Read encrypted file
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Derive key from password
            salt = encrypted_data[:16]  # First 16 bytes are salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Decrypt data
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data[16:])  # Skip salt
            
            # Parse credentials
            credentials = json.loads(decrypted_data.decode())
            
            config = cls(
                user=credentials["user"],
                passwd=credentials["passwd"],
                ashost=credentials["ashost"],
                sysnr=credentials["sysnr"],
                client=credentials["client"],
                lang=credentials.get("lang", "EN"),
                trace=credentials.get("trace", "0"),
            )
            config._credential_source = f"encrypted_file:{file_path}"
            config._encrypted = True
            return config
            
        except Exception as e:
            raise SecurityError(f"Failed to decrypt credential file: {e}")
    
    def save_to_keyring(self, service_name: str = "AgentSAP", username: str = "sap_connection") -> None:
        """Save credentials to system keyring."""
        if not KEYRING_AVAILABLE:
            raise SecurityError("keyring package is required for keyring support")
        
        credentials = {
            "user": self.user,
            "passwd": self.passwd,
            "ashost": self.ashost,
            "sysnr": self.sysnr,
            "client": self.client,
            "lang": self.lang,
            "trace": self.trace,
        }
        
        # Store as JSON in keyring
        keyring.set_password(service_name, username, json.dumps(credentials))
        print(f"✅ Credentials saved to keyring: {service_name}/{username}")
    
    def save_to_encrypted_file(self, file_path: Path, password: str) -> None:
        """Save credentials to encrypted file."""
        credentials = {
            "user": self.user,
            "passwd": self.passwd,
            "ashost": self.ashost,
            "sysnr": self.sysnr,
            "client": self.client,
            "lang": self.lang,
            "trace": self.trace,
        }
        
        # Generate salt and derive key
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        # Encrypt data
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(json.dumps(credentials).encode())
        
        # Save salt + encrypted data
        with open(file_path, 'wb') as f:
            f.write(salt + encrypted_data)
        
        # Set restrictive file permissions
        file_path.chmod(0o600)  # Read/write for owner only
        print(f"✅ Credentials encrypted and saved to: {file_path}")
    
    def to_connection_params(self) -> dict:
        """Convert to pyrfc connection parameters."""
        return {
            "user": self.user,
            "passwd": self.passwd,
            "ashost": self.ashost,
            "sysnr": self.sysnr,
            "client": self.client,
            "lang": self.lang,
            "trace": self.trace,
        }
    
    def get_security_info(self) -> Dict[str, Any]:
        """Get information about credential security."""
        return {
            "source": self._credential_source,
            "encrypted": self._encrypted,
            "has_credentials": bool(self.user and self.passwd and self.ashost),
            "connection_string": f"{self.user}@{self.ashost}:{self.sysnr}[{self.client}]"
        }
    
    def __repr__(self) -> str:
        """String representation without sensitive data."""
        return (f"SAPConfig(user='{self.user}', ashost='{self.ashost}', "
                f"sysnr='{self.sysnr}', client='{self.client}', "
                f"source='{self._credential_source}')")


class SAPConfigManager:
    """Manager for SAP configuration with multiple security options."""
    
    @staticmethod
    def get_config(method: str = "auto", **kwargs) -> SAPConfig:
        """Get SAP configuration using specified method.
        
        Args:
            method: Configuration method - 'auto', 'env', 'dotenv', 'keyring', 'encrypted_file'
            **kwargs: Method-specific arguments
        
        Returns:
            SAPConfig instance
        """
        if method == "auto":
            return SAPConfigManager._auto_detect_config()
        elif method == "env":
            return SAPConfig.from_env(kwargs.get("prefix", "SAP_"))
        elif method == "dotenv":
            return SAPConfig.from_dotenv(
                kwargs.get("env_file"),
                kwargs.get("prefix", "SAP_")
            )
        elif method == "keyring":
            return SAPConfig.from_keyring(
                kwargs.get("service_name", "AgentSAP"),
                kwargs.get("username", "sap_connection")
            )
        elif method == "encrypted_file":
            return SAPConfig.from_encrypted_file(
                kwargs["file_path"],
                kwargs["password"]
            )
        else:
            raise SecurityError(f"Unknown configuration method: {method}")
    
    @staticmethod
    def _auto_detect_config() -> SAPConfig:
        """Auto-detect best available configuration method."""
        # Priority order: keyring > encrypted_file > .env > environment
        
        # Try keyring first (most secure)
        if KEYRING_AVAILABLE:
            try:
                return SAPConfig.from_keyring()
            except SecurityError:
                pass  # Keyring not configured, try next method
        
        # Try .env file (good for development)
        env_file = Path.cwd() / ".env"
        if DOTENV_AVAILABLE and env_file.exists():
            try:
                return SAPConfig.from_dotenv(env_file)
            except SecurityError:
                pass  # .env file doesn't have SAP config
        
        # Fall back to environment variables
        try:
            return SAPConfig.from_env()
        except SecurityError:
            raise SecurityError(
                "No SAP credentials found. Please configure using one of: "
                "keyring, .env file, or environment variables"
            )
    
    @staticmethod
    def setup_credentials_interactive() -> SAPConfig:
        """Interactive setup for SAP credentials."""
        print("🔧 SAP Credentials Setup")
        print("=" * 30)
        
        # Collect credentials
        user = input("SAP User: ").strip()
        passwd = input("SAP Password: ").strip()  # Note: visible input, consider getpass
        ashost = input("SAP Application Server Host: ").strip()
        sysnr = input("SAP System Number: ").strip()
        client = input("SAP Client: ").strip()
        lang = input("Language (default: EN): ").strip() or "EN"
        
        config = SAPConfig(
            user=user,
            passwd=passwd,
            ashost=ashost,
            sysnr=sysnr,
            client=client,
            lang=lang
        )
        
        # Choose storage method
        print("\n🔐 Choose credential storage method:")
        print("1. System Keyring (recommended for production)")
        print("2. Encrypted File (enterprise-grade)")
        print("3. .env File (development only)")
        
        choice = input("Choice (1-3): ").strip()
        
        if choice == "1" and KEYRING_AVAILABLE:
            config.save_to_keyring()
        elif choice == "2":
            file_path = Path(input("Encrypted file path: ").strip())
            password = input("Encryption password: ").strip()
            config.save_to_encrypted_file(file_path, password)
        elif choice == "3":
            env_file = Path(".env")
            with open(env_file, 'w') as f:
                f.write(f"SAP_USER={user}\n")
                f.write(f"SAP_PASSWORD={passwd}\n")
                f.write(f"SAP_ASHOST={ashost}\n")
                f.write(f"SAP_SYSNR={sysnr}\n")
                f.write(f"SAP_CLIENT={client}\n")
                f.write(f"SAP_LANG={lang}\n")
            env_file.chmod(0o600)
            print(f"✅ Credentials saved to {env_file}")
        else:
            print("⚠️ Invalid choice or missing dependencies")
        
        return config


# Security best practices documentation
SECURITY_RECOMMENDATIONS = """
🔐 SAP Credential Security Recommendations:

1. PRODUCTION ENVIRONMENTS:
   - Use system keyring (Windows Credential Manager, macOS Keychain, Linux Secret Service)
   - Use encrypted files with strong passwords
   - Never store credentials in code or version control

2. DEVELOPMENT ENVIRONMENTS:
   - Use .env files with restrictive permissions (600)
   - Add .env to .gitignore
   - Use environment variables as fallback

3. ENTERPRISE ENVIRONMENTS:
   - Integrate with enterprise secret management (HashiCorp Vault, Azure Key Vault, AWS Secrets Manager)
   - Use certificate-based authentication where possible
   - Implement credential rotation policies

4. GENERAL SECURITY:
   - Use least-privilege SAP user accounts
   - Enable SAP audit logging
   - Monitor connection patterns
   - Use encrypted connections (SNC/TLS)
"""
