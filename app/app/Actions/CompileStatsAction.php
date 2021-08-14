<?php

namespace App\Actions;

use App\Enums\VotePositionEnum;
use App\VotingList;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

class CompileStatsAction extends Action
{
    public function execute(VotingList $votingList): void
    {
        $active = $votingList->members()->count();
        $byPosition = $this->byPosition($votingList);

        $stats = [
            'voted' => $active - $byPosition['NOVOTE'],
            'active' => $active,
            'by_position' => $byPosition,
            'by_country' => $this->byCountry($votingList),
            'by_group' => $this->byGroup($votingList),
        ];

        $votingList->update(['stats' => $stats]);
    }

    protected function byCountry(VotingList $votingList): array
    {
        $this->log("Compiling country stats for vote {$votingList->id}");

        // We're using `getQuery` to get the underlying query builder
        // for the relation. For some reason, Eloquent always selects
        // the pivot columns for a relation query. This will however
        // cause an SQL syntax error, as they aren't included in the
        // group by statement.
        $active = $votingList->members()
            ->getQuery()
            ->select('country', DB::raw('count(*) as count'))
            ->groupBy('country')
            ->get()
            ->map(fn ($row) => [$row->country->value, $row->count])
            ->toAssoc();

        $byPosition = $votingList->members()
            ->getQuery()
            ->select('position', 'country', DB::raw('count(*) as count'))
            ->groupBy('country', 'position')
            ->get()
            ->groupBy(fn ($row) => $row->country->value)
            ->map(fn ($rows) => $this->formatPositions($rows));

        $voted = $byPosition->map(function ($counts, $country) use ($active) {
            return $active[$country] - $counts['NOVOTE'];
        });

        $stats = $this->mergeStats([
            'active' => $active,
            'voted' => $voted,
            'by_position' => $byPosition,
        ]);

        return $stats;
    }

    protected function byGroup(VotingList $votingList): array
    {
        $this->log("Compiling group stats for vote {$votingList->id}");

        // See comment in `byCountry` for an explanation why we're
        // using `getQuery`.
        $active = $votingList->members()
            ->getQuery()
            ->withGroupMembershipAt($votingList->date)
            ->select('group_id', DB::raw('count(*) as count'))
            ->groupBy('group_id')
            ->get()
            ->map(fn ($row) => [$row->group_id, $row->count])
            ->toAssoc();

        $byPosition = $votingList->members()
            ->getQuery()
            ->withGroupMembershipAt($votingList->date)
            ->select('position', 'group_id', DB::raw('count(*) as count'))
            ->groupBy('position', 'group_id')
            ->get()
            ->groupBy('group_id')
            ->map(fn ($rows) => $this->formatPositions($rows));

        $voted = $byPosition->map(function ($counts, $country) use ($active) {
            return $active[$country] - $counts['NOVOTE'];
        });

        return $this->mergeStats([
            'active' => $active,
            'by_position' => $byPosition,
            'voted' => $voted,
        ]);
    }

    protected function byPosition(VotingList $votingList): array
    {
        $this->log("Compiling general stats for vote {$votingList->id}");

        // See comment in `byCountry` for an explanation why we're
        // using `getQuery`.
        $rows = $votingList->members()
            ->getQuery()
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
            ->map(function ($row) {
                return [
                    VotePositionEnum::make($row->position)->label,
                    $row->count,
                ];
            })
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
