<?php

namespace App;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Str;

class Summary extends Model
{
    use HasFactory;

    protected $fillable = [
        'reference',
        'text',
    ];

    public function getExcerptAttribute(): string
    {
        $text = Str::of($this->text)
            ->explode("\n\n")
            // Remove the first paragraph as it almost always only contains
            // the title and the vote result, which is redundant information.
            ->splice(1)
            // Remove headings from excerpt
            ->filter(fn ($block) => ! Str::startsWith($block, '## '))
            ->join("\n\n");

        return Str::words($text, 50);
    }
}
