<?php

namespace Database\Factories;

use App\Enums\VotePositionEnum;
use App\Term;
use App\VotingList;
use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Carbon;

class VotingListFactory extends Factory
{
    /**
     * The name of the factory's corresponding model.
     *
     * @var string
     */
    protected $model = VotingList::class;

    /**
     * Define the model's default state.
     *
     * @return array
     */
    public function definition()
    {
        return [
            'doceo_vote_id' => $this->faker->numberBetween(0, 999999),
            'date' => $this->faker->dateTimeThisCentury(),
            'description' => '§ 1/2',
            'term_id' => Term::factory(),
        ];
    }

    public function withDate(Carbon $date)
    {
        return $this->state([
            'date' => $date,
        ]);
    }

    public function withMembers(string $position, MemberFactory $factory)
    {
        $position = VotePositionEnum::make($position);

        return $this->afterCreating(function (VotingList $votingList) use ($position, $factory) {
            $members = $factory
                ->create()
                ->map(function ($member) use ($position) {
                    return [$member->id, ['position' => $position]];
                })
                ->toAssoc();

            $votingList->members()->syncWithoutDetaching($members);
        });
    }

    public function withStats()
    {
        return $this->state([
            'stats' => [
                'voted' => 60,
                'active' => 100,
                'by_position' => [
                    'FOR' => 10,
                    'AGAINST' => 20,
                    'ABSTENTION' => 30,
                ],
            ],
        ]);
    }
}
