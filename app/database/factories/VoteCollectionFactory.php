<?php

namespace Database\Factories;

use App\VoteCollection;
use Illuminate\Database\Eloquent\Factories\Factory;

class VoteCollectionFactory extends Factory
{
    /**
     * The name of the factory's corresponding model.
     *
     * @var string
     */
    protected $model = VoteCollection::class;

    /**
     * Define the model's default state.
     *
     * @return array
     */
    public function definition()
    {
        return [
            'title' => 'Children’s rights',
            'reference' => 'A9-1234/2021',
            'date' => $this->faker->dateTimeThisCentury(),
        ];
    }
}
