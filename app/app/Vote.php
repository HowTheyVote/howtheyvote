<?php

namespace App;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

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
}
