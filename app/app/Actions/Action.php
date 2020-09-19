<?php

namespace App\Actions;

use Illuminate\Support\Facades\Log;

abstract class Action
{
    protected function log(string $message, $context = []): void
    {
        $prefix = static::class;
        Log::info("{$prefix}: $message", $context);
    }
}
