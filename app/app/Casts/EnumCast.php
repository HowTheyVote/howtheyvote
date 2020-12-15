<?php

namespace App\Casts;

use BadMethodCallException;
use Spatie\Enum\Laravel\Casts\EnumCast as BaseCast;

class EnumCast extends BaseCast
{
    public function get($model, string $key, $value, array $attributes)
    {
        try {
            return parent::get($model, $key, $value, $attributes);
        } catch (BadMethodCallException $exception) {
            // TODO: Spatie\Enum does strict type checks when initializing
            // a new enum. As SQLite (which is used in the test environment)
            // lacks support for integer types, try to cast to integer.
            // Remove once the following issues is solved:
            // https://github.com/spatie/laravel-enum/issues/57
            return parent::get($model, $key, intval($value), $attributes);
        }
    }
}
