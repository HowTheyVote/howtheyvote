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
        // Wrapping the where conditions in a closure logically groups
        // them using parentheses. It’s not strictly necessary in this
        // case, but makes the query a little more robust.
        // https://laravel.com/docs/8.x/queries#logical-grouping
        $query->where(function ($query) use ($date) {
            $query
                ->where(function ($query) use ($date) {
                    $query
                        ->whereDate('start_date', '<=', $date)
                        ->whereDate('end_date', '>=', $date);
                })
                ->orWhere(function ($query) use ($date) {
                    $query
                        ->whereDate('start_date', '<=', $date)
                        ->whereNull('end_date');
                });
        });

        return $query;
    }
}
