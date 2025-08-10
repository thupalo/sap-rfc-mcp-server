"""SAP Connection Configuration."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class SAPConfig:
    """SAP connection configuration."""

    user: str
    passwd: str
    ashost: str
    sysnr: str
    client: str
    lang: str = "EN"
    trace: str = "0"

    @classmethod
    def from_env(cls) -> "SAPConfig":
        """Create config from environment variables."""
        return cls(
            user=os.getenv("SAP_USER", ""),
            passwd=os.getenv("SAP_PASSWD", ""),
            ashost=os.getenv("SAP_ASHOST", ""),
            sysnr=os.getenv("SAP_SYSNR", ""),
            client=os.getenv("SAP_CLIENT", ""),
            lang=os.getenv("SAP_LANG", ""),
            trace=os.getenv("SAP_TRACE", ""),
        )

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
