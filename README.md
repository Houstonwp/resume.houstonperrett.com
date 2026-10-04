# Houston Perrett's resume

Source for https://resume.houstonp.com/. Resume facts and accomplishments live in `data/content.toml`.

## Reproducible build

Use **Hugo extended 0.167.0** from the [official release](https://github.com/gohugoio/hugo/releases/tag/v0.167.0), plus Python 3.12 or newer for smoke checks:

```sh
git submodule update --init --recursive
hugo --gc --minify
python scripts/check_site.py
hugo server
```

The `simple-resume` submodule is the customized [Houstonwp fork](https://github.com/Houstonwp/simple-resume), pinned to `54a58603a474e5573f40ed747cc777d2055ed71e`. It keeps work experience before education, the custom date/location layout, and the fork's “Present” wording. Do not replace it with upstream without reviewing those differences. This cleanup does not change the fork itself.

The site-level `layouts` overrides provide charset, language, viewport, canonical URL, description, and responsive stylesheet loading. `assets/responsive.css` adjusts narrow screens and print without replacing the desktop design. The unused Source Sans Pro request is omitted; the original CSS font stack remains in effect.

Netlify reads `netlify.toml`; GitHub Actions checks the build without deploying. The CI installer verifies the Hugo archive checksum. `public/` and `resources/_gen/` are regenerated and ignored.

## Sass compatibility

The pinned theme uses LibSass. Hugo extended 0.167.0 still builds it, but warns that LibSass and the theme's `.Site.Data` usage are deprecated. The compiler is explicit in the site head override. Before a later Hugo upgrade removes support, migrate the customized theme to Dart Sass and test the resulting web and print CSS together. The pin is intentional; do not silently switch to standard Hugo or update the runtime without checks.

## Review and printing

Review the page at 320px, 390px, 768px, and desktop widths. Use the browser's print preview, disable browser headers/footers, and check US Letter and A4 output before sending a PDF. Printer/browser margins can affect pagination; there is no enforced one-page target.

The offline smoke check covers generated assets/internal links, document metadata, proofreading regressions, and section order. It does not verify current employment facts or remote font/icon availability. The legacy resume domain is not redirected here because its hosting/DNS ownership has not been verified.

## Browser checks

CI also installs the pinned Playwright test dependency from `requirements-test.txt`, checks 320/390/768/1280px layouts for horizontal overflow and broken images, and saves screenshots as the `site-previews` artifact. The resume check also produces Letter/A4 PDFs for human print review; generating a PDF alone is not a visual pagination approval. Run locally with:

```sh
python -m pip install -r requirements-test.txt
python -m playwright install chromium
python scripts/check_render.py
```
