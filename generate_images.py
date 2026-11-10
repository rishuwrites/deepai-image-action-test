import asyncio
import json
import re
from pathlib import Path

from playwright.async_api import async_playwright


OUTPUT_DIR = Path("output")
GENERATOR_URL = "https://deepai.org/machine-learning-model/text2img"
IMAGE_URL_PREFIX = "https://api.deepai.org/job-view-file/"
PROMPTS = [
    "A red fox resting in an autumn forest, warm watercolor illustration, no text",
    "A tiny lighthouse on a rocky coast at sunrise, soft gouache painting, no text",
    "A glass greenhouse filled with tropical plants, editorial photography, no text",
    "A floating market at dawn with colorful boats, storybook illustration, no text",
    "A cozy cabin beneath the northern lights, cinematic digital painting, no text",
    "A close-up of a monarch butterfly on a purple flower, macro nature photography",
    "A quiet Japanese garden with a koi pond in spring, watercolor illustration",
    "A mountain train crossing a stone viaduct, misty landscape painting, no text",
    "A colorful hot air balloon festival over a valley, vibrant illustration",
    "A bowl of fresh fruit on a sunlit kitchen table, still life oil painting",
    "An old observatory under a star-filled night sky, detailed concept art",
    "A sea turtle swimming above a coral reef, vivid underwater photography",
    "A treehouse connected by rope bridges in a forest, whimsical illustration",
    "A traditional pottery workshop with sunlight through the window, no text",
    "A desert canyon after rain with a small river, cinematic landscape art",
    "A playful red panda sitting among bamboo leaves, soft pastel illustration",
    "A city street in the rain with warm reflections, impressionist painting",
    "A field of sunflowers beneath a cloudy summer sky, bright oil painting",
    "A friendly robot watering flowers on a balcony, children's book illustration",
    "A peaceful snowy village at blue hour with glowing windows, no text",
]


def is_block_page(text: str) -> bool:
    lowered = text.lower()
    return any(
        marker in lowered
        for marker in (
            "verify you are human",
            "are you a human",
            "captcha",
            "unusual traffic",
            "rate limit",
            "too many requests",
        )
    )


async def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = OUTPUT_DIR / "manifest.json"
    results: list[dict[str, str]] = []

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        try:
            response = await page.goto(
                GENERATOR_URL,
                wait_until="domcontentloaded",
                timeout=60_000,
            )
            if response is None or response.status >= 400:
                status = response.status if response else "no response"
                raise RuntimeError(f"DeepAI page did not load successfully: {status}")
            await page.locator("#generate-textarea").wait_for(timeout=30_000)

            for index, prompt in enumerate(PROMPTS, start=1):
                try:
                    body_text = await page.locator("body").inner_text(timeout=10_000)
                    if is_block_page(body_text):
                        raise RuntimeError(
                            "DeepAI displayed a CAPTCHA, verification, or rate-limit page; "
                            "stopping without attempting to bypass it."
                        )

                    previous_urls = set(
                        await page.locator("main img").evaluate_all(
                            """(images, prefix) =>
                                images.map(image => image.currentSrc || image.src)
                                    .filter(src => src.startsWith(prefix))""",
                            IMAGE_URL_PREFIX,
                        )
                    )

                    await page.locator("#generate-textarea").fill(prompt)
                    submit = page.locator("#modelSubmitButton")
                    await submit.wait_for(state="visible", timeout=10_000)
                    await submit.click()

                    await page.wait_for_function(
                        """({prefix, previous}) =>
                            [...document.querySelectorAll('main img')]
                                .some(image => {
                                    const src = image.currentSrc || image.src;
                                    return src.startsWith(prefix) && !previous.includes(src);
                                })""",
                        arg={"prefix": IMAGE_URL_PREFIX, "previous": list(previous_urls)},
                        timeout=180_000,
                    )

                    image_urls = await page.locator("main img").evaluate_all(
                        """(images, args) => {
                            const image = images.find(element => {
                                const src = element.currentSrc || element.src;
                                return src.startsWith(args.prefix) && !args.previous.includes(src);
                            });
                            return image ? [image.currentSrc || image.src] : [];
                        }""",
                        {"prefix": IMAGE_URL_PREFIX, "previous": list(previous_urls)},
                    )
                    image_url = image_urls[0] if image_urls else None
                    if not image_url:
                        raise RuntimeError("Generation completed but no output image was found.")

                    download = await page.request.get(image_url, timeout=60_000)
                    if not download.ok:
                        raise RuntimeError(f"Image download failed with HTTP {download.status}.")
                    image_bytes = await download.body()
                    if not image_bytes.startswith(b"\xff\xd8\xff"):
                        raise RuntimeError("Downloaded output was not a JPEG image.")

                    image_path = OUTPUT_DIR / f"image-{index:02}.jpg"
                    image_path.write_bytes(image_bytes)
                    results.append(
                        {
                            "index": str(index),
                            "status": "generated",
                            "prompt": prompt,
                            "file": image_path.name,
                        }
                    )
                    print(f"Generated {image_path.name} ({len(image_bytes)} bytes)")

                    if index < len(PROMPTS):
                        await page.wait_for_timeout(5_000)
                except Exception as error:
                    results.append(
                        {
                            "index": str(index),
                            "status": "failed",
                            "prompt": prompt,
                            "error": re.sub(r"\s+", " ", str(error))[:500],
                        }
                    )
                    print(f"Image {index} failed: {error}")
                    if is_block_page(await page.locator("body").inner_text()):
                        break
        finally:
            manifest_path.write_text(
                json.dumps(results, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            await browser.close()

    generated = sum(result["status"] == "generated" for result in results)
    print(f"Generated {generated} of {len(PROMPTS)} requested images.")
    if generated != len(PROMPTS):
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
