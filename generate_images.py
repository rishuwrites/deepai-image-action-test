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
    "A cozy wooden cabin tucked into snowy pine trees, vintage storybook illustration, no text",
    "A vintage blue bicycle parked against a stone wall covered in ivy, impressionist oil painting, no text",
    "A steaming cup of tea on a rustic wooden windowsill with falling rain outside, cozy digital art, no text",
    "A majestic stag standing in a misty morning meadow, ethereal watercolor, no text",
    "A sleepy ginger cat curled up on a stack of old books, warm acrylic painting, no text",
    "A rustic Italian village nestled among rolling green hills at golden hour, watercolor and ink, no text",
    "A glowing glass terrarium filled with tiny ferns and mushrooms, whimsical botanical illustration, no text",
    "A lone astronaut gazing at a distant ringed planet from a crater, cinematic concept art, no text",
    "A vibrant coral reef teeming with colorful tropical fish and sunbeams, detailed digital painting, no text",
    "A steaming bowl of ramen with soft-boiled egg and green onions, vibrant anime style art, no text",
    "A medieval castle perched high on a dramatic fog-shrouded cliff, epic fantasy illustration, no text",
    "A stack of colorful vintage suitcases with travel stickers, charming gouache painting, no text",
    "A mysterious glowing portal hidden deep within an ancient magical forest, fantasy digital art, no text",
    "A golden retriever puppy chasing autumn leaves in a sunlit park, warm cinematic photography, no text",
    "A vintage radio sitting on a wooden desk next to a potted cactus, retro aesthetic digital art, no text",
    "A traditional Japanese pagoda surrounded by blooming pink cherry blossoms, ukiyo-e inspired art, no text",
    "A sleek futuristic sports car driving through a neon-lit cyberpunk city at night, vibrant digital render, no text",
    "A magical treehouse glowing warmly in the twilight of an enchanted forest, whimsical fantasy art, no text",
    "A delicate monarch butterfly resting on a purple lavender blossom, macro nature photography, no text",
    "A rustic bakery window filled with freshly baked artisan bread and pastries, warm cozy illustration, no text",
    "A majestic snowy mountain peak reflecting in a crystal-clear alpine lake, landscape photography, no text",
    "A cute little owl perched on a mossy branch under a starry night sky, digital storybook illustration, no text",
    "A collection of antique brass pocket watches and compasses on a dark wooden table, still life painting, no text",
    "A field of vibrant red poppies swaying gently in a summer breeze, impressionist painting, no text",
    "A futuristic floating city in the clouds with flying vehicles, sci-fi concept art, no text",
    "A cup of hot cocoa with melting marshmallows and cinnamon sticks, cozy watercolor, no text",
    "A sleepy little red panda napping on a tree branch, charming wildlife illustration, no text",
    "A mystical crystal ball glowing with swirling starry galaxies inside, fantasy digital art, no text",
    "A lonely park bench under a streetlamp on a quiet, foggy autumn evening, moody atmospheric painting, no text",
    "A bright yellow camper van parked by a serene pine-fringed lake at sunset, vintage illustration, no text",
    "A whimsical hot air balloon floating over a patchwork quilt of green fields, dreamy digital art, no text",
    "A sleek black cat sitting gracefully on a velvet armchair, elegant digital painting, no text",
    "An ancient stone bridge arching over a babbling brook in a lush green valley, classical landscape painting, no text",
    "A plate of freshly rolled sushi with chopsticks and bamboo mat, vibrant food illustration, no text",
    "A tiny mouse wearing a knitted sweater reading a book, whimsical children's book illustration, no text",
    "A magnificent glowing nebula swirling in deep space with distant star clusters, astronomical art, no text",
    "A rustic wooden dock stretching out into a calm turquoise tropical sea, serene travel photography, no text",
    "A stack of fluffy pancakes dripping with golden maple syrup and butter, appetizing food photography, no text",
    "A cute baby elephant playing playfully in muddy water, heartwarming wildlife photography, no text",
    "A vintage typewriter resting on a cluttered desk with loose sheets of paper, moody retro art, no text",
    "A magical floating island with waterfalls cascading into the clouds, epic fantasy illustration, no text",
    "A colorful parrot perched on a branch in a dense, sun-dappled tropical rainforest, vivid wildlife art, no text",
    "A steaming ceramic mug of coffee with latte art shaped like a heart, cozy café photography, no text",
    "A futuristic robotic hand holding a glowing holographic butterfly, sci-fi concept art, no text",
    "A charming French street café with small round tables and red awnings, watercolor sketch, no text",
    "A tiny frog sitting on a giant wet lily pad after a summer rain, macro nature photography, no text",
    "An intricate stained glass window casting colorful light across a cathedral floor, atmospheric photography, no text",
    "A friendly golden retriever wearing a yellow raincoat on a rainy street, cute digital illustration, no text",
    "A glowing jack-o'-lantern sitting on a spooky haunted porch on Halloween night, dark fantasy art, no text",
    "A sleek white yacht sailing across deep blue ocean waves on a sunny day, marine photography, no text",
    "A plate of colorful French macarons arranged neatly on a pastel background, elegant food photography, no text",
    "A magical glowing mushroom forest illuminated by bioluminescent flora, fantasy concept art, no text",
    "A vintage globe and a stack of old leather-bound books on a study table, classic still life, no text",
    "A majestic bald eagle soaring proudly across a bright blue sky, wildlife photography, no text",
    "A charming Parisian balcony overflowing with blooming red geraniums, romantic watercolor, no text",
    "A futuristic cyberpunk street vendor selling glowing noodles at night, moody digital painting, no text",
    "A cozy reading nook with a plush armchair, warm floor lamp, and bookshelves, interior design art, no text",
    "A playful dolphin leaping out of crystal-clear ocean waves at sunset, dynamic marine photography, no text",
    "A delicate snowflake resting on a dark wool mitten in winter, macro photography, no text",
    "A colorful hot air balloon festival filling a golden morning sky, vibrant landscape painting, no text",
    "A mysterious ancient temple ruin overgrown with thick jungle vines, adventure concept art, no text",
    "A fluffy Pomeranian puppy sitting on a soft white fur rug, adorable pet photography, no text",
    "A bowl of fresh summer berries including strawberries, blueberries, and raspberries, vibrant food art, no text",
    "A sleek silver jet flying high above a sea of fluffy white clouds at sunset, aviation photography, no text",
    "A quaint English cottage with a thatched roof and a wild English garden, picturesque watercolor, no text",
    "A futuristic cyborg warrior standing in a ruined, rain-slicked city street, sci-fi concept art, no text",
    "A glass bottle containing a miniature sailing ship on a wooden shelf, nautical still life, no text",
    "A majestic waterfall plunging into a hidden lagoon surrounded by ferns, lush nature photography, no text",
    "A cute chubby hamster nibbling on a sunflower seed, adorable macro animal photography, no text",
    "A vintage telephone sitting on a lace doily on a wooden side table, nostalgic retro art, no text",
    "A magical wizard's desk covered in spellbooks, potion bottles, and glowing runes, fantasy illustration, no text",
    "A field of bright yellow sunflowers turning toward a warm summer sun, cheerful landscape painting, no text",
    "A steaming bowl of spicy pho with herbs and lime slices, appetizing food photography, no text",
    "A tiny fairy sleeping peacefully inside the petals of a blooming lotus flower, whimsical digital art, no text",
    "A sleek electric vehicle charging at a modern station during a neon-lit twilight, futuristic art, no text",
    "A tranquil Zen garden with raked white sand, smooth smooth river stones, and bonsai, minimalist photography, no text",
    "A stack of colorful children's building blocks on a bright wooden floor, playful minimalist art, no text",
    "A majestic polar bear walking across vast sheet ice in the Arctic wilderness, wildlife photography, no text",
    "A rustic wooden table set for a candlelit dinner outdoors under fairy lights, romantic evening art, no text",
    "A vintage camera with a leather strap resting on a topographical map, adventure travel aesthetic, no text",
    "A glowing neon sign buzzing brightly in a dark rainy alleyway, cyberpunk photography, no text",
    "A cute fluffy bunny rabbit sitting peacefully in a field of daisies, charming spring illustration, no text",
    "An ancient viking ship navigating through icy, choppy northern seas, dramatic historical art, no text",
    "A tall stack of fluffy buttermilk pancakes with melting butter and blueberries, cozy breakfast art, no text",
    "A futuristic lunar base on the dusty gray surface of the moon with Earth rising, sci-fi art, no text",
    "A classic acoustic guitar leaning against a vintage amplifier in a sunny room, musical aesthetic art, no text",
    "A vibrant school of glowing jellyfish drifting through deep ocean darkness, mesmerizing marine art, no text",
    "A tiny wooden birdhouse hanging from a blossoming apple tree branch in spring, gentle watercolor, no text",
    "A luxurious modern living room with floor-to-ceiling windows overlooking a city skyline, interior design art, no text",
    "A steaming hot bowl of creamy tomato soup with a grilled cheese sandwich, comforting food art, no text",
    "A mysterious cloaked traveler walking down a foggy cobblestone street in an old European town, moody art, no text",
    "A cute orange tabby cat stretching lazily on a sunny wooden floor, cozy pet photography, no text",
    "A breathtaking view of the Northern Lights dancing across a starry winter night sky, nature photography, no text",
    "A vintage record player spinning a vinyl disc with warm ambient lighting, nostalgic retro art, no text",
    "A cheerful sunflower patch buzzing with bumblebees under a bright blue summer sky, vivid painting, no text",
    "A futuristic glass dome city nestled within a barren alien canyon landscape, sci-fi concept art, no text",
    "A rustic ceramic teapot and matching teacups on a woven bamboo mat, minimalist tea ceremony art, no text",
    "A majestic white tiger walking stealthily through tall green jungle grass, wildlife photography, no text",
    "A classic red telephone box standing on a rainy London street with blurred traffic, atmospheric photography, no text",
    "A delicious slice of New York style cheesecake topped with fresh strawberries, appetizing food art, no text",
    "A whimsical tree carved into a giant smiling face in an enchanted forest, fantasy illustration, no text",
    "A sleek silver wristwatch resting on a dark leather texture background, luxury product photography, no text",
    "A peaceful mountain stream winding its way through a forest of tall pine trees, serene nature photography, no text",
    "A cute little hedgehog exploring a patch of green moss and mushrooms, adorable wildlife photography, no text",
    "A vintage globe illuminated from within on a dark wooden bookshelf, classic academic art, no text",
    "A futuristic flying drone delivering a small package over a high-tech city, sci-fi illustration, no text",
    "A charming Venetian canal with a traditional gondola passing under an arched bridge, watercolor painting, no text",
    "A warm bowl of oatmeal topped with sliced bananas, chia seeds, and honey, healthy breakfast art, no text",
    "A magical floating crystal castle glowing with ethereal blue light in the clouds, fantasy art, no text",
    "A sleek black sports car accelerating down a coastal highway at sunset, dynamic automotive photography, no text",
    "A cozy corner of a greenhouse filled with lush tropical plants and hanging ferns, botanical art, no text",
    "A playful otter floating on its back in a calm river holding a smooth pebble, wildlife photography, no text",
    "A collection of colorful glass spice jars neatly arranged on a rustic kitchen shelf, still life art, no text",
    "An epic battle scene between futuristic mechs and giant monsters in a ruined city, cinematic concept art, no text",
    "A delicate glass of sparkling champagne with rising bubbles at a festive celebration, event photography, no text",
    "A tranquil bamboo forest with tall green stalks filtering bright morning sunlight, serene nature art, no text",
    "A cute little squirrel holding an acorn on a mossy log in a golden autumn forest, wildlife photography, no text",
    "A vintage leather armchair positioned next to a glowing fireplace on a winter night, cozy interior art, no text",
    "A breathtaking aerial view of a winding turquoise river cutting through a green canyon, landscape photography, no text",
    "A steaming bowl of creamy mushroom risotto garnished with fresh herbs, gourmet food photography, no text",
    "A magical floating hot air balloon shaped like a giant sleeping whale, whimsical fantasy art, no text",
    "A classic fountain pen resting on a blank parchment journal with ink splatters, artistic still life, no text",
    "A majestic bald eagle perched proudly on a snow-covered pine branch in winter, wildlife photography, no text",
    "A futuristic holographic interface glowing in front of a scientist's eyes, sci-fi digital art, no text",
    "A rustic wooden picnic table set with a checkered cloth and a basket of apples, pastoral art, no text",
    "A cute baby panda munching happily on a fresh bamboo shoot, adorable wildlife photography, no text",
    "A glowing neon arcade cabinet glowing brightly in a retro dark room, nostalgic gaming art, no text",
    "A picturesque windmill standing tall beside a Dutch tulip field in full bloom, landscape painting, no text",
    "A plate of golden crispy French fries served with ketchup in a diner, appetizing food photography, no text",
    "A mysterious glowing crystal cave filled with sparkling stalactites and underground pools, fantasy art, no text",
    "An elegant ballerina performing a graceful leap on a dimly lit stage, dramatic dance photography, no text",
    "A cozy corner of a bedroom with fairy lights stringing across a whitewashed brick wall, interior art, no text",
    "A sleek futuristic passenger train speeding across a desert landscape at sunrise, sci-fi photography, no text",
    "A vibrant bowl of fresh poke with tuna, avocado, sesame seeds, and rice, appetizing food art, no text",
    "A charming cobblestone alleyway in an old European town lit by warm lanterns at dusk, atmospheric art, no text",
    "A cute fluffy duckling swimming across a calm pond reflecting green reeds, wildlife photography, no text",
    "A vintage rotary telephone sitting on a stack of hardcover books, nostalgic retro art, no text",
    "A magical glowing tree standing alone on a grassy hill under a swirling purple nebula, fantasy art, no text",
    "A traditional Japanese sushi chef carefully preparing nigiri behind a wooden counter, cultural art, no text",
    "A breathtaking view of a massive glacier cracking into a deep blue arctic sea, landscape photography, no text",
    "A warm mug of spiced apple cider with floating cinnamon sticks on a wooden table, cozy fall art, no text",
    "A sleek white racing yacht cutting sharply through deep blue ocean waves, dynamic marine photography, no text",
    "A whimsical toadstool house with a little round wooden door and chimney smoke, fairy tale art, no text",
    "A modern minimalist kitchen with marble countertops and sleek black cabinets, interior design art, no text",
    "A playful red fox kit bouncing playfully in a vibrant green meadow, wildlife photography, no text",
    "A vintage leather suitcase decorated with old hotel stamps on a wooden floor, travel aesthetic, no text",
    "An epic cyberpunk skyscraper towering into a rainy, neon-lit night sky, sci-fi concept art, no text",
    "A delicious chocolate layer cake with rich fudge frosting and chocolate shavings, food photography, no text",
    "A peaceful misty lake reflecting towering pine trees in the early morning light, serene nature art, no text",
    "A cute little koala bear clinging lazily to a eucalyptus tree trunk, wildlife photography, no text",
    "A classic brass telescope pointing toward a starry night sky from an old observatory tower, astronomy art, no text",
    "A vibrant street market in Marrakech filled with colorful woven rugs and lanterns, travel photography, no text",
    "A steaming ceramic bowl of creamy clam chowder with oyster crackers, comforting food art, no text",
    "A magical glowing portal opening up inside an ancient stone ruin, fantasy concept art, no text",
    "A sleek electric motorcycle parked outside a modern industrial coffee shop, urban aesthetic photography, no text",
    "A serene autumn park with golden leaves blanketing the walking paths and benches, landscape art, no text",
    "A cute baby penguin waddling across a sheet of white Antarctic ice, adorable wildlife photography, no text",
    "A vintage globe and brass compass resting on a wooden captain's desk, nautical aesthetic, no text",
    "A futuristic orbital space station orbiting high above a glowing blue planet, sci-fi art, no text",
    "A charming Italian seaside village with pastel-colored houses stacked along a cliff, travel art, no text",
    "A refreshing glass of iced lemonade with fresh mint leaves and lemon slices, summer photography, no text",
    "A majestic elk standing proudly in a snowy mountain forest at twilight, wildlife photography, no text",
    "A cozy stack of oversized knit sweaters in warm neutral tones, lifestyle photography, no text",
    "A whimsical flying turtle carrying a tiny medieval village on its shell, fantasy digital art, no text",
    "A classic vinyl record spinning on a turntable with visible sound waves, music aesthetic art, no text",
    "A vibrant coral reef filled with glowing anemones and schools of neon fish, underwater art, no text",
    "A rustic wooden beehive resting in a sunny meadow filled with wild clover, pastoral photography, no text",
    "A futuristic cyberpunk hacker working at a desk surrounded by multiple glowing monitors, sci-fi art, no text",
    "A delicious plate of homemade Italian pasta with tomato sauce and fresh basil, food photography, no text",
    "A peaceful Japanese zen garden with smooth mossy rocks and a trickling stone fountain, nature art, no text",
    "A cute little raccoon wearing a tiny bandit mask looking curiously at the camera, wildlife photography, no text",
    "An antique brass hourglass with white sand flowing slowly on a dark table, still life art, no text",
    "A magical floating island connected to the mainland by a glowing energy bridge, fantasy art, no text",
    "A sleek silver sports car driving through a misty mountain pass at dawn, automotive photography, no text",
    "A cozy reading corner with a steaming cup of tea, open book, and soft throw blanket, lifestyle art, no text",
    "A playful dolphin pod jumping through sparkling blue ocean waves under a bright sun, marine art, no text",
    "A collection of vintage apothecary glass bottles filled with colorful liquids, mystical still life, no text",
    "An epic fantasy dragon soaring over a burning medieval castle siege, cinematic digital art, no text",
    "A refreshing bowl of acai smoothie topped with fresh granola, coconut flakes, and fruit, food art, no text",
    "A serene winter landscape with a single wooden cabin glowing warmly in the snow, holiday art, no text",
    "A cute baby otter floating on its back and holding a shiny sea shell, adorable wildlife photography, no text",
    "A vintage typewriter with a typed letter reading adventures await, nostalgic retro art, no text",
    "A futuristic sci-fi corridor lined with glowing blue neon lights and metallic walls, concept art, no text",
    "A charming French bakery counter displaying an array of colorful croissants and tarts, food photography, no text",
    "A majestic waterfall cascading down a lush green jungle cliff into a blue pool, nature art, no text",
    "A cute little owl sitting on a pumpkin patch on a crisp autumn evening, seasonal illustration, no text",
    "A classic acoustic guitar resting against a vintage leather trunk in a sunlit room, musical art, no text",
    "A vibrant hot air balloon drifting over the dramatic rock formations of Cappadocia, travel photography, no text",
    "A warm bowl of creamy butternut squash soup garnished with roasted pumpkin seeds, food art, no text",
    "A magical glowing moon tree standing tall in an enchanted forest filled with fireflies, fantasy art, no text",
    "A sleek modern bullet train speeding past green agricultural fields in the countryside, photography, no text",
    "A peaceful rustic wooden porch with a rocking chair overlooking a vast green meadow, cozy art, no text",
    "A cute baby red panda balancing clumsily on a mossy green branch, adorable wildlife photography, no text",
    "A vintage brass telescope mounted on a tripod overlooking a stormy ocean horizon, nautical art, no text",
    "A futuristic cybernetic tiger prowling through a neon-drenched alleyway, sci-fi concept art, no text"
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
