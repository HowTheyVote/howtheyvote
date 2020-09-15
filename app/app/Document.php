<?php

namespace App;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Spatie\Enum\Laravel\HasEnums;

class Document extends Model
{
    use HasFactory;
    use HasEnums;

    public $timestamps = false;

    protected $fillable = [
        'type',
        'term_id',
        'number',
        'year',
        'title',
    ];

    protected $enums = [
        'type',
    ];

    public function term()
    {
        return $this->belongsTo(Term::class);
    }
}
