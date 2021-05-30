<?php

namespace App\Mixins;

class TestViewMixin extends AbstractRenderedMixin
{
    public function getRenderedHTML()
    {
        return function (): string {
            return $this->rendered;
        };
    }
}
