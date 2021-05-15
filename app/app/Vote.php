<?php

namespace App;

use App\Enums\VoteResultEnum;
use App\Enums\VoteTypeEnum;
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
        'vote_collection_id',
        'formatted',
        'remarks',
    ];

    protected $casts = [
        'result' => VoteResultEnum::class,
        'type' => VoteTypeEnum::class,
    ];

    public function voteCollection()
    {
        return $this->belongsTo(VoteCollection::class);
    }

    public function votingList()
    {
        return $this->hasOne(VotingList::class);
    }
}
