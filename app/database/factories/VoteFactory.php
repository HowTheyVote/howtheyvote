<?php

namespace Database\Factories;

use App\Document;
use App\Enums\VotePositionEnum;
use App\Term;
use App\Vote;
use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Carbon;

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

    public function withDate(Carbon $date)
    {
        return $this->state([
            'date' => $date,
        ]);
    }

    public function withMembers(string $position, MemberFactory $factory)
    {
        $position = VotePositionEnum::make($position);

        return $this->afterCreating(function (Vote $vote) use ($position, $factory) {
            $members = $factory
                ->create()
                ->map(function ($member) use ($position) {
                    return [$member->id, ['position' => $position]];
                })
                ->toAssoc();

            $vote->members()->syncWithoutDetaching($members);
        });
    }
}
