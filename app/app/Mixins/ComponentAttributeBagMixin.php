<?php

namespace App\Mixins;

use Illuminate\View\ComponentAttributeBag;

class ComponentAttributeBagMixin
{
    public function bem()
    {
        return function (string $base, array | string | null $modifiers = null): ComponentAttributeBag {
            if (! $modifiers) {
                return $this->class($base);
            }

            if (is_string($modifiers)) {
                $modifiers = explode(' ', $modifiers);
            }

            $modifiers = array_filter($modifiers);
            $classes = array_map(fn ($modifier) => "{$base}--{$modifier}", $modifiers);

            return $this->class([$base, ...$classes]);
        };
    }
}
