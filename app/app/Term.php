<?php

namespace App;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Term extends Model
{
    use HasFactory;

    public $timestamps = false;

    protected $fillable = [
        'number',
    ];

    public function members()
    {
        return $this->belongsToMany(Member::class);
    }
}
