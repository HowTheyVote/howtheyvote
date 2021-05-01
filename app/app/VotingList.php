<?php

namespace App;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Vinkla\Hashids\Facades\Hashids;

class VotingList extends Model
{
    use HasFactory;

    protected $fillable = [
        'doceo_vote_id',
        'date',
        'description',
        'term_id',
        'stats',
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

    public function getDisplayTitleAttribute(): ?string
    {
        return $this->description;
    }

    public function getHashIdAttribute(): string
    {
        return Hashids::encode($this->id);
    }
}
