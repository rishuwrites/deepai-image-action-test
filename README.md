# DeepAI browser generation test

This private test repository runs a manually triggered GitHub Actions workflow
that attempts to generate 20 images through DeepAI's public image-generator
page. It uses a normal headless Chromium browser and the page's visible prompt
and Generate controls; it does not use a DeepAI API key or bypass CAPTCHA,
sign-in gates, or rate limits.

Run **Generate 20 images** from the Actions tab. Results and a JSON manifest
are uploaded as the `deepai-generated-images` workflow artifact, including
partial results if the run is interrupted. The images are not committed to
this repository.

DeepAI may change its page, limit automated requests, or require additional
authorization. In that case the workflow stops and reports the failure rather
than trying to evade the restriction.
