<?php

namespace App;

use Illuminate\Database\Eloquent\Casts\Attribute;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Str;

class Summary extends Model /*
 * A summary references one text or procedure that can be subject
 * to a vote in the plenary. This connection happens on the basis
 * of its reference.
 *
 * It is a textual summary of the subject matter at hand.
 * Summaries may not be available for some votes/subjects.
 */
{
    use HasFactory;

    protected $fillable = [
        'reference',
        'text',
        'oeil_id',
    ];

    public function excerpt(): Attribute
    {
        return new Attribute(
            get: function () {
                $text = str($this->text)
            ->explode("\n\n")
            // Remove the first paragraph as it almost always only contains
            // the title and the vote result, which is redundant information.
            ->splice(1)
            // Remove headings from excerpt
            ->filter(fn ($block) => ! Str::startsWith($block, '## '))
            ->join("\n\n");

                return Str::words($text, 50);
            }
        );
    }

    public function externalUrl(): Attribute
    {
        return new Attribute(
            get: function () {
                $baseUrl = 'https://oeil.secure.europarl.europa.eu/oeil/popups';

                return "{$baseUrl}/summary.do?id={$this->oeil_id}&t=e&l=en";
            }
        );
    }
}
