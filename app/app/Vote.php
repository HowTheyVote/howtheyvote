<?php

namespace App;

use Enums\VoteResultEnum;
use Enums\VoteTypeEnum;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Vote extends Model
{
    use HasFactory;

    protected $fillable = [
        'author',
        'subject',
        'type',
        'amendment',
        'result',
        'split_part',
    ];

    protected $casts = [
        'result' => VoteResultEnum::class,
        'type' => VoteTypeEnum::class,
    ];

    public function voteCollection()
    {
        return $this->belongsTo(VoteCollection::class);
    }
}
