<?php

namespace Database\Factories;

use App\Enums\VoteResultEnum;
use App\Enums\VoteTypeEnum;
use App\Vote;
use App\VoteCollection;
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
            'type' => VoteTypeEnum::PRIMARY(),
            'result' =>  VoteResultEnum::ADOPTED(),
            'formatted' => 'Proposition de résolution',
            'vote_collection_id' => VoteCollection::factory(),
            'final' => false,
        ];
    }
}
