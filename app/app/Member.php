<?php

namespace App;

use App\Enums\CountryEnum;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Str;

class Member extends Model
{
    use HasFactory;

    protected $fillable = [
        'web_id',
        'first_name',
        'last_name',
        'first_name_normalized',
        'last_name_normalized',
        'date_of_birth',
        'country',
    ];

    protected $dates = [
        'date_of_birth',
    ];

    protected $casts = [
        'country' => CountryEnum::class.':nullable',
    ];

    public function terms()
    {
        return $this->belongsToMany(Term::class);
    }

    public function groupMemberships()
    {
        return $this->hasMany(GroupMembership::class);
    }

    public function group()
    {
        return $this->belongsTo(Group::class);
    }

    public function votes()
    {
        return $this->belongsToMany(VotingList::class, 'votings')
            ->using(Voting::class)
            ->withPivot('position');
    }

    public static function normalizeName(string $name): string
    {
        $name = Str::lower($name);

        $replacements = [
            '-' => ' ',
            'ß' => 'ss',
        ];

        return strtr($name, $replacements);
    }

    public function setFirstNameAttribute($name)
    {
        $this->attributes['first_name'] = $name;

        return $this->first_name_normalized = static::normalizeName($name);
    }

    public function setLastNameAttribute($name)
    {
        $this->attributes['last_name'] = $name;

        return $this->last_name_normalized = static::normalizeName($name);
    }

    public function mergeTerms($newTerms): self
    {
        $this->terms()->syncWithoutDetaching($newTerms->pluck('id'));

        return $this;
    }

    public function scopeActiveAt(Builder $query, \DateTime $date, Term $term = null)
    {
        // While members are active members of parliament, they are
        // always a member of at least one group. Even independent members
        // are technically a member of the NI (non-incrits) group.
        return $query->whereHas('groupMemberships', function (Builder $query) use ($date, $term) {
            return $query->activeAt($date, $term);
        });
    }

    public function scopeWithGroupMembershipAt(Builder $query, \DateTime $date)
    {
        $groups = GroupMembership::activeAt($date);

        return $query->leftJoinSub($groups, 'group_memberships', function ($join) {
            $join->on('group_memberships.member_id', '=', 'members.id');
        });
    }
}
