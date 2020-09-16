<?php

namespace Database\Factories;

use App\Document;
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
            'date' => $this->faker->dateThisCentury(),
            'description' => '§ 1/2',
            'document_id' => Document::factory(),
        ];
    }
}
