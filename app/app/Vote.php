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
        'document_id',
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

    public function document()
    {
        return $this->belongsTo(Document::class);
    }

    public function members()
    {
        return $this->belongsToMany(Member::class)
            ->using(MemberVote::class)
            ->withPivot('position');
    }

    public function getDisplayTitleAttribute(): ?string
    {
        if ($procedureTitle = $this->document?->procedure?->title) {
            return $procedureTitle;
        }

        if ($documentTitle = $this->document?->title) {
            return $documentTitle;
        }

        return $this->description;
    }

    public function getHashIdAttribute(): string
    {
        return Hashids::encode($this->id);
    }
}
