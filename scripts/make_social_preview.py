"""生成 GitHub social preview 图（1280x640，OG 推荐尺寸）

输出到 docs/social-preview.png，可直接拖到 GitHub 网页端
Settings → General → Social preview 上传。
"""
import asyncio, os
from playwright.async_api import async_playwright

OUT = "/Users/shenzhiheng/.claude-internal/skills/universal-pitfall-detector/docs/social-preview.png"

HTML = """<!DOCTYPE html>
<html><head><meta charset='UTF-8'>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=Inter:wght@600;700&display=swap');
  body { margin: 0; width: 1280px; height: 640px;
         background: #fafaf7;
         font-family: 'Source Serif 4','Songti SC','Noto Serif SC',Georgia,serif;
         display: flex; flex-direction: column;
         padding: 64px 72px;
         box-sizing: border-box;
         color: #1a1a1a;
         border-top: 6px solid #8B0000; }
  .badge { font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 700;
           letter-spacing: 0.22em; color: #8B0000; text-transform: uppercase; }
  h1 { font-size: 76px; font-weight: 700; line-height: 1.05;
       margin: 24px 0 16px; }
  .sub { font-size: 22px; font-style: italic; color: #404040;
         margin: 0 0 32px; max-width: 860px; line-height: 1.5; }
  .pills { display: flex; flex-wrap: wrap; gap: 8px;
           margin-top: 8px; max-width: 1000px; }
  .pill { font-family: 'Inter',sans-serif; font-size: 14px; font-weight: 500;
          background: #fff; border: 1px solid #d8d8d8;
          color: #404040;
          padding: 6px 14px; border-radius: 999px; }
  mark { background: linear-gradient(180deg, transparent 55%, #FFE066 55%, #FFE066 92%, transparent 92%);
         padding: 0 4px; font-weight: 700; }
  .footer { position: absolute; bottom: 56px; left: 72px;
            font-family: 'Inter', sans-serif; font-size: 14px;
            color: #6b6b6b; letter-spacing: 0.05em; }
  .accent { color: #8B0000; font-weight: 700; }
</style></head>
<body>
  <div class="badge">A Claude Code Skill · 统计陷阱检测器</div>
  <h1>Universal<br>Pitfall Detector</h1>
  <div class="sub">
    给「<mark>研究显示</mark>」「<mark>NN% 有效率</mark>」「<mark>人人在用</mark>」<br>
    这类论断装一个 BS 检测器
  </div>
  <div class="pills">
    <span class="pill">辛普森悖论</span>
    <span class="pill">幸存者偏差</span>
    <span class="pill">相对风险夸大</span>
    <span class="pill">软硬终点偷换</span>
    <span class="pill">效应量微小</span>
    <span class="pill">基率谬误</span>
    <span class="pill">选择偏差</span>
    <span class="pill">数据污染</span>
    <span class="pill">多重比较</span>
  </div>
  <div class="footer">
    github.com/Faust-Donf/universal-pitfall-detector ·
    <span class="accent">9 类陷阱</span> · 学术杂志 HTML 报告 · MIT
  </div>
</body></html>"""


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(
            viewport={"width": 1280, "height": 640},
            device_scale_factor=2,
        )
        page = await ctx.new_page()
        await page.set_content(HTML)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(500)
        await page.screenshot(path=OUT, full_page=False, omit_background=False,
                              clip={"x": 0, "y": 0, "width": 1280, "height": 640})
        await browser.close()
    print(f"✓ Social preview saved: {OUT}")


if __name__ == "__main__":
    asyncio.run(main())
