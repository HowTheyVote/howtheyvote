<?php

namespace App;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Group extends Model
/*
 * Represents a group in the European Parliament. Groups have names (like
 * "European People's Party") and abbreviations ("EPP"). Groups and Members
 * are connected through GroupMemberships.
 */
{
    use HasFactory;

    public $timestamps = false;

    protected $fillable = [
        'code',
    ];

    public function groupMemberships()
    {
        return $this->hasMany(GroupMembership::class);
    }
}
