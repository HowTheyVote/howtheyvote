<?php

namespace App;

use App\Enums\VoteResultEnum;
use App\Enums\VoteTypeEnum;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Laravel\Scout\Searchable;

class Vote extends Model
{
    use HasFactory;
    use Searchable;

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
        'session_id',
    ];

    protected $casts = [
        'result' => VoteResultEnum::class,
        'type' => VoteTypeEnum::class,
    ];

    public function shouldBeSearchable()
    {
        return $this->votingList && $this->isPrimaryVote();
    }

    public function makeAllSearchableUsing($query)
    {
        return $query->with([
            'voteCollection',
            'voteCollection.summary',
            'votingList',
        ]);
    }

    public function toSearchableArray()
    {
        return [
            'id' => $this->id,
            'display_title' => $this->display_title,
            'date' => $this->votingList->date,
            'result' => $this->result->label,
            'summary' => $this->voteCollection->summary?->text,
        ];
    }

    public function voteCollection()
    {
        return $this->belongsTo(VoteCollection::class);
    }

    public function session()
    {
        return $this->belongsTo(Session::class);
    }

    public function votingList()
    {
        return $this->hasOne(VotingList::class);
    }

    public function summary()
    {
        return $this->voteCollection->summary();
    }

    public function getDisplayTitleAttribute()
    {
        return $this->voteCollection->title;
    }

    public function getSubtitleAttribute()
    {
        if ($this->isAmendmentVote()) {
            return __('votes.subtitle.amendment', [
                'amendment' => $this->amendment,
                'author' => $this->author,
            ]);
        }

        if ($this->isSeparateVote()) {
            $subject = $this->split_part
                ? "{$this->subject}/{$this->split_part}"
                : $this->subject;

            return __('votes.subtitle.separate', ['subject' => $subject]);
        }

        if ($this->isPrimaryVote()) {
            return __('votes.subtitle.primary');
        }
    }

    public function relatedVotes()
    {
        return $this
            ->hasMany(self::class, 'vote_collection_id', 'vote_collection_id')
            ->where('id', '!=', $this->id);
    }

    public function primaryVote()
    {
        return $this
            ->hasOne(self::class, 'vote_collection_id', 'vote_collection_id')
            ->ofMany(['id' => 'max'], function ($query) {
                return $query->where('type', VoteTypeEnum::PRIMARY());
            });
    }

    public function isPrimaryVote()
    {
        return VoteTypeEnum::PRIMARY()->equals($this->type);
    }

    public function isSeparateVote()
    {
        return VoteTypeEnum::SEPARATE()->equals($this->type);
    }

    public function isAmendmentVote()
    {
        return VoteTypeEnum::AMENDMENT()->equals($this->type);
    }

    public function hasRelatedVotes()
    {
        return $this->relatedVotes()->exists();
    }
}
