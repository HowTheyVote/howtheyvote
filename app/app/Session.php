<?php

namespace App;

use App\Enums\LocationEnum;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Carbon;

class Session extends Model /*
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
        'notes',
        'id',
    ];

    protected $casts = [
        'location' => LocationEnum::class,
    ];

    protected $dates = [
        'start_date',
        'end_date',
    ];

    public static function next()
    {
        return static::query()
            ->where('start_date', '>', Carbon::now())
            ->orderBy('start_date')
            ->first();
    }

    public static function last()
    {
        return static::query()
            ->where('end_date', '<', Carbon::now())
            ->orderByDesc('start_date')
            ->first();
    }

    public static function current()
    {
        return static::query()
            ->where('start_date', '<=', Carbon::now())
            ->where('end_date', '>=', Carbon::now())
            ->first();
    }

    public function getDisplayTitleAttribute()
    {
        return __('session.title', [
            'date' => $this->start_date->format('F Y'),
            'location' => $this->location->label(),
        ]);
    }

    public function votes()
    {
        return $this->hasMany(Vote::class);
    }

    public function getAgendaUrlAttribute()
    {
        return "https://www.europarl.europa.eu/doceo/document/OJ-9-{$this->start_date->format('Y-m-d')}-SYN_EN.html";
    }
}
