"""一键运行：python run.py [medical|social|decision|llm]"""
import sys
import importlib

DEMOS = {
    "medical":  "examples.demo_medical",
    "social":   "examples.demo_social",
    "decision": "examples.demo_decision",
    "llm":      "examples.demo_llm",
}


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "decision"
    if name not in DEMOS:
        print(f"可用案例: {list(DEMOS.keys())}")
        return
    importlib.import_module(DEMOS[name])


if __name__ == "__main__":
    main()
