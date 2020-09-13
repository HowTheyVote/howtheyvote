<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Member extends Model
{
    protected $fillable = [
        'web_id',
        'first_name',
        'last_name',
        'date_of_birth',
    ];

    protected $dates = [
        'date_of_birth',
    ];
}
