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
    ];

    public function term()
    {
        return $this->belongsTo(Term::class);
    }

    public function document()
    {
        return $this->belongsTo(Document::class);
    }
}
