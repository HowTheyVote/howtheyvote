<?php

namespace App;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Carbon;

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

    public function scopeActiveAt(Builder $query, Carbon $date)
    {
        return $query
            ->whereDate('start_date', '<=', $date)
            ->whereDate('end_date', '>=', $date);
    }
}
