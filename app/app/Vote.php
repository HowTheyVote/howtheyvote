<?php

namespace App;

use App\Enums\VoteResultEnum;
use App\Enums\VoteTypeEnum;
use Illuminate\Database\Eloquent\Model;

class Vote extends Model
{
    protected $fillable = [
        'author',
        'subject',
        'type',
        'amendment',
        'result',
        'split_part',
        'vote_collection_id',
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
