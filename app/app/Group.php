<?php

namespace App;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Group extends Model
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
