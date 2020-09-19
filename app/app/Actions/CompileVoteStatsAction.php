<?php

namespace App\Actions;

use App\Enums\VotePositionEnum;
use App\Vote;
use Illuminate\Support\Facades\DB;

class CompileVoteStatsAction extends Action
{
    public function execute(Vote $vote): void
    {
        $stats = [
            'voted' => $vote->members()->count(),
            'by_position' => $this->byPosition($vote),
            'by_country' => $this->byCountry($vote),
        ];

        $vote->update(['stats' => $stats]);
    }

    protected function byCountry(Vote $vote): array
    {
        $this->log("Compiling group stats for vote {$vote->id}");

        $defaults = collect(VotePositionEnum::getValues())
            ->map(fn ($position) => [$position, 0])
            ->toAssoc();

        return $vote->members()
            ->select('position', 'country', DB::raw('count(*) as count'))
            ->groupBy('country', 'position')
            ->get()
            ->groupBy('country')
            ->map(function ($group) use ($defaults) {
                $positions = $group
                    ->map(fn ($row) => [$row->position, $row->count])
                    ->toAssoc();

                return $defaults->merge($positions);
            })
            ->toArray();
    }

    protected function byPosition(Vote $vote): array
    {
        $this->log("Compiling general stats for vote {$vote->id}");

        $defaults = collect(VotePositionEnum::getValues())
            ->map(fn ($position) => [$position, 0])
            ->toAssoc();

        $positions = $vote->members()
            ->groupBy('position')
            ->select('position', DB::raw('count(*) as count'))
            ->get()
            ->map(fn ($row) => [$row->position, $row->count])
            ->toAssoc();

        return $defaults
            ->merge($positions)
            ->toArray();
    }
}
