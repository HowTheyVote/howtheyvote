<?php

namespace App\Enums;

enum VoteResultEnum: int
{
    case ADOPTED = 0;
    case REJECTED = 1;

    public function label()
    {
        return match ($this) {
            self::ADOPTED => 'adopted',
            self::REJECTED => 'rejected'
        };
    }

    public static function make(string $result): static
    {
        return match ($result) {
            'ADOPTED' => static::ADOPTED,
            'REJECTED' => static::REJECTED,
        };
    }
}
