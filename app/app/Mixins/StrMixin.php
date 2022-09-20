<?php

namespace App\Mixins;

use Illuminate\Support\Str;

class StrMixin
{
    public static function obfuscate()
    {
        return function (string $string): string {
            return Str::of($string)
                ->split(1)
                ->map(fn ($char) => '&#x'.dechex(ord($char)).';')
                ->join('');
        };
    }
}
