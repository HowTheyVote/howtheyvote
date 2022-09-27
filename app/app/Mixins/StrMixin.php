<?php

namespace App\Mixins;

class StrMixin
{
    public static function obfuscate()
    {
        return function (string $string): string {
            return str($string)
                ->split(1)
                ->map(fn ($char) => '&#x'.dechex(ord($char)).';')
                ->join('');
        };
    }
}
