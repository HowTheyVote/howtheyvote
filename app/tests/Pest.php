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
