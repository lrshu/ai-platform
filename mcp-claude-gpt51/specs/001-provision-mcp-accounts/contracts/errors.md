# MCP Provisioning Validation Errors

| Code | Message | Client Action |
| --- | --- | --- |
| ERR_INVALID_ID | National ID is not a valid 18-digit GB11643 number. | Verify ID length, digits, and checksum; resubmit after correcting data. |
| ERR_TRANSLITERATION | Name cannot be transliterated into compliant pinyin. | Update HR records to use supported characters; retry once resolved. |
| ERR_CONFIG | Provisioning service misconfiguration detected. | Escalate to platform operations; retry after configuration is fixed. |
