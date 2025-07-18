from dataclasses import dataclass, field
from typing import List


@dataclass
class EmailMessageData:
    subject: str
    body: str
    from_addr: str
    to_addrs: List[str]
    cc_addrs: List[str] = field(default_factory=list)
    bcc_addrs: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    html: bool = False
