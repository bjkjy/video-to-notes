#!/usr/bin/env python3
"""video-to-notes deterministic grader — 内容类型无关的结构完整性检查"""

import json
import os
import sys
import re


def grade(filepath: str) -> dict:
    if not os.path.isfile(filepath):
        return {"pass": False, "reason": "file_not_found", "score": 0.0}

    size = os.path.getsize(filepath)
    if size < 100:
        return {"pass": False, "reason": "file_too_small", "score": 0.0}

    with open(filepath, encoding="utf-8", errors="replace") as f:
        content = f.read()

    checks = {}
    total = 0
    passed = 0

    total += 1
    c1 = size >= 1024
    checks["file_size_ok"] = c1
    passed += int(c1)

    total += 1
    c2 = any(kw in content.lower() for kw in ["思维导图", "mind map", "mermaid"])
    checks["has_mind_map"] = c2
    passed += int(c2)

    # 通用的对比内容检测：找含对比关键词的表格/章节
    total += 1
    comparison_kws = ["对比", "vs", "比较", "区别", "差异", "versus", "comparison",
                      "对比如下", "选择", "推荐方案"]
    c3 = any(kw in content.lower() for kw in comparison_kws)
    checks["has_comparative_content"] = c3
    passed += int(c3)

    total += 1
    guide_kws = ["选择指南", "决策树", "decision tree", "推荐", "适用场景",
                 "建议", "方案", "什么时候", "按场景"]
    c4 = any(kw in content.lower() for kw in guide_kws)
    checks["has_guidance"] = c4
    passed += int(c4)

    total += 1
    c5 = any(kw in content.lower() for kw in ["总结", "summary", "核心要点",
                                               "回顾", "takeaway", "执行摘要",
                                               "关键要点", "摘要"])
    checks["has_summary"] = c5
    passed += int(c5)

    total += 1
    c6 = bool(re.search(r"^##\s+\S", content, re.MULTILINE))
    checks["has_chapters"] = c6
    passed += int(c6)

    total += 1
    c7 = "|" in content and "|---" in content
    checks["has_table"] = c7
    passed += int(c7)

    score = passed / total if total > 0 else 0.0
    if score >= 0.9:
        grade = "A"
    elif score >= 0.75:
        grade = "B"
    elif score >= 0.6:
        grade = "C"
    else:
        grade = "D"

    return {
        "pass": score >= 0.7,
        "grade": grade,
        "score": round(score, 2),
        "checks_passed": passed,
        "checks_total": total,
        "checks": checks,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: deterministic_grader.py <note_file.md> [label]")
        sys.exit(1)

    filepath = sys.argv[1]
    label = sys.argv[2] if len(sys.argv) > 2 else "unknown"

    result = grade(filepath)
    result["label"] = label
    result["filepath"] = filepath

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
