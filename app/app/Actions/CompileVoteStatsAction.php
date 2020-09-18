<?php

namespace App\Actions;

use App\Enums\VotePositionEnum;
use App\Member;
use App\Vote;
use Illuminate\Support\Facades\DB;

class CompileVoteStatsAction
{
    public function execute(Vote $vote): void
    {
        $stats = [
            'voted' => $this->voted($vote),
            'active' => $this->active($vote),
            'by_position' => $this->byPosition($vote),
        ];

        $vote->update(['stats' => $stats]);
    }

    protected function voted(Vote $vote): int
    {
        return $vote->members()->count();
    }

    protected function active(Vote $vote): int
    {
        return Member::activeAt($vote->date)->count();
    }

    protected function byPosition(Vote $vote): array
    {
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
