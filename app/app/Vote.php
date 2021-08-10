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
        'reference',
        'subheading',
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

    public function getDisplayTitleAttribute()
    {
        return $this->voteCollection->title;
    }

    public function getSubtitleAttribute()
    {
        if ($this->type->equals(VoteTypeEnum::AMENDMENT())) {
            return __('votes.subtitle.amendment', [
                'amendment' => $this->amendment,
                'author' => $this->author,
            ]);
        }

        if ($this->type->equals(VoteTypeEnum::SEPARATE())) {
            $subject = $this->split_part
                ? "{$this->subject}/{$this->split_part}"
                : $this->subject;

            return __('votes.subtitle.separate', ['subject' => $subject]);
        }

        if ($this->type->equals(VoteTypeEnum::PRIMARY())) {
            return __('votes.subtitle.primary');
        }
    }

    public function relatedVotes()
    {
        return Vote::where('vote_collection_id', $this->voteCollection->id)->where('id', '!=', $this->id);
    }

    public function primaryVote()
    {
        return $this->relatedVotes()->where('type', VoteTypeEnum::PRIMARY());
    }
}
