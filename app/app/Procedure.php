<?php

namespace App;

use App\Enums\ProcedureTypeEnum;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Procedure extends Model
{
    use HasFactory;

    public $timestamps = false;

    protected $fillable = [
        'type', 'number', 'year', 'title',
    ];

    protected $casts = [
        'type' => ProcedureTypeEnum::class,
    ];
}
