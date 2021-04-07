<?php

namespace App\Mixins;

use Illuminate\View\ComponentAttributeBag;

class ComponentAttributeBagMixin
{
    public function bem()
    {
        return function (string $base, ?string $modifiers = null): ComponentAttributeBag {
            if (! $modifiers) {
                return $this->class($base);
            }

            $modifiers = explode(' ', $modifiers);
            $classes = array_map(fn ($modifier) => "{$base}--{$modifier}", $modifiers);

            return $this->class([$base, ...$classes]);
        };
    }
}
