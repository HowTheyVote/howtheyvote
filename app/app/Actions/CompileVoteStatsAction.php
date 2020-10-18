<?php

namespace App\Actions;

use App\Enums\VotePositionEnum;
use App\GroupMembership;
use App\Member;
use App\Vote;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

class CompileVoteStatsAction extends Action
{
    public function execute(Vote $vote): void
    {
        $voted = $vote->members()->count();
        $active = Member::activeAt($vote->date)->count();

        $stats = [
            'voted' => $vote->members()->count(),
            'active' => $active,
            'by_position' => $this->byPosition($vote),
            'by_country' => $this->byCountry($vote),
            'by_group' => $this->byGroup($vote),
        ];

        $vote->update(['stats' => $stats]);
    }

    protected function byCountry(Vote $vote): array
    {
        $this->log("Compiling country stats for vote {$vote->id}");

        $active = Member::activeAt($vote->date)
            ->select('country', DB::raw('count(*) as count'))
            ->groupBy('country')
            ->get()
            ->map(fn ($row) => [$row->country->label, $row->count])
            ->toAssoc();

        $byPosition = $vote->members()
            ->select('position', 'country', DB::raw('count(*) as count'))
            ->groupBy('country', 'position')
            ->get()
            ->groupBy(fn ($row) => $row->country->label)
            ->map(fn ($rows) => $this->formatPositions($rows));

        $voted = $byPosition->map(function ($counts) {
            return array_sum($counts->toArray());
        });

        $stats = $this->mergeStats([
            'active' => $active,
            'voted' => $voted,
            'by_position' => $byPosition,
        ]);

        return $stats;
    }

    protected function byGroup(Vote $vote): array
    {
        $this->log("Compiling group stats for vote {$vote->id}");

        $groups = GroupMembership::activeAt($vote->date);

        $active = Member::activeAt($vote->date)
            ->joinSub($groups, 'g', function ($join) {
                $join->on('g.member_id', '=', 'members.id');
            })
            ->select('group_id', DB::raw('count(*) as count'))
            ->groupBy('group_id')
            ->get()
            ->map(fn ($row) => [$row->group_id, $row->count])
            ->toAssoc();

        $byPosition = $vote->members()
            ->joinSub($groups, 'g', function ($join) {
                $join->on('g.member_id', '=', 'members.id');
            })
            ->select('position', 'group_id', DB::raw('count(*) as count'))
            ->groupBy('position', 'group_id')
            ->get()
            ->groupBy('group_id')
            ->map(fn ($rows) => $this->formatPositions($rows));

        $voted = $byPosition->map(function ($counts) {
            return array_sum($counts->toArray());
        });

        return $this->mergeStats([
            'active' => $active,
            'by_position' => $byPosition,
            'voted' => $voted,
        ]);
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
            ->map(fn ($row) => [$row->pivot->position->label, intval($row->count)])
            ->toAssoc();

        return $defaults->merge($positions);
    }

    protected function mergeStats(array $stats): array
    {
        $stats = collect($stats)->map(function ($stat, $key) {
            return $stat->map(fn ($item) => [$key => $item]);
        });

        return array_replace_recursive(...$stats->values()->toArray());
    }
}
