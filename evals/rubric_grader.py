#!/usr/bin/env python3
"""video-to-notes rubric grader — 内容类型无关的 4 维度质量评分"""

import json
import os
import re
import sys


RUBRIC = {
    "completeness": {
        "weight": 0.3,
        "description": "内容完整性 — 是否覆盖核心概念和要点",
        "criteria": [
            ("has_title", "有标题", lambda c: bool(re.search(r"^#\s+\S", c, re.MULTILINE))),
            ("has_source_info", "有来源信息", lambda c: "视频来源" in c or "来源" in c or "source" in c.lower()),
            ("has_chapters", "有章节划分（>=3章）",
             lambda c: len(re.findall(r"^##\s+\S", c, re.MULTILINE)) >= 3),
        ],
    },
    "structure": {
        "weight": 0.3,
        "description": "结构清晰度 — 思维导图、层级、排版",
        "criteria": [
            ("has_mind_map", "有思维导图", lambda c: "思维导图" in c or "mind map" in c.lower() or "```mermaid" in c),
            ("has_table_or_list", "有表格或列表",
             lambda c: ("|" in c and "|---" in c) or len(re.findall(r"^\s*[-*]\s", c, re.MULTILINE)) >= 3),
            ("consistent_headers", "标题层级一致", lambda c: _check_header_consistency(c)),
        ],
    },
    "accuracy": {
        "weight": 0.2,
        "description": "准确性 — 无幻觉、内容充实",
        "criteria": [
            ("no_placeholder", "无占位符内容", lambda c: "待补充" not in c and "TODO" not in c and "{{" not in c),
            ("reasonable_length", "内容充实（>500字）", lambda c: len(c) > 500),
        ],
    },
    "reviewability": {
        "weight": 0.2,
        "description": "可复习性 — 便于后续回顾",
        "criteria": [
            ("has_summary_section", "有开头的概览或结尾的总结",
             lambda c: bool(re.search(r"^##?\s*(总结|概述|概览|概要|执行摘要|关键要点|abstract|summary)", c, re.MULTILINE | re.IGNORECASE))),
            ("has_bullet_takeaways", "有要点提炼（列表/注意事项）",
             lambda c: any(kw in c.lower() for kw in ["要点", "注意", "建议", "推荐", "最佳实践",
                                                       "tips", "提示", "warning", "关键"])),
            ("has_actionable_content", "有可操作的内容（步骤/选择指南/决策）",
             lambda c: any(kw in c.lower() for kw in ["步骤", "选择", "推荐", "适用场景", "方案推荐",
                                                       "按场景", "决策", "workflow", "流程",
                                                       "何时用", "什么时候"])),
        ],
    },
}


def _check_header_consistency(content: str) -> bool:
    lines = content.split("\n")
    levels = []
    for line in lines:
        m = re.match(r"^(#{1,6})\s", line)
        if m:
            levels.append(len(m.group(1)))
    if not levels:
        return False
    return max(levels) <= 4


def grade(content: str) -> dict:
    dimensions = {}
    total_score = 0.0

    for dim_name, dim in RUBRIC.items():
        dim_results = {}
        dim_passed = 0
        dim_total = len(dim["criteria"])
        for criterion in dim["criteria"]:
            key, desc, fn = criterion
            passed = fn(content)
            dim_results[key] = {"description": desc, "pass": passed}
            dim_passed += int(passed)

        dim_score = dim_passed / dim_total if dim_total > 0 else 0.0
        dimensions[dim_name] = {
            "score": round(dim_score, 2),
            "weight": dim["weight"],
            "passed": dim_passed,
            "total": dim_total,
            "description": dim["description"],
            "checks": dim_results,
        }
        total_score += dim_score * dim["weight"]

    if total_score >= 0.9:
        grade = "A"
    elif total_score >= 0.75:
        grade = "B"
    elif total_score >= 0.6:
        grade = "C"
    else:
        grade = "D"

    return {
        "total_score": round(total_score, 2),
        "grade": grade,
        "dimensions": dimensions,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: rubric_grader.py <note_file.md> [label]")
        sys.exit(1)

    filepath = sys.argv[1]
    label = sys.argv[2] if len(sys.argv) > 2 else "unknown"

    if not os.path.isfile(filepath):
        print(json.dumps({"error": "file_not_found", "filepath": filepath}, ensure_ascii=False))
        sys.exit(1)

    with open(filepath, encoding="utf-8", errors="replace") as f:
        content = f.read()

    result = grade(content)
    result["label"] = label
    result["filepath"] = filepath

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["total_score"] >= 0.65 else 1)


if __name__ == "__main__":
    main()
