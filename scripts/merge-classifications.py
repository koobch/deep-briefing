#!/usr/bin/env python3
"""이미지 기반 분류 결과를 slide-catalog.json에 병합"""
import json
from pathlib import Path
from collections import Counter

# 3개 배치 이미지 기반 분류 결과 (에이전트 출력에서 추출)
IMAGE_CLASSIFICATIONS = {
  "ai-first-win-p01":"cover","ai-first-win-p02":"text-heavy","ai-first-win-p03":"exec-summary",
  "ai-first-win-p04":"ranked","ai-first-win-p05":"insight-chart","ai-first-win-p06":"insight-chart",
  "ai-first-win-p07":"big-number","ai-first-win-p08":"insight-chart","ai-first-win-p09":"ranked",
  "ai-first-win-p10":"ranked","ai-first-win-p11":"comparison","ai-first-win-p12":"insight-chart",
  "ai-first-win-p13":"framework","ai-first-win-p14":"comparison","ai-first-win-p15":"insight-chart",
  "ai-first-win-p16":"process","ai-first-win-p17":"case-study","ai-first-win-p18":"back-cover",
  "ai-first-pu-p01":"cover","ai-first-pu-p02":"text-heavy","ai-first-pu-p03":"exec-summary",
  "ai-first-pu-p04":"text-heavy","ai-first-pu-p05":"framework","ai-first-pu-p06":"framework",
  "ai-first-pu-p07":"big-number","ai-first-pu-p08":"insight-chart","ai-first-pu-p09":"insight-chart",
  "ai-first-pu-p10":"framework","ai-first-pu-p11":"case-study","ai-first-pu-p12":"table",
  "ai-first-pu-p13":"case-study","ai-first-pu-p14":"case-study","ai-first-pu-p15":"case-study",
  "ai-first-pu-p16":"case-study","ai-first-pu-p17":"framework","ai-first-pu-p18":"case-study",
  "ai-first-pu-p19":"framework","ai-first-pu-p20":"case-study","ai-first-pu-p21":"framework",
  "ai-first-pu-p22":"comparison","ai-first-pu-p23":"framework","ai-first-pu-p24":"matrix",
  "ai-first-pu-p25":"table","ai-first-pu-p26":"process","ai-first-pu-p27":"ranked",
  "ai-first-pu-p28":"ranked","ai-first-pu-p29":"case-study","ai-first-pu-p30":"back-cover",
  "ai-first-telco-p01":"cover","ai-first-telco-p02":"text-heavy","ai-first-telco-p03":"exec-summary",
  "ai-first-telco-p04":"text-heavy","ai-first-telco-p05":"table","ai-first-telco-p06":"insight-chart",
  "ai-first-telco-p07":"insight-chart","ai-first-telco-p08":"framework","ai-first-telco-p09":"matrix",
  "ai-first-telco-p10":"case-study","ai-first-telco-p11":"framework","ai-first-telco-p12":"process",
  "ai-first-telco-p13":"process","ai-first-telco-p14":"case-study","ai-first-telco-p15":"big-number",
  "ai-first-telco-p16":"text-heavy","ai-first-telco-p17":"framework","ai-first-telco-p18":"framework",
  "ai-first-telco-p19":"text-heavy","ai-first-telco-p20":"text-heavy","ai-first-telco-p21":"case-study",
  "ai-first-telco-p22":"back-cover",
  "genai-hr-p01":"cover","genai-hr-p02":"text-heavy","genai-hr-p03":"exec-summary",
  "genai-hr-p04":"big-number","genai-hr-p05":"framework","genai-hr-p06":"framework",
  "genai-hr-p07":"comparison","genai-hr-p08":"process","genai-hr-p09":"text-heavy",
  "genai-hr-p10":"data-visualization","genai-hr-p11":"data-visualization","genai-hr-p12":"table",
  "genai-hr-p13":"case-study","genai-hr-p14":"table","genai-hr-p15":"table",
  "genai-hr-p16":"table","genai-hr-p17":"framework","genai-hr-p18":"framework",
  "genai-hr-p19":"comparison","genai-hr-p20":"comparison","genai-hr-p21":"text-heavy",
  "genai-hr-p22":"framework","genai-hr-p23":"ranked","genai-hr-p24":"framework",
  "genai-hr-p25":"data-visualization","genai-hr-p26":"framework","genai-hr-p27":"big-number",
  "genai-hr-p28":"ranked","genai-hr-p29":"framework","genai-hr-p30":"comparison",
  "genai-hr-p31":"framework","genai-hr-p32":"data-visualization","genai-hr-p33":"ranked",
  "genai-hr-p34":"framework","genai-hr-p35":"back-cover",
  "genai-marketing-p01":"cover","genai-marketing-p02":"text-heavy","genai-marketing-p03":"framework",
  "genai-marketing-p04":"exec-summary","genai-marketing-p05":"framework","genai-marketing-p06":"process",
  "genai-marketing-p07":"big-number","genai-marketing-p08":"case-study","genai-marketing-p09":"process",
  "genai-marketing-p10":"process","genai-marketing-p11":"framework","genai-marketing-p12":"case-study",
  "genai-marketing-p13":"case-study","genai-marketing-p14":"case-study","genai-marketing-p15":"framework",
  "genai-marketing-p16":"case-study","genai-marketing-p17":"data-visualization",
  "genai-marketing-p18":"framework","genai-marketing-p19":"table","genai-marketing-p20":"ranked",
  "genai-marketing-p21":"data-visualization","genai-marketing-p22":"table",
  "genai-marketing-p23":"data-visualization","genai-marketing-p24":"framework",
  "genai-marketing-p25":"ranked","genai-marketing-p26":"framework","genai-marketing-p27":"back-cover",
  "ai-cost-advantage-p01":"cover","ai-cost-advantage-p02":"text-heavy",
  "ai-cost-advantage-p03":"exec-summary","ai-cost-advantage-p04":"big-number",
  "ai-cost-advantage-p05":"framework","ai-cost-advantage-p06":"framework",
  "ai-cost-advantage-p07":"framework","ai-cost-advantage-p08":"table",
  "ai-cost-advantage-p09":"big-number","ai-cost-advantage-p10":"case-study",
  "ai-cost-advantage-p11":"case-study","ai-cost-advantage-p12":"case-study",
  "ai-cost-advantage-p13":"case-study","ai-cost-advantage-p14":"ranked",
  "ai-cost-advantage-p15":"big-number","ai-cost-advantage-p16":"data-visualization",
  "ai-cost-advantage-p17":"framework","ai-cost-advantage-p18":"exec-summary",
  "ai-cost-advantage-p19":"table","ai-cost-advantage-p20":"back-cover",
  "ai-engineering-p01":"cover","ai-engineering-p02":"text-heavy","ai-engineering-p03":"exec-summary",
  "ai-engineering-p04":"big-number","ai-engineering-p05":"ranked","ai-engineering-p06":"table",
  "ai-engineering-p07":"matrix","ai-engineering-p08":"data-visualization",
  "ai-engineering-p09":"framework","ai-engineering-p10":"process","ai-engineering-p11":"table",
  "ai-engineering-p12":"ranked","ai-engineering-p13":"data-visualization",
  "ai-engineering-p14":"framework","ai-engineering-p15":"data-visualization",
  "ai-engineering-p16":"framework","ai-engineering-p17":"process","ai-engineering-p18":"comparison",
  "ai-engineering-p19":"table","ai-engineering-p20":"table","ai-engineering-p21":"matrix",
  "ai-engineering-p22":"ranked","ai-engineering-p23":"ranked","ai-engineering-p24":"table",
  "ai-engineering-p25":"back-cover",
  "bcg-cost-p01":"cover","bcg-cost-p02":"text-heavy","bcg-cost-p03":"exec-summary",
  "bcg-cost-p04":"agenda","bcg-cost-p05":"data-visualization","bcg-cost-p06":"big-number",
  "bcg-cost-p07":"data-visualization","bcg-cost-p08":"data-visualization","bcg-cost-p09":"big-number",
  "bcg-cost-p10":"agenda","bcg-cost-p11":"ranked","bcg-cost-p12":"ranked","bcg-cost-p13":"table",
  "bcg-cost-p14":"process","bcg-cost-p15":"data-visualization","bcg-cost-p16":"data-visualization",
  "bcg-cost-p17":"agenda","bcg-cost-p18":"framework","bcg-cost-p19":"ranked",
  "bcg-cost-p20":"data-visualization","bcg-cost-p21":"ranked","bcg-cost-p22":"table",
  "bcg-cost-p23":"text-heavy","bcg-cost-p24":"back-cover",
  "mckinsey-nature-p01":"cover","mckinsey-nature-p02":"agenda","mckinsey-nature-p03":"table",
  "mckinsey-nature-p04":"data-visualization","mckinsey-nature-p05":"framework",
  "mckinsey-nature-p06":"framework","mckinsey-nature-p07":"table",
  "mckinsey-nature-p08":"data-visualization","mckinsey-nature-p09":"data-visualization",
  "mckinsey-nature-p10":"framework","mckinsey-nature-p11":"framework",
}

OUT = Path("/Users/noname/deep-briefing/core/style/ref-specs/slide-catalog.json")

counts = Counter(IMAGE_CLASSIFICATIONS.values())
result = {
    "total": len(IMAGE_CLASSIFICATIONS),
    "method": "image-based (3 agents × 72p batches)",
    "type_counts": dict(counts.most_common()),
    "catalog": IMAGE_CLASSIFICATIONS,
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"총 {len(IMAGE_CLASSIFICATIONS)}p 분류 완료")
print(f"유형 수: {len(counts)}")
for t, c in counts.most_common():
    print(f"  {t}: {c}개 ({c/len(IMAGE_CLASSIFICATIONS)*100:.1f}%)")
