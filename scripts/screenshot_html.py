"""用 Playwright 截鱼油报告 HTML 各关键区域，输出 PNG 用于 README 配图"""
import asyncio
import os
from playwright.async_api import async_playwright

HTML_PATH = "/Users/shenzhiheng/Documents/Projects/统计陷阱/鱼油分析/报告.html"
OUT_DIR = "/Users/shenzhiheng/.claude-internal/skills/universal-pitfall-detector/docs/screenshots"
os.makedirs(OUT_DIR, exist_ok=True)


SHOTS = [
    {"name": "01_full_overview.png", "selector": ".paper", "full_page": False, "viewport_h": 1600},
    {"name": "02_masthead_abstract.png", "selectors": [".masthead", ".title", ".subtitle", ".authors", ".abstract"]},
    {"name": "03_kpis.png", "selector": ".kpi-row"},
    {"name": "04_abstract_highlight.png", "selector": ".abstract"},
    {"name": "05_figure_grid.png", "selector": ".figure-grid"},
    {"name": "06_positive_findings.png", "selector": ".positive"},
    {"name": "07_pitfall_table.png", "selector_nth": ("table.data", 0)},
    {"name": "08_pitfall_detail.png", "selectors_first_n": (".pitfall", 3)},
    {"name": "09_scenario_table.png", "selector_nth": ("table.data", 1)},
    {"name": "10_recommendations.png", "selector": ".recs"},
    {"name": "11_five_questions.png", "selector": ".five"},
]


async def shoot(page, shot):
    name = shot["name"]
    out = os.path.join(OUT_DIR, name)

    if "selector" in shot:
        loc = page.locator(shot["selector"]).first
        await loc.scroll_into_view_if_needed()
        await loc.screenshot(path=out)
    elif "selector_nth" in shot:
        sel, idx = shot["selector_nth"]
        loc = page.locator(sel).nth(idx)
        await loc.scroll_into_view_if_needed()
        await loc.screenshot(path=out)
    elif "selectors" in shot:
        # 包裹多个连续元素：截最外层 .paper 的指定上下区间
        # 简单做法：截 .paper 全图，让用户用第一张做缩略
        loc = page.locator(shot["selectors"][0]).first
        last = page.locator(shot["selectors"][-1]).first
        bbox1 = await loc.bounding_box()
        bbox2 = await last.bounding_box()
        if bbox1 and bbox2:
            top = bbox1["y"]
            bottom = bbox2["y"] + bbox2["height"]
            await page.screenshot(
                path=out,
                clip={"x": bbox1["x"] - 10, "y": top - 10,
                      "width": bbox1["width"] + 20,
                      "height": bottom - top + 20},
            )
    elif "selectors_first_n" in shot:
        sel, n = shot["selectors_first_n"]
        first = page.locator(sel).nth(0)
        last = page.locator(sel).nth(n - 1)
        bbox1 = await first.bounding_box()
        bbox2 = await last.bounding_box()
        if bbox1 and bbox2:
            top = bbox1["y"]
            bottom = bbox2["y"] + bbox2["height"]
            await page.screenshot(
                path=out,
                clip={"x": bbox1["x"] - 10, "y": top - 10,
                      "width": bbox1["width"] + 20,
                      "height": bottom - top + 20},
            )

    print(f"  ✓ {name}")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(
            viewport={"width": 1100, "height": 1600},
            device_scale_factor=2,  # Retina 截图
        )
        page = await ctx.new_page()
        await page.goto(f"file://{HTML_PATH}")
        # 等字体渲染
        await page.wait_for_timeout(800)

        print("正在截图...")
        for shot in SHOTS:
            try:
                await shoot(page, shot)
            except Exception as e:
                print(f"  ✗ {shot['name']}: {e}")

        await browser.close()
    print(f"\n截图保存到: {OUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
