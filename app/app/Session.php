<?php

namespace App;

use App\Enums\LocationEnum;
use App\Enums\VoteTypeEnum;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Session extends Model
{
    use HasFactory;

    protected $fillable = [
        'start_date',
        'end_date',
        'location',
        'id',
    ];

    protected $casts = [
        'location' => LocationEnum::class,
    ];

    protected $dates = [
        'start_date',
        'end_date',
    ];

    public function getDisplayTitleAttribute()
    {
        return __('session.title', [
            'date' => $this->start_date->format('F Y'),
            'location' => $this->location->label,
        ]);
    }

    public function votes()
    {
        return $this->hasMany(Vote::class);
    }

    public function primaryVotes()
    {
        return $this->votes()->where('type', VoteTypeEnum::PRIMARY());
    }
}
