<?php

namespace App\Mixins;

use Illuminate\Support\Collection;

class CollectionMixin
{
    public static function toAssoc()
    {
        return function () : Collection {
            return $this->reduce(function ($assoc, $keyValuePair) {
                [$key, $value] = $keyValuePair;
                $assoc[$key] = $value;

                return $assoc;
            }, new static);
        };
    }
}
