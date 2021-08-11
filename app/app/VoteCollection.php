<?php

namespace App;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class VoteCollection extends Model
{
    use HasFactory;

    protected $fillable = [
        'title',
        'reference',
        'date',
        'term_id',
    ];

    protected $dates = [
        'date',
    ];

    public function term()
    {
        return $this->belongsTo(Term::class);
    }

    public function votes()
    {
        return $this->hasMany(Vote::class);
    }

    public function summary()
    {
        return $this->belongsTo(Summary::class, 'reference', 'reference');
    }
}
