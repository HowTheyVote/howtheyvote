<?php

namespace App;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class GroupMembership extends Model
{
    use HasFactory;

    protected $fillable = [
        'member_id',
        'group_id',
        'term_id',
        'start_date',
        'end_date',
    ];

    public function member()
    {
        return $this->belongsTo(Member::class);
    }

    public function group()
    {
        return $this->belongsTo(Group::class);
    }

    public function term()
    {
        return $this->belongsTo(Term::class);
    }

    public function scopeActiveAt(Builder $query, \DateTime $date)
    {
        return $query
            ->where(function ($query) use ($date) {
                return $query
                    ->whereDate('start_date', '<=', $date)
                    ->whereDate('end_date', '>=', $date);
            })
            ->orWhere(function ($query) use ($date) {
                return $query
                    ->whereDate('start_date', '<=', $date)
                    ->whereNull('end_date');
            });
    }
}
