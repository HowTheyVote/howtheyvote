<?php

expect()->extend('toSee', function (string $string) {
    return $this->value->assertSee($string);
});

expect()->extend('toSeeText', function (string $text) {
    return $this->value->assertSeeText($text);
});

expect()->extend('toSeeInOrder', function (array $strings) {
    return $this->value->assertSeeInOrder($strings);
});

expect()->extend('toSeeTextInOrder', function (array $texts) {
    return $this->value->assertSeeTextInOrder($texts);
});

expect()->extend('toHaveStatus', function (int $code) {
    return $this->value->assertStatus($code);
});

expect()->extend('toHaveSelector', function (string $selector, ?int $count = null) {
    return $this->value->assertSelector($selector, $count);
});

expect()->extend('toHaveSelectorWithText', function (string $selector, string $text, ?int $count = null) {
    return $this->value->assertSelectorText($selector, $text, $count);
});

expect()->extend('toHaveHeader', function (string $headerName, mixed $value = null) {
    return $this->value->assertHeader($headerName, $value);
});

expect()->extend('toRedirectTo', function (string $uri) {
    return $this->value->assertRedirect($uri);
});
