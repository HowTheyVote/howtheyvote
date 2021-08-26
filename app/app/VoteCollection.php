<?php

namespace App;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class VoteCollection extends Model
/*
 * Votes are based on the tables found in the VOT annexes of the
 * official plenary minutes. An example can be found under
 * https://www.europarl.europa.eu/RegData/seance_pleniere/
 * proces_verbal/2021/01-20/liste_presence/P9_PV(2021)01-20(VOT)_EN.pdf.
 * One table represents one VoteCollection whereas each row that contains
 * a roll-call-vote (RCV) represents one vote.
 *
 * One Vote per VoteCollection is *final*. We currently assume that this
 * is the last one in a collection/table. This is important, since a
 * VoteCollection groups Votes on the same subject, where most of these
 * are amendments etc. The final Vote represents the overall position of
 * the parliament to a text in its final version.
 */
{
    use HasFactory;

    protected $fillable = [
        'title',
        'reference',
        'date',
        'term_id',
    ];

    protected $dates = [
        'date',
    ];

    public function term()
    {
        return $this->belongsTo(Term::class);
    }

    public function votes()
    {
        return $this->hasMany(Vote::class);
    }

    public function summary()
    {
        return $this->belongsTo(Summary::class, 'reference', 'reference');
    }
}
