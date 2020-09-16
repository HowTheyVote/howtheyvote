<?php

namespace App;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Carbon;

class Member extends Model
{
    use HasFactory;

    protected $fillable = [
        'web_id',
        'first_name',
        'last_name',
        'date_of_birth',
        'country_id',
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

    public function groupMemberships()
    {
        return $this->hasMany(GroupMembership::class);
    }

    public function votes()
    {
        return $this->belongsToMany(Vote::class)->withPivot('position');
    }

    public function mergeTerms($newTerms): self
    {
        $this->terms()->syncWithoutDetaching($newTerms->pluck('id'));

        return $this;
    }

    public function scopeActiveAt(Builder $query, Carbon $date)
    {
        // While members are active members of parliament, they are
        // always a member of at least one group. Even independent members
        // are technically a member of the NI (non-incrits) group.
        return $query->whereHas('groupMemberships', function (Builder $query) use ($date) {
            return $query->activeAt($date);
        });
    }
}
