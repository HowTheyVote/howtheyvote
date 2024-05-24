import { strict as assert } from "node:assert";
// import { Request } from "node:http";
import { describe, it } from "node:test";
import { requestIsBot } from "./bots";

describe("requestIsBot", () => {
  it("detects common bot/crawler user agents", () => {
    const allow = [
      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
      "Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0",
    ];

    const block = [
      // Search engines
      "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/W.X.Y.Z Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
      "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/W.X.Y.Z Safari/537.36",
      "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",

      // CLI tools and libraries
      "curl/7.79.1",
      "python-requests/2.31.0",

      // Socials
      "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
      "Twitterbot/1.0",
      "http.rb/2.2.2 (Mastodon/1.5.1; +https://example-masto-instance.org/)",
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/600.2.5 (KHTML, like Gecko) Version/8.0.2 Safari/600.2.5 (Applebot/0.1)",

      // Misc
      "Mozilla/5.0 (compatible; heritrix/3.1.1-SNAPSHOT-20120116.200628 +http://www.archive.org/details/archive.org_bot)",
    ];

    for (const userAgent of allow) {
      assert.strictEqual(requestIsBot("/", userAgent), false);
    }

    for (const userAgent of block) {
      assert.strictEqual(requestIsBot("/", userAgent), true);
    }
  });

  it("detects common request path patterns", () => {
    const allow = ["/", "/votes/123456", "/123456", "/about", "/developers/"];

    const block = [
      "/wp-admin.php",
      "/wp-includes/css/buttons.css",
      "/wp-content/plugins/woopra/inc/php-ofc-library/ofc_upload_image.php",
      "/getConfig/getArticle.do",
      "/verification.asp",
      "/.env",
      "/app.env",
      "/.git",
      "/.git/HEAD",
      "/xmlrpc.php",
      "/admin/index.php",
    ];

    for (const path of allow) {
      assert.strictEqual(requestIsBot(path, ""), false);
    }

    for (const path of block) {
      assert.strictEqual(requestIsBot(path, ""), true);
    }
  });
});
