<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Term extends Model
{
    public $timestamps = false;

    protected $fillable = [
        'number',
    ];

    public function members()
    {
        return $this->belongsToMany(Term::class);
    }
}
