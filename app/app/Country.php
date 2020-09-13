<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Country extends Model
{
    public $timestamps = false;

    protected $fillable = [
        'code',
    ];

    public function members()
    {
        return $this->hasMany(Member::class);
    }
}
