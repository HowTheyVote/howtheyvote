<?php

namespace App;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Member extends Model
{
    use HasFactory;

    protected $fillable = [
        'web_id',
        'first_name',
        'last_name',
        'date_of_birth',
    ];

    protected $dates = [
        'date_of_birth',
    ];

    public function country()
    {
        return $this->belongsTo(Country::class);
    }

    public function terms()
    {
        return $this->belongsToMany(Term::class);
    }

    public function mergeTerms($newTerms): self
    {
        $this->terms()->sync($newTerms->pluck('id'), false);

        return $this;
    }
}
