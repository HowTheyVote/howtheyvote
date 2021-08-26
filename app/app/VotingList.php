<?php

namespace App;

use App\Enums\VoteResultEnum;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Storage;
use Laravel\Scout\Searchable;
use Vinkla\Hashids\Facades\Hashids;

class VotingList extends Model
/*
 * VotingLists hold a collection of Votings that MEPs casted during
 * one specific vote. VotingLists are based on the voting lists provided
 * by the parliament that list each MEP by name and how they voted in a
 * specific roll-call-vote. An example can be found under
 * https://www.europarl.europa.eu/RegData/seance_pleniere/proces_verbal/
 * 2021/01-20/liste_presence/P9_PV(2021)01-20(RCV)_XC.pdf.
 *
 * The headings of each voting list are stored in separate parts, e.g. list 1
 * of above example:
 * 1. A9-0248/2020 - Javier Zarzalejos - Proposition de résolution
 *     REFERENCE   |                   DESCRIPTION
 *
 * VotingLists should correspond to exactly one Vote. Allocating this is
 * the responsibility of the MatchVotesAndVotingListsAction.
 */
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
            'vote.session',
        ]);
    }

    public function toSearchableArray()
    {
        return [
            'id' => $this->id,
            'display_title' => $this->display_title,
            'date' => $this->date->timestamp,
            'result' => $this->vote->result->label,
            'summary' => $this->vote->voteCollection->summary?->text,
            'session_id' => $this->vote->session?->id,
            'session_display_title' => $this->vote->session?->display_title,
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

    public function scopeMatched($query)
    {
        return $query->whereHas('vote');
    }

    public function scopeFinal($query)
    {
        return $query->whereHas('vote', function ($query) {
            return $query->where('final', true);
        });
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

    public function getSharePictureDescriptionAttribute(): ?string
    {
        if (! $this->vote?->isFinalVote()) {
            return null;
        }

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

    public function getResultAttribute(): ?VoteResultEnum
    {
        return $this->vote?->result;
    }
}
