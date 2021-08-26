<?php

namespace App;

use App\Enums\LocationEnum;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Session extends Model
/*
 * A Session represents a session week of parliament, i.e., subsequent
 * days at which plenary sessions in parliament took place. Roll call
 * votes (i.e., votes we are interested in) can only happen on those days.
 * During each Session, many votes can take place.
 *
 * Plenary sessions can take place in Brussels or Strasbourg.
 */
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
}
