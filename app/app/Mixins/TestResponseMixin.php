<?php

namespace App\Mixins;

class TestResponseMixin extends AbstractRenderedMixin
{
    public function getRenderedHTML()
    {
        return function (): string {
            return $this->getContent();
        };
    }
}
