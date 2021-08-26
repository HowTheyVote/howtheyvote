<?php

namespace App;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Term extends Model
/*
 * Elections to the European Parliament take place every five years.
 * The time-frame between two of these elections is called a plenary
 * term, i.e. a term represents the time the Parliament is constituted.
 * Terms are numbered since the inception of the European Parliament.
 */
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
