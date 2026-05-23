"""
Activity Heatmap
Visualizes whale activity patterns by hour and day of week.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


@dataclass
class HeatmapCell:
    day: str  # "Mon", "Tue", etc.
    hour: int  # 0-23
    activity_score: float  # 0-100
    tx_count: int
    volume_usd: float


# DEMO DATA: Simulated activity patterns
# Real production: aggregate historical whale transactions by time
DEMO_HEATMAP_DATA: Dict[Tuple[str, int], HeatmapCell] = {}

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Generate realistic demo patterns
import random
random.seed(42)

for day in DAYS:
    for hour in range(24):
        # More activity during US/EU market hours
        base_score = 20
        if 13 <= hour <= 21:  # US market hours (UTC)
            base_score = 60
        elif 8 <= hour <= 16:  # EU market hours (UTC)
            base_score = 45
        elif 0 <= hour <= 4:  # Asia hours
            base_score = 35
        
        # Weekend reduction
        if day in ["Sat", "Sun"]:
            base_score *= 0.6
        
        score = min(100, base_score + random.uniform(-15, 15))
        tx_count = int(score * random.uniform(0.8, 1.2))
        volume = score * random.uniform(500_000, 2_000_000)
        
        DEMO_HEATMAP_DATA[(day, hour)] = HeatmapCell(day, hour, score, tx_count, volume)


class ActivityHeatmap:
    """
    Generates whale activity heatmaps by hour and day.
    
    Helps identify:
    - Peak whale activity hours
    - Best times to monitor for large moves
    - Timezone patterns of different whale groups
    
    [DEMO] Uses simulated activity data with realistic patterns.
    [PRODUCTION] Aggregate from historical whale transaction data.
    """

    def __init__(self, demo: bool = True):
        self.demo = demo

    async def get_heatmap(self) -> Dict[Tuple[str, int], HeatmapCell]:
        """Get the full heatmap data."""
        if self.demo:
            return DEMO_HEATMAP_DATA
        
        # Production: aggregate from transaction history
        return {}

    async def get_peak_hours(self, top_n: int = 5) -> List[HeatmapCell]:
        """Get the top N peak activity hours."""
        heatmap = await self.get_heatmap()
        cells = sorted(heatmap.values(), key=lambda c: c.activity_score, reverse=True)
        return cells[:top_n]

    async def get_quiet_hours(self, top_n: int = 5) -> List[HeatmapCell]:
        """Get the top N quietest hours."""
        heatmap = await self.get_heatmap()
        cells = sorted(heatmap.values(), key=lambda c: c.activity_score)
        return cells[:top_n]

    async def get_day_summary(self) -> Dict[str, float]:
        """Get average activity score per day."""
        heatmap = await self.get_heatmap()
        day_scores: Dict[str, List[float]] = {}
        
        for (day, hour), cell in heatmap.items():
            if day not in day_scores:
                day_scores[day] = []
            day_scores[day].append(cell.activity_score)
        
        return {day: sum(scores) / len(scores) for day, scores in day_scores.items()}

    async def generate_report(self) -> str:
        """Generate heatmap report with ASCII visualization."""
        heatmap = await self.get_heatmap()
        peak = await self.get_peak_hours(3)
        quiet = await self.get_quiet_hours(3)
        day_summary = await self.get_day_summary()
        
        lines = [
            "🗓️ WHALE ACTIVITY HEATMAP",
            "=" * 50,
            "",
        ]
        
        # ASCII heatmap
        # Header
        hours_str = "".join(f"{h:3d}" for h in range(24))
        lines.append(f"     {hours_str}")
        lines.append(f"     {'---' * 24}")
        
        for day in DAYS:
            row = f"{day} |"
            for hour in range(24):
                cell = heatmap.get((day, hour))
                if cell:
                    # Use block characters for intensity
                    if cell.activity_score >= 70:
                        row += " ██"
                    elif cell.activity_score >= 50:
                        row += " ▓▓"
                    elif cell.activity_score >= 30:
                        row += " ░░"
                    else:
                        row += "   "
                else:
                    row += "   "
            lines.append(row)
        
        lines.append(f"\nLegend: ██ High (>70) | ▓▓ Medium (50-70) | ░░ Low (30-50) |    Very Low (<30)")
        
        lines.append("\n📊 Peak Activity Hours:")
        for cell in peak:
            lines.append(f"  🔥 {cell.day} {cell.hour:02d}:00 UTC - Score: {cell.activity_score:.0f} | "
                        f"{cell.tx_count} txs | ${cell.volume_usd:,.0f}")
        
        lines.append("\n📊 Quietest Hours:")
        for cell in quiet:
            lines.append(f"  😴 {cell.day} {cell.hour:02d}:00 UTC - Score: {cell.activity_score:.0f} | "
                        f"{cell.tx_count} txs | ${cell.volume_usd:,.0f}")
        
        lines.append("\n📊 Day Averages:")
        for day in DAYS:
            score = day_summary.get(day, 0)
            bar = "█" * int(score / 5)
            lines.append(f"  {day}: {bar} {score:.0f}")
        
        return "\n".join(lines)
