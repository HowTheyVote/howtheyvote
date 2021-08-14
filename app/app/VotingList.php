<?php

namespace App;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Storage;
use Vinkla\Hashids\Facades\Hashids;

class VotingList extends Model
{
    use HasFactory;

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
        if (! $this->vote?->isPrimaryVote()) {
            return null;
        }

        $path = "share-pictures/vote-sharepic-{$this->id}.png";
        $disk = Storage::disk('public');

        if (! $disk->exists($path)) {
            return null;
        }

        return $disk->url($path);
    }
}
