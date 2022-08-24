<?php

namespace App\Mixins;

use DOMDocument;
use DOMXPath;
use Illuminate\Support\Collection;
use Illuminate\Support\Str;
use Illuminate\Testing\Assert;
use Symfony\Component\CssSelector\CssSelectorConverter;

abstract class AbstractRenderedMixin
{
    abstract public function getRenderedHTML();

    public function select()
    {
        return function (string $selector): Collection {
            // TODO: Explain why we need to internalize/ignore errors
            libxml_use_internal_errors(true);

            $document = new DOMDocument();
            $document->loadHTML($this->getRenderedHTML());

            $converter = new CssSelectorConverter();
            $xPathSelector = $converter->toXPath($selector);

            $xPath = new DOMXPath($document);
            $elements = $xPath->query($xPathSelector);

            return collect($elements);
        };
    }

    public function assertSelector()
    {
        return function (string $selector, ?int $count = null): self {
            $elements = $this->select($selector);
            $actualCount = $elements->count();

            Assert::assertTrue(
                $elements->isNotEmpty(),
                "Did not find '{$selector}'."
            );

            if ($count !== null) {
                Assert::assertEquals(
                    $count,
                    $actualCount,
                    "Expected to find '{$selector}' ${count} times, but found only {$actualCount} matching elements."
                );
            }

            return $this;
        };
    }

    public function assertSelectorText()
    {
        return function (string $selector, string $text, ?int $count = null): self {
            // Replace multiple whitespace chars with a single space. In HTML, multiple
            // whitespace characters will usually be rendered as a single space.
            $normalizeText = fn (string $text) => preg_replace('/\s+/', ' ', $text);

            $elements = $this
                ->select($selector)
                ->filter(function ($element) use ($normalizeText, $text) {
                    return Str::contains(
                        $normalizeText($element->textContent),
                        $normalizeText($text),
                    );
                });

            $actualCount = $elements->count();

            Assert::assertTrue(
                $elements->isNotEmpty(),
                "Did not find '{$selector}' with text '{$text}'."
            );

            if ($count !== null) {
                Assert::assertEquals(
                    $count,
                    $actualCount,
                    "Expected to find '{$selector}' with text '{$text}' {$count} times, but found only {$actualCount} matching elements."
                );
            }

            return $this;
        };
    }
}
