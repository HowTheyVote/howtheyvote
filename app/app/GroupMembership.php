<?php

namespace App;

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
}
