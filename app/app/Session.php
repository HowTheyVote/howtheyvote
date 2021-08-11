<?php

namespace App;

use App\Enums\LocationEnum;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Session extends Model
{
    use HasFactory;

    protected $fillable = [
        'start_date',
        'end_date',
        'location',
    ];

    protected $casts = [
        'location' => LocationEnum::class,
    ];
}
