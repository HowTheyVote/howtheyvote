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

            $classes = [];

            // Optionally support constrained modifiers using associative arrays
            foreach ($modifiers as $modifier => $constraint) {
                if (is_numeric($modifier)) {
                    $classes[] = $constraint;
                } elseif ($constraint) {
                    $classes[] = $modifier;
                }
            }

            $classes = array_filter($classes);
            $classes = array_map(fn ($class) => "{$base}--{$class}", $classes);

            return $this->class([$base, ...$classes]);
        };
    }
}
