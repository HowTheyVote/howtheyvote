<?php

namespace App\Actions;

use App\Enums\VotePositionEnum;
use App\Vote;
use Illuminate\Support\Collection;
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

        $defaults = collect(VotePositionEnum::toArray())
            ->map(fn ($position) => [$position, 0])
            ->toAssoc();

        return $vote->members()
            ->select('position', 'country', DB::raw('count(*) as count'))
            ->groupBy('country', 'position')
            ->get()
            ->groupBy(fn ($row) => $row->country->label)
            ->map(fn ($rows) => $this->formatPositions($rows))
            ->toArray();
    }

    protected function byPosition(Vote $vote): array
    {
        $this->log("Compiling general stats for vote {$vote->id}");

        $rows = $vote->members()
            ->groupBy('position')
            ->select('position', DB::raw('count(*) as count'))
            ->get();

        return $this->formatPositions($rows)->toArray();
    }

    protected function formatPositions(Collection $rows): Collection
    {
        $defaults = collect(VotePositionEnum::toArray())
            ->map(fn ($position) => [$position, 0])
            ->toAssoc();

        $positions = $rows
            ->map(fn ($row) => [$row->pivot->position->label, $row->count])
            ->toAssoc();

        return $defaults->merge($positions);
    }
}
