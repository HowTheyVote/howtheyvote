<?php

namespace App;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Storage;
use Laravel\Scout\Searchable;
use Vinkla\Hashids\Facades\Hashids;

class VotingList extends Model
{
    use HasFactory;
    use Searchable;

    protected $fillable = [
        'doceo_vote_id',
        'date',
        'description',
        'reference',
        'term_id',
        'stats',
        'vote_id',
    ];

    protected $dates = [
        'date',
    ];

    protected $casts = [
        'stats' => 'array',
    ];

    public function shouldBeSearchable()
    {
        return $this->vote && $this->vote->isFinalVote();
    }

    public function makeAllSearchableUsing($query)
    {
        return $query->with([
            'vote',
            'vote.voteCollection',
            'vote.voteCollection.summary',
        ]);
    }

    public function toSearchableArray()
    {
        return [
            'id' => $this->id,
            'display_title' => $this->display_title,
            'date' => $this->date,
            'result' => $this->vote->result->label,
            'summary' => $this->vote->voteCollection->summary?->text,
        ];
    }

    public function term()
    {
        return $this->belongsTo(Term::class);
    }

    public function members()
    {
        return $this->belongsToMany(Member::class, 'votings')
            ->using(Voting::class)
            ->withPivot('position');
    }

    public function vote()
    {
        return $this->belongsTo(Vote::class);
    }

    public function getDisplayTitleAttribute(): string
    {
        return $this->vote?->display_title ?: $this->description;
    }

    public function getHashIdAttribute(): string
    {
        return Hashids::encode($this->id);
    }

    public function getFormattedDateAttribute(): string
    {
        return $this->date->isoFormat('dddd, MMMM D, YYYY');
    }

    public function getSharePictureUrlAttribute(): ?string
    {
        if (! $this->vote?->isFinalVote()) {
            return null;
        }

        $path = "share-pictures/vote-sharepic-{$this->id}.png";
        $disk = Storage::disk('public');

        if (! $disk->exists($path)) {
            return null;
        }

        return $disk->url($path);
    }

    public function getSharePictureDescriptionAttribute(): string
    {
        return __('voting-lists.share-picture.alt-text', [
           'title' => $this->display_title,
           'date' => $this->date->formatLocalized('%b%e, %Y'),
           'for' => $this->stats['by_position']['FOR'],
           'forpercent' => round(($this->stats['by_position']['FOR'] / $this->stats['voted'] * 100)),
           'against' => $this->stats['by_position']['AGAINST'],
           'againstpercent' => round(($this->stats['by_position']['AGAINST'] / $this->stats['voted'] * 100)),
           'abstention' => $this->stats['by_position']['ABSTENTION'],
           'abstentionpercent' => round(($this->stats['by_position']['ABSTENTION'] / $this->stats['voted'] * 100)),
           'voted' => $this->stats['voted'],
           'novote' => $this->stats['by_position']['NOVOTE'],
        ]);
    }

    public function getUrlAttribute(): ?string
    {
        return route('voting-list.show', ['votingList' => $this->id]);
    }
}
