"""
Smart Contract Auditor
AI-powered Solidity contract analysis using MiMo.
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..client import MiMoClient

logger = logging.getLogger(__name__)


@dataclass
class Vulnerability:
    severity: str  # "critical", "high", "medium", "low", "informational"
    name: str
    description: str
    line_numbers: List[int]
    recommendation: str
    cwe_id: Optional[str] = None  # Common Weakness Enumeration ID


@dataclass
class GasOptimization:
    location: str
    current_pattern: str
    optimized_pattern: str
    estimated_savings: str  # e.g., "~200 gas per call"


@dataclass
class AuditResult:
    contract_name: str
    vulnerabilities: List[Vulnerability]
    gas_optimizations: List[GasOptimization]
    overall_risk: str  # "critical", "high", "medium", "low", "safe"
    score: int  # 0-100
    summary: str
    lines_analyzed: int


# Common vulnerability patterns (regex-based pre-screening)
VULN_PATTERNS = [
    (r'\.call\{value:', "Potential reentrancy with value transfer", "high", "CWE-841"),
    (r'tx\.origin', "Use of tx.origin for authentication", "high", "CWE-477"),
    (r'selfdestruct', "Selfdestruct usage - funds may be lost", "critical", "CWE-740"),
    (r'block\.timestamp', "Block timestamp dependency", "low", "CWE-829"),
    (r'assembly\s*\{', "Inline assembly usage - review carefully", "informational", None),
    (r'delegatecall', "Delegatecall usage - potential for proxy attacks", "critical", "CWE-829"),
    (r'unsafe\s+ERC20', "Unsafe ERC20 operation", "medium", None),
    (r'approve\(', "Approve race condition", "medium", "CWE-362"),
    (r'ecrecover', "ecrecover may return address(0)", "medium", "CWE-252"),
    (r'floating\s+pragma', "Floating pragma version", "informational", None),
]

GAS_PATTERNS = [
    (r'for\s*\(uint\s+\w+\s*=\s*0;\s*\w+\s*<\s*\w+\.length', "Cache array length outside loop", "~200 gas per iteration"),
    (r'uint256\s+\w+\s*=\s*0;', "Use uint256 default (no need to initialize to 0)", "~3 gas"),
    (r'public\s+\w+\s*=', "Consider using immutable/constant for unchanging values", "~2000 gas on deployment"),
    (r'\+\+\w+;', "Use unchecked{++i} when overflow is impossible", "~80 gas per iteration"),
    (r'string\s+public', "Consider using bytes32 for short strings", "~2000 gas per storage slot"),
]


class SmartContractAuditor:
    """
    AI-powered smart contract auditor.
    
    Features:
    - Pattern-based vulnerability detection
    - MiMo AI deep analysis
    - Gas optimization suggestions
    - OWASP-style severity rating
    
    [REAL] Regex pattern matching for known vulnerability patterns
    [REAL] MiMo-V2.5-Pro for deep semantic analysis
    """

    def __init__(self, mimo_client: MiMoClient):
        self.mimo = mimo_client

    def _pattern_scan(self, code: str) -> List[Vulnerability]:
        """Quick regex-based vulnerability scanning."""
        vulns = []
        lines = code.split('\n')
        
        for pattern, desc, severity, cwe in VULN_PATTERNS:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    vulns.append(Vulnerability(
                        severity=severity,
                        name=desc,
                        description=f"Found pattern '{pattern}' at line {i}",
                        line_numbers=[i],
                        recommendation=f"Review line {i} and consider safer alternatives",
                        cwe_id=cwe,
                    ))
        
        return vulns

    def _gas_scan(self, code: str) -> List[GasOptimization]:
        """Quick regex-based gas optimization scanning."""
        optimizations = []
        lines = code.split('\n')
        
        for pattern, suggestion, savings in GAS_PATTERNS:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    optimizations.append(GasOptimization(
                        location=f"Line {i}",
                        current_pattern=line.strip()[:80],
                        optimized_pattern=suggestion,
                        estimated_savings=savings,
                    ))
        
        return optimizations

    async def audit_contract(self, code: str, contract_name: str = "Unknown") -> AuditResult:
        """
        Perform a comprehensive smart contract audit.
        
        1. Pattern-based scanning (fast, deterministic)
        2. MiMo AI deep analysis (thorough, contextual)
        3. Combine results
        """
        # Step 1: Pattern scan
        pattern_vulns = self._pattern_scan(code)
        gas_opts = self._gas_scan(code)

        # Step 2: MiMo deep analysis
        prompt = f"""Analyze this Solidity smart contract for security vulnerabilities:

```solidity
{code[:6000]}
```

Identify vulnerabilities and respond in JSON:
{{
  "vulnerabilities": [
    {{
      "severity": "critical/high/medium/low/informational",
      "name": "Vulnerability name",
      "description": "Detailed description",
      "line_range": "approximate line numbers",
      "recommendation": "How to fix",
      "cwe": "CWE-XXX or null"
    }}
  ],
  "gas_optimizations": [
    {{
      "location": "function or line",
      "current": "current pattern",
      "optimized": "better pattern",
      "savings": "estimated savings"
    }}
  ],
  "overall_assessment": "brief security assessment",
  "score": 0-100
}}

Focus on: reentrancy, access control, integer overflow, flash loan attacks,
oracle manipulation, front-running, and centralization risks.
"""

        system = (
            "You are an expert smart contract security auditor. "
            "Analyze Solidity code for vulnerabilities. Be thorough but avoid false positives. "
            "Always respond in valid JSON."
        )

        ai_vulns = []
        ai_gas = []
        ai_score = 70
        ai_summary = "Pattern-based analysis completed."

        try:
            result = await self.mimo.chat_json(prompt, system)
            
            for v in result.get("vulnerabilities", []):
                ai_vulns.append(Vulnerability(
                    severity=v.get("severity", "medium"),
                    name=v.get("name", "Unknown"),
                    description=v.get("description", ""),
                    line_numbers=[],  # AI gives approximate ranges
                    recommendation=v.get("recommendation", ""),
                    cwe_id=v.get("cwe"),
                ))
            
            for g in result.get("gas_optimizations", []):
                ai_gas.append(GasOptimization(
                    location=g.get("location", "Unknown"),
                    current_pattern=g.get("current", ""),
                    optimized_pattern=g.get("optimized", ""),
                    estimated_savings=g.get("savings", "Unknown"),
                ))
            
            ai_score = result.get("score", 70)
            ai_summary = result.get("overall_assessment", "")
        except Exception as e:
            logger.warning(f"MiMo audit analysis error: {e}")
            ai_summary = "AI analysis unavailable; pattern-based results only."

        # Combine results
        all_vulns = pattern_vulns + ai_vulns
        all_gas = gas_opts + ai_gas

        # Deduplicate by name
        seen_vuln_names = set()
        unique_vulns = []
        for v in all_vulns:
            if v.name not in seen_vuln_names:
                unique_vulns.append(v)
                seen_vuln_names.add(v.name)

        # Determine overall risk
        critical = sum(1 for v in unique_vulns if v.severity == "critical")
        high = sum(1 for v in unique_vulns if v.severity == "high")
        
        if critical > 0:
            overall_risk = "critical"
        elif high > 0:
            overall_risk = "high"
        elif any(v.severity == "medium" for v in unique_vulns):
            overall_risk = "medium"
        elif any(v.severity == "low" for v in unique_vulns):
            overall_risk = "low"
        else:
            overall_risk = "safe"

        return AuditResult(
            contract_name=contract_name,
            vulnerabilities=unique_vulns,
            gas_optimizations=all_gas,
            overall_risk=overall_risk,
            score=ai_score,
            summary=ai_summary,
            lines_analyzed=len(code.split('\n')),
        )

    async def generate_report(self, result: AuditResult) -> str:
        """Generate a formatted audit report."""
        risk_emoji = {
            "critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢", "safe": "✅"
        }

        lines = [
            "🔍 SMART CONTRACT AUDIT REPORT",
            "=" * 50,
            f"Contract: {result.contract_name}",
            f"Lines Analyzed: {result.lines_analyzed}",
            f"Overall Risk: {risk_emoji.get(result.overall_risk, '❓')} {result.overall_risk.upper()}",
            f"Security Score: {result.score}/100",
            f"Vulnerabilities Found: {len(result.vulnerabilities)}",
            f"Gas Optimizations: {len(result.gas_optimizations)}",
            "",
            f"Summary: {result.summary}",
        ]

        if result.vulnerabilities:
            lines.append("\n🚨 VULNERABILITIES:")
            for v in sorted(result.vulnerabilities, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3, "informational": 4}.get(x.severity, 5)):
                emoji = risk_emoji.get(v.severity, "❓")
                lines.append(f"\n  {emoji} [{v.severity.upper()}] {v.name}")
                lines.append(f"     {v.description}")
                lines.append(f"     Fix: {v.recommendation}")
                if v.cwe_id:
                    lines.append(f"     CWE: {v.cwe_id}")

        if result.gas_optimizations:
            lines.append("\n⛽ GAS OPTIMIZATIONS:")
            for g in result.gas_optimizations[:10]:
                lines.append(f"  📍 {g.location}")
                lines.append(f"     Current: {g.current_pattern[:60]}...")
                lines.append(f"     Better: {g.optimized_pattern}")
                lines.append(f"     Savings: {g.estimated_savings}")

        return "\n".join(lines)
