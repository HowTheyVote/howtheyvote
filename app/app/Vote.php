<?php

namespace App;

use App\Enums\VoteTypeEnum;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Vinkla\Hashids\Facades\Hashids;

class Vote extends Model
{
    use HasFactory;

    protected $fillable = [
        'doceo_vote_id',
        'date',
        'description',
        'term_id',
        'stats',
        'type',
        'subvote_description',
    ];

    protected $dates = [
        'date',
    ];

    protected $casts = [
        'stats' => 'array',
        'type' => VoteTypeEnum::class,
    ];

    public function term()
    {
        return $this->belongsTo(Term::class);
    }

    public function members()
    {
        return $this->belongsToMany(Member::class)
            ->using(MemberVote::class)
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
