<?php

namespace Database\Factories;

use App\Document;
use App\Enums\VotePositionEnum;
use App\Member;
use App\Term;
use App\Vote;
use Illuminate\Database\Eloquent\Factories\Factory;

class VoteFactory extends Factory
{
    /**
     * The name of the factory's corresponding model.
     *
     * @var string
     */
    protected $model = Vote::class;

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
            'document_id' => Document::factory(),
            'term_id' => Term::factory(),
        ];
    }

    public function withFor(int $count = 1)
    {
        $position = VotePositionEnum::FOR();

        return $this->withPosition($position, $count);
    }

    public function withAgainst(int $count = 1)
    {
        $position = VotePositionEnum::AGAINST();

        return $this->withPosition($position, $count);
    }

    public function withAbstention(int $count = 1)
    {
        $position = VotePositionEnum::ABSTENTION();

        return $this->withPosition($position, $count);
    }

    public function withPosition(VotePositionEnum $position, int $count = 1)
    {
        return $this->afterCreating(function (Vote $vote) use ($position, $count) {
            $members = Member::factory()
                ->activeAt($vote->date)
                ->count($count)
                ->create()
                ->map(function ($member) use ($position) {
                    return [$member->id, [
                        'position' => $position,
                    ]];
                })
                ->toAssoc();

            $vote->members()->syncWithoutDetaching($members);
        });
    }
}
